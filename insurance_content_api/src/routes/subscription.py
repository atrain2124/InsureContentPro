from flask import Blueprint, request, jsonify
from src.models.insurance_models import db, Agent, SubscriptionStatus
from src.routes.auth import require_auth
import stripe
import os
from datetime import datetime, timedelta
import logging

subscription_bp = Blueprint('subscription', __name__)

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_placeholder')

# Subscription pricing (in cents)
MONTHLY_PRICE = 2997  # $29.97/month
ANNUAL_PRICE = 29997  # $299.97/year (save $60)

@subscription_bp.route('/create-checkout-session', methods=['POST'])
@require_auth
def create_checkout_session(agent):
    """Create a Stripe checkout session for subscription"""
    try:
        data = request.get_json()
        plan_type = data.get('plan_type', 'monthly')  # monthly or annual
        
        # Determine price based on plan type
        if plan_type == 'annual':
            price_amount = ANNUAL_PRICE
            interval = 'year'
            interval_count = 1
        else:
            price_amount = MONTHLY_PRICE
            interval = 'month'
            interval_count = 1
        
        # Create or retrieve Stripe customer
        stripe_customer = None
        if agent.stripe_customer_id:
            try:
                stripe_customer = stripe.Customer.retrieve(agent.stripe_customer_id)
            except stripe.error.InvalidRequestError:
                # Customer doesn't exist, create new one
                stripe_customer = None
        
        if not stripe_customer:
            stripe_customer = stripe.Customer.create(
                email=agent.email,
                name=f"{agent.first_name} {agent.last_name}",
                metadata={
                    'agent_id': agent.id,
                    'trial_end_date': agent.trial_end_date.isoformat() if agent.trial_end_date else None
                }
            )
            agent.stripe_customer_id = stripe_customer.id
            db.session.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'InsureContent Pro - {plan_type.title()} Plan',
                        'description': 'AI-powered social media content generation for insurance agents',
                    },
                    'unit_amount': price_amount,
                    'recurring': {
                        'interval': interval,
                        'interval_count': interval_count,
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'subscription/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'subscription/cancel',
            metadata={
                'agent_id': agent.id,
                'plan_type': plan_type
            },
            subscription_data={
                'metadata': {
                    'agent_id': agent.id,
                    'plan_type': plan_type
                }
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': 'Failed to create checkout session'}), 500

@subscription_bp.route('/success', methods=['GET'])
def subscription_success():
    """Handle successful subscription"""
    session_id = request.args.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'No session ID provided'}), 400
    
    try:
        # Retrieve the checkout session
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Get the agent
            agent_id = session.metadata.get('agent_id')
            agent = Agent.query.get(agent_id)
            
            if agent:
                # Update agent subscription status
                agent.subscription_status = SubscriptionStatus.ACTIVE
                agent.stripe_subscription_id = session.subscription
                agent.subscription_start_date = datetime.utcnow()
                
                # Set subscription end date based on plan type
                plan_type = session.metadata.get('plan_type', 'monthly')
                if plan_type == 'annual':
                    agent.subscription_end_date = datetime.utcnow() + timedelta(days=365)
                else:
                    agent.subscription_end_date = datetime.utcnow() + timedelta(days=30)
                
                db.session.commit()
                
                return jsonify({
                    'message': 'Subscription activated successfully',
                    'plan_type': plan_type,
                    'status': 'active'
                }), 200
        
        return jsonify({'error': 'Payment not completed'}), 400
        
    except Exception as e:
        logging.error(f"Error processing subscription success: {str(e)}")
        return jsonify({'error': 'Failed to process subscription'}), 500

@subscription_bp.route('/cancel', methods=['GET'])
def subscription_cancel():
    """Handle cancelled subscription checkout"""
    return jsonify({
        'message': 'Subscription checkout was cancelled',
        'status': 'cancelled'
    }), 200

@subscription_bp.route('/portal', methods=['POST'])
@require_auth
def create_portal_session(agent):
    """Create a Stripe customer portal session"""
    try:
        if not agent.stripe_customer_id:
            return jsonify({'error': 'No Stripe customer found'}), 404
        
        portal_session = stripe.billing_portal.Session.create(
            customer=agent.stripe_customer_id,
            return_url=request.host_url + 'dashboard'
        )
        
        return jsonify({
            'portal_url': portal_session.url
        }), 200
        
    except Exception as e:
        logging.error(f"Error creating portal session: {str(e)}")
        return jsonify({'error': 'Failed to create portal session'}), 500

@subscription_bp.route('/status', methods=['GET'])
@require_auth
def get_subscription_status(agent):
    """Get current subscription status"""
    try:
        subscription_info = {
            'status': agent.subscription_status.value,
            'trial_end_date': agent.trial_end_date.isoformat() if agent.trial_end_date else None,
            'subscription_start_date': agent.subscription_start_date.isoformat() if agent.subscription_start_date else None,
            'subscription_end_date': agent.subscription_end_date.isoformat() if agent.subscription_end_date else None,
            'stripe_subscription_id': agent.stripe_subscription_id,
            'can_generate_content': agent.can_generate_content()
        }
        
        # If there's an active Stripe subscription, get additional details
        if agent.stripe_subscription_id:
            try:
                stripe_subscription = stripe.Subscription.retrieve(agent.stripe_subscription_id)
                subscription_info.update({
                    'stripe_status': stripe_subscription.status,
                    'current_period_end': datetime.fromtimestamp(stripe_subscription.current_period_end).isoformat(),
                    'cancel_at_period_end': stripe_subscription.cancel_at_period_end,
                    'plan_amount': stripe_subscription.items.data[0].price.unit_amount,
                    'plan_interval': stripe_subscription.items.data[0].price.recurring.interval
                })
            except stripe.error.InvalidRequestError:
                # Subscription doesn't exist in Stripe
                pass
        
        return jsonify(subscription_info), 200
        
    except Exception as e:
        logging.error(f"Error getting subscription status: {str(e)}")
        return jsonify({'error': 'Failed to get subscription status'}), 500

