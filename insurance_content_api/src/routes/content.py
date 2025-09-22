from flask import Blueprint, request, jsonify
from src.models.insurance_models import db, ContentSchedule, SocialMediaPost, InsuranceType, ToneType, APIUsage
from src.routes.auth import require_auth, require_active_subscription
from src.services.ai_service import AIContentService
from datetime import datetime, timedelta
import os
import json

content_bp = Blueprint('content', __name__)

def get_week_dates(date_str=None):
    """Get start and end dates for a week"""
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = datetime.now().date()
    
    # Get Monday of the week
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end

@content_bp.route('/generate-schedule', methods=['POST'])
@require_auth
@require_active_subscription
def generate_schedule(agent):
    """Generate a weekly content schedule"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('insurance_types'):
            return jsonify({'error': 'Insurance types are required'}), 400
        
        if not data.get('tone'):
            return jsonify({'error': 'Tone is required'}), 400
        
        # Parse input data
        insurance_types = data['insurance_types']
        tone_str = data['tone']
        additional_prompt = data.get('additional_prompt', '')
        week_date = data.get('week_start_date')  # Optional, defaults to current week
        
        # Validate tone
        try:
            tone = ToneType(tone_str)
        except ValueError:
            return jsonify({'error': 'Invalid tone type'}), 400
        
        # Validate insurance types
        valid_types = [t.value for t in InsuranceType]
        for ins_type in insurance_types:
            if ins_type not in valid_types:
                return jsonify({'error': f'Invalid insurance type: {ins_type}'}), 400
        
        # Get week dates
        week_start, week_end = get_week_dates(week_date)
        
        # Check if schedule already exists for this week
        existing_schedule = ContentSchedule.query.filter_by(
            agent_id=agent.id,
            week_start_date=week_start
        ).first()
        
        if existing_schedule:
            return jsonify({
                'message': 'Schedule already exists for this week',
                'schedule': existing_schedule.to_dict()
            }), 200
        
        # Generate content using enhanced AI service
        ai_service = AIContentService()
        
        try:
            posts_data, tokens_used = ai_service.generate_weekly_content(
                insurance_types=insurance_types,
                tone=tone_str,
                additional_prompt=additional_prompt,
                week_start=week_start
            )
            
            # Track API usage
            api_usage = APIUsage(
                agent_id=agent.id,
                endpoint='generate_content',
                tokens_used=tokens_used,
                cost=tokens_used * 0.00003  # Approximate cost
            )
            db.session.add(api_usage)
            
        except Exception as e:
            return jsonify({'error': 'Failed to generate content', 'details': str(e)}), 500
        
        # Create content schedule
        schedule = ContentSchedule(
            agent_id=agent.id,
            week_start_date=week_start,
            week_end_date=week_end,
            generation_prompt=additional_prompt,
            tone=tone
        )
        schedule.set_insurance_types(insurance_types)
        
        db.session.add(schedule)
        db.session.flush()  # Get the schedule ID
        
        # Create individual posts
        for post_data in posts_data:
            # Parse post date from the enhanced data
            if 'post_date' in post_data:
                post_date = datetime.strptime(post_data['post_date'], '%Y-%m-%d').date()
            else:
                post_date = week_start + timedelta(days=post_data.get('day', 1) - 1)
            
            # Map insurance focus to enum
            insurance_focus = None
            if post_data.get('insurance_focus'):
                try:
                    insurance_focus = InsuranceType(post_data['insurance_focus'])
                except ValueError:
                    pass
            
            post = SocialMediaPost(
                schedule_id=schedule.id,
                post_date=post_date,
                post_text=post_data.get('post_text', ''),
                image_description=post_data.get('image_description', ''),
                insurance_type_focus=insurance_focus,
                content_theme=post_data.get('content_theme', 'general')
            )
            
            # Set hashtags
            if post_data.get('hashtags'):
                post.set_hashtags(post_data['hashtags'])
            
            db.session.add(post)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Content schedule generated successfully',
            'schedule': schedule.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to generate schedule', 'details': str(e)}), 500

@content_bp.route('/schedules', methods=['GET'])
@require_auth
def get_schedules(agent):
    """Get all content schedules for the agent"""
    try:
        schedules = ContentSchedule.query.filter_by(agent_id=agent.id).order_by(ContentSchedule.week_start_date.desc()).all()
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get schedules', 'details': str(e)}), 500

@content_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
@require_auth
def get_schedule(agent, schedule_id):
    """Get a specific content schedule"""
    try:
        schedule = ContentSchedule.query.filter_by(id=schedule_id, agent_id=agent.id).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        return jsonify({
            'schedule': schedule.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get schedule', 'details': str(e)}), 500

@content_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@require_auth
def delete_schedule(agent, schedule_id):
    """Delete a content schedule"""
    try:
        schedule = ContentSchedule.query.filter_by(id=schedule_id, agent_id=agent.id).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({'message': 'Schedule deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete schedule', 'details': str(e)}), 500

@content_bp.route('/current-week', methods=['GET'])
@require_auth
def get_current_week_schedule(agent):
    """Get the current week's content schedule"""
    try:
        week_start, week_end = get_week_dates()
        
        schedule = ContentSchedule.query.filter_by(
            agent_id=agent.id,
            week_start_date=week_start
        ).first()
        
        if not schedule:
            return jsonify({
                'message': 'No schedule found for current week',
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat()
            }), 404
        
        return jsonify({
            'schedule': schedule.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get current week schedule', 'details': str(e)}), 500

@content_bp.route('/insurance-types', methods=['GET'])
def get_insurance_types():
    """Get available insurance types"""
    types = [{'value': t.value, 'label': t.value.replace('_', ' ').title()} for t in InsuranceType]
    return jsonify({'insurance_types': types}), 200

@content_bp.route('/tones', methods=['GET'])
def get_tones():
    """Get available tone types"""
    tones = [{'value': t.value, 'label': t.value.replace('_', ' ').title()} for t in ToneType]
    return jsonify({'tones': tones}), 200
