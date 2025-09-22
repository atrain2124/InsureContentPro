import { useState } from 'react';
import { imagesAPI, contentAPI } from '../lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  ArrowLeft, 
  Calendar, 
  Copy, 
  Download, 
  Image as ImageIcon, 
  RefreshCw, 
  Trash2, 
  Wand2,
  CheckCircle,
  ExternalLink,
  Hash
} from 'lucide-react';
import { format } from 'date-fns';

const ScheduleView = ({ schedule, onBack, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState({});
  const [error, setError] = useState('');
  const [copiedPost, setCopiedPost] = useState(null);
  const [selectedPost, setSelectedPost] = useState(null);

  const handleCopyPost = async (post) => {
    try {
      const textToCopy = `${post.post_text}\n\n${post.hashtags?.join(' ') || ''}`;
      await navigator.clipboard.writeText(textToCopy);
      setCopiedPost(post.id);
      setTimeout(() => setCopiedPost(null), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const handleGenerateImage = async (postId) => {
    setImageLoading(prev => ({ ...prev, [postId]: true }));
    setError('');

    try {
      await imagesAPI.generateImage(postId);
      onRefresh(); // Refresh the schedule to show the new image
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to generate image');
    } finally {
      setImageLoading(prev => ({ ...prev, [postId]: false }));
    }
  };

  const handleGenerateAllImages = async () => {
    setLoading(true);
    setError('');

    try {
      await imagesAPI.generateAllImages(schedule.id);
      onRefresh(); // Refresh the schedule to show the new images
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to generate images');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSchedule = async () => {
    if (!window.confirm('Are you sure you want to delete this schedule? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      await contentAPI.deleteSchedule(schedule.id);
      onBack(); // Go back to dashboard
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to delete schedule');
      setLoading(false);
    }
  };

  const getPostsWithoutImages = () => {
    return schedule.posts.filter(post => !post.image_url);
  };

  const PostCard = ({ post, index }) => (
    <Card key={post.id} className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">
              {format(new Date(post.post_date), 'EEEE, MMMM d')}
            </CardTitle>
            <CardDescription>
              Day {index + 1} • {post.content_theme || 'General'} content
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            {post.insurance_type_focus && (
              <Badge variant="outline" className="text-xs">
                {post.insurance_type_focus.replace('_', ' ')}
              </Badge>
            )}
            {post.image_url && (
              <Badge variant="secondary" className="text-xs">
                <ImageIcon className="h-3 w-3 mr-1" />
                Image
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Post Text */}
        <div>
          <h4 className="font-medium mb-2">Post Content</h4>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-gray-800 whitespace-pre-wrap">{post.post_text}</p>
          </div>
        </div>

        {/* Hashtags */}
        {post.hashtags && post.hashtags.length > 0 && (
          <div>
            <h4 className="font-medium mb-2 flex items-center">
              <Hash className="h-4 w-4 mr-1" />
              Hashtags
            </h4>
            <div className="flex flex-wrap gap-1">
              {post.hashtags.map((hashtag, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  {hashtag}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Image Section */}
        <div>
          <h4 className="font-medium mb-2 flex items-center">
            <ImageIcon className="h-4 w-4 mr-1" />
            Visual Content
          </h4>
          
          {post.image_url ? (
            <div className="space-y-3">
              <div className="relative">
                <img 
                  src={post.image_url} 
                  alt="Generated content" 
                  className="w-full h-48 object-cover rounded-lg border"
                />
                <Button
                  size="sm"
                  variant="secondary"
                  className="absolute top-2 right-2"
                  onClick={() => window.open(post.image_url, '_blank')}
                >
                  <ExternalLink className="h-3 w-3" />
                </Button>
              </div>
              <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                <strong>Description:</strong> {post.image_description}
              </p>
            </div>
          ) : (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <ImageIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600 mb-2">No image generated yet</p>
              <p className="text-sm text-gray-500 mb-3">
                <strong>Suggested image:</strong> {post.image_description}
              </p>
              <Button
                size="sm"
                onClick={() => handleGenerateImage(post.id)}
                disabled={imageLoading[post.id]}
              >
                {imageLoading[post.id] ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                    <span>Generating...</span>
                  </div>
                ) : (
                  <>
                    <Wand2 className="h-3 w-3 mr-1" />
                    Generate Image
                  </>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleCopyPost(post)}
            className="flex items-center space-x-1"
          >
            {copiedPost === post.id ? (
              <>
                <CheckCircle className="h-3 w-3" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" />
                <span>Copy Post</span>
              </>
            )}
          </Button>
          
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm">
                View Details
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  {format(new Date(post.post_date), 'EEEE, MMMM d, yyyy')}
                </DialogTitle>
                <DialogDescription>
                  Complete post details and content
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Full Post Text</h4>
                  <Textarea 
                    value={post.post_text} 
                    readOnly 
                    rows={6}
                    className="resize-none"
                  />
                </div>
                
                {post.image_url && (
                  <div>
                    <h4 className="font-medium mb-2">Generated Image</h4>
                    <img 
                      src={post.image_url} 
                      alt="Generated content" 
                      className="w-full max-w-md mx-auto rounded-lg border"
                    />
                  </div>
                )}
                
                <div className="flex justify-between">
                  <Button
                    variant="outline"
                    onClick={() => handleCopyPost(post)}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Post & Hashtags
                  </Button>
                  
                  {post.image_url && (
                    <Button
                      variant="outline"
                      onClick={() => window.open(post.image_url, '_blank')}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Open Image
                    </Button>
                  )}
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={onBack}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-2">
                <Calendar className="h-6 w-6 text-blue-600" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900">
                    Week of {format(new Date(schedule.week_start_date), 'MMM d, yyyy')}
                  </h1>
                  <p className="text-sm text-gray-600">
                    {schedule.posts.length} posts • {schedule.tone} tone
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={handleDeleteSchedule}
                disabled={loading}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Schedule
              </Button>
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

        {/* Schedule Summary */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Schedule Summary</CardTitle>
            <CardDescription>
              Overview of your weekly content schedule
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{schedule.posts.length}</div>
                <div className="text-sm text-gray-600">Total Posts</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {schedule.posts.filter(p => p.image_url).length}
                </div>
                <div className="text-sm text-gray-600">With Images</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {getPostsWithoutImages().length}
                </div>
                <div className="text-sm text-gray-600">Need Images</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 capitalize">
                  {schedule.tone}
                </div>
                <div className="text-sm text-gray-600">Tone</div>
              </div>
            </div>
            
            {getPostsWithoutImages().length > 0 && (
              <div className="mt-6 pt-4 border-t">
                <Button
                  onClick={handleGenerateAllImages}
                  disabled={loading}
                  className="w-full md:w-auto"
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Generating Images...</span>
                    </div>
                  ) : (
                    <>
                      <Wand2 className="h-4 w-4 mr-2" />
                      Generate All Missing Images ({getPostsWithoutImages().length})
                    </>
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Insurance Types */}
        {schedule.insurance_types && schedule.insurance_types.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Insurance Focus Areas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {schedule.insurance_types.map((type, index) => (
                  <Badge key={index} variant="outline">
                    {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Posts Grid */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">Weekly Content</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {schedule.posts
              .sort((a, b) => new Date(a.post_date) - new Date(b.post_date))
              .map((post, index) => (
                <PostCard key={post.id} post={post} index={index} />
              ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ScheduleView;
