import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { 
  CreditCard, 
  Calendar, 
  CheckCircle, 
  XCircle, 
  ExternalLink,
  Crown,
  Zap,
  Shield,
  Star
} from 'lucide-react';
import { format, differenceInDays } from 'date-fns';
import axios from 'axios';

const SubscriptionManager = ({ onBack }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [pricing, setPricing] = useState(null);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      setLoading(true);
      const [statusResponse, pricingResponse] = await Promise.all([
        axios.get('/api/subscription/status'),
        axios.get('/api/subscription/pricing')
      ]);
      
      setSubscriptionStatus(statusResponse.data);
      setPricing(pricingResponse.data);
    } catch (error) {
      setError('Failed to load subscription information');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planType) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.post('/api/subscription/create-checkout-session', {
        plan_type: planType
      });
      
      // Redirect to Stripe checkout
      window.location.href = response.data.checkout_url;
      
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to create checkout session');
      setLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    try {
      setLoading(true);
      const response = await axios.post('/api/subscription/portal');
      window.open(response.data.portal_url, '_blank');
    } catch (error) {
      setError('Failed to open subscription portal');
    } finally {
      setLoading(false);
    }
  };

  const getTrialDaysRemaining = () => {
    if (subscriptionStatus?.trial_end_date) {
      const trialEnd = new Date(subscriptionStatus.trial_end_date);
      const today = new Date();
      return Math.max(0, differenceInDays(trialEnd, today));
    }
    return 0;
  };

  const getStatusBadge = () => {
    const status = subscriptionStatus?.status;
    const trialDays = getTrialDaysRemaining();
    
    if (status === 'trial') {
      return (
        <Badge variant={trialDays > 3 ? "default" : "destructive"} className="text-sm">
          <Calendar className="h-3 w-3 mr-1" />
          Trial - {trialDays} days left
        </Badge>
      );
    } else if (status === 'active') {
      return (
        <Badge variant="default" className="bg-green-600 text-sm">
          <CheckCircle className="h-3 w-3 mr-1" />
          Active Subscription
        </Badge>
      );
    } else {
      return (
        <Badge variant="destructive" className="text-sm">
          <XCircle className="h-3 w-3 mr-1" />
          Subscription Expired
        </Badge>
      );
    }
  };

  const PricingCard = ({ plan, isPopular = false }) => (
    <Card className={`relative ${isPopular ? 'border-blue-500 shadow-lg' : ''}`}>
      {isPopular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <Badge className="bg-blue-600 text-white px-3 py-1">
            <Star className="h-3 w-3 mr-1" />
            Most Popular
          </Badge>
        </div>
      )}
      
      <CardHeader className="text-center">
        <CardTitle className="text-xl">{plan.name}</CardTitle>
        <div className="text-3xl font-bold text-blue-600">
          {plan.price_display}
          <span className="text-sm text-gray-600 font-normal">
            /{plan.interval}
          </span>
        </div>
        {plan.savings && (
          <div className="text-green-600 font-medium">
            Save {plan.savings}
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        <ul className="space-y-3 mb-6">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-center text-sm">
              <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
              {feature}
            </li>
          ))}
        </ul>
        
        <Button 
          className="w-full" 
          onClick={() => handleSubscribe(plan.interval === 'year' ? 'annual' : 'monthly')}
          disabled={loading}
          variant={isPopular ? "default" : "outline"}
        >
          {loading ? 'Processing...' : `Choose ${plan.name}`}
        </Button>
      </CardContent>
    </Card>
  );

  if (loading && !subscriptionStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={onBack}>
                ← Back to Dashboard
              </Button>
              <div className="flex items-center space-x-2">
                <CreditCard className="h-6 w-6 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">Subscription Management</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {getStatusBadge()}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Current Subscription Status */}
        {subscriptionStatus && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Current Subscription</CardTitle>
              <CardDescription>
                Your current plan and billing information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Status</h4>
                  {getStatusBadge()}
                </div>
                
                {subscriptionStatus.status === 'trial' && (
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Trial Ends</h4>
                    <p className="text-gray-600">
                      {subscriptionStatus.trial_end_date 
                        ? format(new Date(subscriptionStatus.trial_end_date), 'MMM d, yyyy')
                        : 'N/A'
                      }
                    </p>
                  </div>
                )}
                
                {subscriptionStatus.status === 'active' && (
                  <>
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Next Billing</h4>
                      <p className="text-gray-600">
                        {subscriptionStatus.current_period_end 
                          ? format(new Date(subscriptionStatus.current_period_end), 'MMM d, yyyy')
                          : 'N/A'
                        }
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Plan</h4>
                      <p className="text-gray-600 capitalize">
                        ${(subscriptionStatus.plan_amount / 100).toFixed(2)} / {subscriptionStatus.plan_interval}
                      </p>
                    </div>
                  </>
                )}
              </div>
              
              {subscriptionStatus.status === 'active' && (
                <div className="mt-6 pt-4 border-t">
                  <Button 
                    variant="outline" 
                    onClick={handleManageSubscription}
                    disabled={loading}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Manage Subscription
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Pricing Plans */}
        {pricing && subscriptionStatus?.status !== 'active' && (
          <div>
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Choose Your Plan
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Upgrade to continue generating professional social media content for your insurance business.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {pricing.plans.map((plan, index) => (
                <PricingCard 
                  key={plan.name} 
                  plan={plan} 
                  isPopular={index === 1} // Make annual plan popular
                />
              ))}
            </div>

            {/* Features Highlight */}
            <div className="mt-12">
              <Card>
                <CardHeader className="text-center">
                  <CardTitle className="flex items-center justify-center space-x-2">
                    <Crown className="h-6 w-6 text-yellow-500" />
                    <span>Why Choose InsureContent Pro?</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <Zap className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                      <h4 className="font-semibold mb-2">AI-Powered Content</h4>
                      <p className="text-sm text-gray-600">
                        Generate professional, compliant content in minutes, not hours
                      </p>
                    </div>
                    
                    <div className="text-center">
                      <Shield className="h-8 w-8 text-green-600 mx-auto mb-3" />
                      <h4 className="font-semibold mb-2">Insurance Compliant</h4>
                      <p className="text-sm text-gray-600">
                        Built-in compliance ensures your content meets industry regulations
                      </p>
                    </div>
                    
                    <div className="text-center">
                      <CheckCircle className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                      <h4 className="font-semibold mb-2">Proven Results</h4>
                      <p className="text-sm text-gray-600">
                        Join thousands of agents growing their warm market reach
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Money Back Guarantee */}
            <div className="mt-8 text-center">
              <Card className="bg-green-50 border-green-200">
                <CardContent className="pt-6">
                  <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-green-800 mb-2">
                    30-Day Money Back Guarantee
                  </h3>
                  <p className="text-green-700">
                    Not satisfied? Get a full refund within 30 days, no questions asked.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default SubscriptionManager;