@subscription_bp.route('/cancel-subscription', methods=['POST'])
@require_auth
def cancel_subscription(agent):
    """Cancel the current subscription"""
    try:
        if not agent.stripe_subscription_id:
            return jsonify({'error': 'No active subscription found'}), 404
        
        # Cancel the subscription at period end
        stripe.Subscription.modify(
            agent.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        return jsonify({
            'message': 'Subscription will be cancelled at the end of the current period',
            'status': 'cancelled_at_period_end'
        }), 200
        
    except Exception as e:
        logging.error(f"Error cancelling subscription: {str(e)}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500

@subscription_bp.route('/reactivate-subscription', methods=['POST'])
@require_auth
def reactivate_subscription(agent):
    """Reactivate a cancelled subscription"""
    try:
        if not agent.stripe_subscription_id:
            return jsonify({'error': 'No subscription found'}), 404
        
        # Reactivate the subscription
        stripe.Subscription.modify(
            agent.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        return jsonify({
            'message': 'Subscription reactivated successfully',
            'status': 'active'
        }), 200
        
    except Exception as e:
        logging.error(f"Error reactivating subscription: {str(e)}")
        return jsonify({'error': 'Failed to reactivate subscription'}), 500

@subscription_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return jsonify({'status': 'success'}), 200

def handle_subscription_updated(subscription):
    """Handle subscription update webhook"""
    try:
        agent_id = subscription['metadata'].get('agent_id')
        if agent_id:
            agent = Agent.query.get(agent_id)
            if agent:
                # Update subscription status based on Stripe status
                if subscription['status'] == 'active':
                    agent.subscription_status = SubscriptionStatus.ACTIVE
                elif subscription['status'] == 'canceled':
                    agent.subscription_status = SubscriptionStatus.CANCELLED
                elif subscription['status'] in ['past_due', 'unpaid']:
                    agent.subscription_status = SubscriptionStatus.EXPIRED
                
                # Update subscription end date
                agent.subscription_end_date = datetime.fromtimestamp(subscription['current_period_end'])
                
                db.session.commit()
                
    except Exception as e:
        logging.error(f"Error handling subscription update: {str(e)}")

def handle_subscription_deleted(subscription):
    """Handle subscription deletion webhook"""
    try:
        agent_id = subscription['metadata'].get('agent_id')
        if agent_id:
            agent = Agent.query.get(agent_id)
            if agent:
                agent.subscription_status = SubscriptionStatus.CANCELLED
                agent.subscription_end_date = datetime.utcnow()
                db.session.commit()
                
    except Exception as e:
        logging.error(f"Error handling subscription deletion: {str(e)}")

def handle_payment_succeeded(invoice):
    """Handle successful payment webhook"""
    try:
        subscription_id = invoice['subscription']
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            agent_id = subscription['metadata'].get('agent_id')
            
            if agent_id:
                agent = Agent.query.get(agent_id)
                if agent:
                    agent.subscription_status = SubscriptionStatus.ACTIVE
                    agent.subscription_end_date = datetime.fromtimestamp(subscription['current_period_end'])
                    db.session.commit()
                    
    except Exception as e:
        logging.error(f"Error handling payment success: {str(e)}")

def handle_payment_failed(invoice):
    """Handle failed payment webhook"""
    try:
        subscription_id = invoice['subscription']
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            agent_id = subscription['metadata'].get('agent_id')
            
            if agent_id:
                agent = Agent.query.get(agent_id)
                if agent:
                    # Mark as expired if payment fails
                    agent.subscription_status = SubscriptionStatus.EXPIRED
                    db.session.commit()
                    
    except Exception as e:
        logging.error(f"Error handling payment failure: {str(e)}")

@subscription_bp.route('/pricing', methods=['GET'])
def get_pricing():
    """Get pricing information"""
    return jsonify({
        'plans': [
            {
                'name': 'Monthly Plan',
                'price': MONTHLY_PRICE,
                'price_display': '$29.97',
                'interval': 'month',
                'features': [
                    'Unlimited weekly content generation',
                    'AI-powered image creation',
                    'Multiple insurance types',
                    'Various tone options',
                    'Copy & share functionality',
                    'Email support'
                ]
            },
            {
                'name': 'Annual Plan',
                'price': ANNUAL_PRICE,
                'price_display': '$299.97',
                'interval': 'year',
                'savings': '$60',
                'features': [
                    'Everything in Monthly Plan',
                    'Save $60 per year',
                    'Priority support',
                    'Early access to new features'
                ]
            }
        ],
        'trial': {
            'duration': 7,
            'description': '7-day free trial with full access to all features'
        }
    }), 200
