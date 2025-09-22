import { useState, useEffect } from 'react';
import { contentAPI } from '../lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Sparkles, Calendar, Target, MessageSquare, Wand2, CheckCircle } from 'lucide-react';
import { format, addDays, startOfWeek } from 'date-fns';

const ContentGenerator = ({ onScheduleGenerated, onCancel }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [insuranceTypes, setInsuranceTypes] = useState([]);
  const [tones, setTones] = useState([]);
  
  const [formData, setFormData] = useState({
    insurance_types: [],
    tone: '',
    additional_prompt: '',
    week_start_date: '',
  });

  useEffect(() => {
    loadOptions();
    setDefaultWeekStart();
  }, []);

  const loadOptions = async () => {
    try {
      const [typesResponse, tonesResponse] = await Promise.all([
        contentAPI.getInsuranceTypes(),
        contentAPI.getTones()
      ]);
      
      setInsuranceTypes(typesResponse.data.insurance_types);
      setTones(tonesResponse.data.tones);
    } catch (error) {
      console.error('Error loading options:', error);
      setError('Failed to load options. Please try again.');
    }
  };

  const setDefaultWeekStart = () => {
    const today = new Date();
    const monday = startOfWeek(today, { weekStartsOn: 1 });
    setFormData(prev => ({
      ...prev,
      week_start_date: format(monday, 'yyyy-MM-dd')
    }));
  };

  const handleInsuranceTypeChange = (typeValue, checked) => {
    setFormData(prev => ({
      ...prev,
      insurance_types: checked 
        ? [...prev.insurance_types, typeValue]
        : prev.insurance_types.filter(t => t !== typeValue)
    }));
  };

  const handleSubmit = async () => {
    if (formData.insurance_types.length === 0) {
      setError('Please select at least one insurance type');
      return;
    }
    
    if (!formData.tone) {
      setError('Please select a tone');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await contentAPI.generateSchedule(formData);
      onScheduleGenerated(response.data.schedule);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to generate content. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getWeekDateRange = () => {
    if (!formData.week_start_date) return '';
    const startDate = new Date(formData.week_start_date);
    const endDate = addDays(startDate, 6);
    return `${format(startDate, 'MMM d')} - ${format(endDate, 'MMM d, yyyy')}`;
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Target className="h-5 w-5 mr-2 text-blue-600" />
          Select Insurance Types
        </h3>
        <p className="text-gray-600 mb-4">
          Choose the types of insurance you want to focus on in your content. You can select multiple types.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {insuranceTypes.map((type) => (
            <div key={type.value} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50">
              <Checkbox
                id={type.value}
                checked={formData.insurance_types.includes(type.value)}
                onCheckedChange={(checked) => handleInsuranceTypeChange(type.value, checked)}
              />
              <Label htmlFor={type.value} className="flex-1 cursor-pointer">
                {type.label}
              </Label>
            </div>
          ))}
        </div>
        
        {formData.insurance_types.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">Selected types:</p>
            <div className="flex flex-wrap gap-2">
              {formData.insurance_types.map((typeValue) => {
                const type = insuranceTypes.find(t => t.value === typeValue);
                return (
                  <Badge key={typeValue} variant="secondary">
                    {type?.label}
                  </Badge>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <MessageSquare className="h-5 w-5 mr-2 text-blue-600" />
          Choose Your Tone
        </h3>
        <p className="text-gray-600 mb-4">
          Select the tone that best matches your personality and brand voice.
        </p>
        
        <Select value={formData.tone} onValueChange={(value) => setFormData(prev => ({ ...prev, tone: value }))}>
          <SelectTrigger>
            <SelectValue placeholder="Select a tone for your content" />
          </SelectTrigger>
          <SelectContent>
            {tones.map((tone) => (
              <SelectItem key={tone.value} value={tone.value}>
                {tone.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Calendar className="h-5 w-5 mr-2 text-blue-600" />
          Week Selection
        </h3>
        <p className="text-gray-600 mb-4">
          Choose the week you want to generate content for.
        </p>
        
        <div className="space-y-2">
          <Label htmlFor="week_start_date">Week Starting (Monday)</Label>
          <Input
            id="week_start_date"
            type="date"
            value={formData.week_start_date}
            onChange={(e) => setFormData(prev => ({ ...prev, week_start_date: e.target.value }))}
          />
          {formData.week_start_date && (
            <p className="text-sm text-gray-600">
              Content will be generated for: {getWeekDateRange()}
            </p>
          )}
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Wand2 className="h-5 w-5 mr-2 text-blue-600" />
          Additional Customization
        </h3>
        <p className="text-gray-600 mb-4">
          Add any specific instructions or themes you'd like to include in your content.
        </p>
        
        <div className="space-y-2">
          <Label htmlFor="additional_prompt">Additional Instructions (Optional)</Label>
          <Textarea
            id="additional_prompt"
            placeholder="e.g., Focus on young families, mention local community events, include retirement planning tips..."
            value={formData.additional_prompt}
            onChange={(e) => setFormData(prev => ({ ...prev, additional_prompt: e.target.value }))}
            rows={4}
          />
          <p className="text-xs text-gray-500">
            These instructions will help the AI create more targeted and relevant content for your audience.
          </p>
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="text-lg font-semibold mb-4">Review Your Selections</h3>
        
        <div className="space-y-4">
          <div>
            <p className="font-medium text-gray-700">Insurance Types:</p>
            <div className="flex flex-wrap gap-2 mt-1">
              {formData.insurance_types.map((typeValue) => {
                const type = insuranceTypes.find(t => t.value === typeValue);
                return (
                  <Badge key={typeValue} variant="outline">
                    {type?.label}
                  </Badge>
                );
              })}
            </div>
          </div>
          
          <div>
            <p className="font-medium text-gray-700">Tone:</p>
            <p className="text-gray-600 capitalize">
              {tones.find(t => t.value === formData.tone)?.label}
            </p>
          </div>
          
          <div>
            <p className="font-medium text-gray-700">Week:</p>
            <p className="text-gray-600">{getWeekDateRange()}</p>
          </div>
          
          {formData.additional_prompt && (
            <div>
              <p className="font-medium text-gray-700">Additional Instructions:</p>
              <p className="text-gray-600 text-sm bg-gray-50 p-2 rounded">
                {formData.additional_prompt}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={onCancel}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-2">
                <Sparkles className="h-6 w-6 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">Generate Content</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            {[1, 2, 3].map((stepNumber) => (
              <div key={stepNumber} className="flex items-center">
                <div className={`
                  flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium
                  ${step >= stepNumber 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                  }
                `}>
                  {step > stepNumber ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    stepNumber
                  )}
                </div>
                {stepNumber < 3 && (
                  <div className={`
                    w-16 h-1 mx-2
                    ${step > stepNumber ? 'bg-blue-600' : 'bg-gray-200'}
                  `} />
                )}
              </div>
            ))}
          </div>
          
          <div className="text-center mt-4">
            <h2 className="text-2xl font-bold text-gray-900">
              {step === 1 && 'Choose Insurance Types'}
              {step === 2 && 'Set Tone & Schedule'}
              {step === 3 && 'Review & Generate'}
            </h2>
            <p className="text-gray-600">
              Step {step} of 3
            </p>
          </div>
        </div>

        {/* Content Card */}
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>
              {step === 1 && 'Insurance Focus Areas'}
              {step === 2 && 'Content Preferences'}
              {step === 3 && 'Final Review'}
            </CardTitle>
            <CardDescription>
              {step === 1 && 'Select the insurance products you want to create content about'}
              {step === 2 && 'Configure the tone and timing for your content'}
              {step === 3 && 'Review your selections and generate your weekly content'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {step === 1 && renderStep1()}
            {step === 2 && renderStep2()}
            {step === 3 && renderStep3()}

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8 pt-6 border-t">
              <Button 
                variant="outline" 
                onClick={() => setStep(Math.max(1, step - 1))}
                disabled={step === 1}
              >
                Previous
              </Button>
              
              {step < 3 ? (
                <Button 
                  onClick={() => setStep(step + 1)}
                  disabled={
                    (step === 1 && formData.insurance_types.length === 0) ||
                    (step === 2 && (!formData.tone || !formData.week_start_date))
                  }
                >
                  Next
                </Button>
              ) : (
                <Button 
                  onClick={handleSubmit}
                  disabled={loading}
                  className="min-w-[120px]"
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Generating...</span>
                    </div>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Generate Content
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Loading State */}
        {loading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="max-w-md mx-4">
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <h3 className="text-lg font-semibold mb-2">Generating Your Content</h3>
                  <p className="text-gray-600">
                    Our AI is creating personalized social media content for your insurance business. 
                    This may take a few moments...
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};

export default ContentGenerator;
