import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { contentAPI } from '../lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Calendar, Clock, User, Sparkles, TrendingUp, FileText, Image } from 'lucide-react';
import { format, differenceInDays } from 'date-fns';
import ContentGenerator from './ContentGenerator';
import ScheduleView from './ScheduleView';
import SubscriptionManager from './SubscriptionManager';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [currentSchedule, setCurrentSchedule] = useState(null);
  const [recentSchedules, setRecentSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showGenerator, setShowGenerator] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [showSubscription, setShowSubscription] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load current week schedule
      try {
        const currentWeekResponse = await contentAPI.getCurrentWeekSchedule();
        setCurrentSchedule(currentWeekResponse.data.schedule);
      } catch (error) {
        if (error.response?.status !== 404) {
          console.error('Error loading current week schedule:', error);
        }
      }

      // Load recent schedules
      const schedulesResponse = await contentAPI.getSchedules();
      setRecentSchedules(schedulesResponse.data.schedules.slice(0, 5));
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleGenerated = (newSchedule) => {
    setCurrentSchedule(newSchedule);
    setShowGenerator(false);
    loadDashboardData(); // Refresh the data
  };

  const getTrialDaysRemaining = () => {
    if (user?.subscription_status === 'trial' && user?.trial_end_date) {
      const trialEnd = new Date(user.trial_end_date);
      const today = new Date();
      return Math.max(0, differenceInDays(trialEnd, today));
    }
    return 0;
  };

  const getSubscriptionBadge = () => {
    const status = user?.subscription_status;
    const trialDays = getTrialDaysRemaining();
    
    if (status === 'trial') {
      return (
        <Badge 
          variant={trialDays > 3 ? "default" : "destructive"}
          className="cursor-pointer hover:opacity-80"
          onClick={() => setShowSubscription(true)}
        >
          Trial - {trialDays} days left
        </Badge>
      );
    } else if (status === 'active') {
      return (
        <Badge 
          variant="default" 
          className="bg-green-600 cursor-pointer hover:opacity-80"
          onClick={() => setShowSubscription(true)}
        >
          Active Subscription
        </Badge>
      );
    } else {
      return (
        <Badge 
          variant="destructive"
          className="cursor-pointer hover:opacity-80"
          onClick={() => setShowSubscription(true)}
        >
          Subscription Expired
        </Badge>
      );
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (showGenerator) {
    return (
      <ContentGenerator 
        onScheduleGenerated={handleScheduleGenerated}
        onCancel={() => setShowGenerator(false)}
      />
    );
  }

  if (selectedSchedule) {
    return (
      <ScheduleView 
        schedule={selectedSchedule}
        onBack={() => setSelectedSchedule(null)}
        onRefresh={loadDashboardData}
      />
    );
  }

  if (showSubscription) {
    return (
      <SubscriptionManager 
        onBack={() => setShowSubscription(false)}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">InsureContent Pro</h1>
              </div>
              {getSubscriptionBadge()}
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <User className="h-4 w-4" />
                <span>{user?.first_name} {user?.last_name}</span>
              </div>
              <Button variant="outline" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.first_name}!
          </h2>
          <p className="text-gray-600">
            Generate engaging social media content for your insurance business with AI-powered tools.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">This Week's Content</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {currentSchedule ? currentSchedule.posts.length : 0}
              </div>
              <p className="text-xs text-muted-foreground">
                {currentSchedule ? 'Posts ready to share' : 'No content generated yet'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Schedules</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{recentSchedules.length}</div>
              <p className="text-xs text-muted-foreground">
                Content schedules created
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Account Status</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {user?.subscription_status === 'trial' ? getTrialDaysRemaining() : '∞'}
              </div>
              <p className="text-xs text-muted-foreground">
                {user?.subscription_status === 'trial' ? 'Trial days remaining' : 'Active subscription'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Current Week Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="h-5 w-5" />
                <span>This Week's Content</span>
              </CardTitle>
              <CardDescription>
                Your social media content for the current week
              </CardDescription>
            </CardHeader>
            <CardContent>
              {currentSchedule ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">
                        Week of {format(new Date(currentSchedule.week_start_date), 'MMM d, yyyy')}
                      </p>
                      <p className="text-sm text-gray-600">
                        {currentSchedule.posts.length} posts • {currentSchedule.tone} tone
                      </p>
                    </div>
                    <Button 
                      onClick={() => setSelectedSchedule(currentSchedule)}
                      variant="outline"
                    >
                      View Details
                    </Button>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-2">
                    {currentSchedule.posts.slice(0, 3).map((post, index) => (
                      <div key={post.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">
                            {format(new Date(post.post_date), 'EEEE, MMM d')}
                          </span>
                          {post.image_url && (
                            <Badge variant="secondary" className="text-xs">
                              <Image className="h-3 w-3 mr-1" />
                              Image
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-700 line-clamp-2">
                          {post.post_text}
                        </p>
                      </div>
                    ))}
                    
                    {currentSchedule.posts.length > 3 && (
                      <p className="text-sm text-gray-500 text-center">
                        +{currentSchedule.posts.length - 3} more posts
                      </p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No content for this week
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Generate your first weekly content schedule to get started.
                  </p>
                  <Button onClick={() => setShowGenerator(true)}>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate Content
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Schedules */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Schedules</CardTitle>
              <CardDescription>
                Your previously generated content schedules
              </CardDescription>
            </CardHeader>
            <CardContent>
              {recentSchedules.length > 0 ? (
                <div className="space-y-3">
                  {recentSchedules.map((schedule) => (
                    <div 
                      key={schedule.id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => setSelectedSchedule(schedule)}
                    >
                      <div>
                        <p className="font-medium">
                          {format(new Date(schedule.week_start_date), 'MMM d')} - {format(new Date(schedule.week_end_date), 'MMM d, yyyy')}
                        </p>
                        <p className="text-sm text-gray-600">
                          {schedule.posts.length} posts • {schedule.tone} tone
                        </p>
                      </div>
                      <Badge variant="outline">
                        {schedule.posts.length}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No schedules created yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        {currentSchedule && (
          <div className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks for your content management
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-4">
                  <Button onClick={() => setShowGenerator(true)}>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate New Week
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => setSelectedSchedule(currentSchedule)}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    View Current Schedule
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
