import openai
import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

class AIContentService:
    """Service for AI-powered content generation"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def generate_weekly_content(self, insurance_types: List[str], tone: str, 
                              additional_prompt: str, week_start: datetime.date) -> List[Dict[str, Any]]:
        """Generate a week's worth of social media content"""
        
        # Generate the content prompt
        prompt = self._create_content_prompt(insurance_types, tone, additional_prompt, week_start)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3500,
                temperature=0.7
            )
            
            content_text = response.choices[0].message.content
            
            # Parse the JSON response
            posts_data = self._parse_ai_response(content_text)
            
            # Enhance posts with additional metadata
            enhanced_posts = self._enhance_posts(posts_data, week_start, insurance_types)
            
            return enhanced_posts, response.usage.total_tokens
            
        except Exception as e:
            raise Exception(f"Failed to generate content: {str(e)}")
    
    def generate_image_for_post(self, post_text: str, image_description: str, 
                               insurance_type: str = None) -> str:
        """Generate an image for a social media post using DALL-E"""
        
        # Create enhanced image prompt
        enhanced_prompt = self._create_image_prompt(post_text, image_description, insurance_type)
        
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            return image_url
            
        except Exception as e:
            raise Exception(f"Failed to generate image: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for content generation"""
        return """You are an expert social media content creator specializing in insurance marketing for licensed insurance agents. 

Your expertise includes:
- Creating compliant, engaging content that builds trust and relationships
- Understanding insurance regulations and avoiding misleading claims
- Crafting content that resonates with warm market audiences (friends, family, existing contacts)
- Incorporating current events, seasonal themes, and life events naturally
- Balancing educational value with personal connection

Always respond with valid JSON in the exact format requested. Focus on relationship-building rather than direct sales."""
    
    def _create_content_prompt(self, insurance_types: List[str], tone: str, 
                              additional_prompt: str, week_start: datetime.date) -> str:
        """Create the detailed prompt for content generation"""
        
        # Map insurance types to descriptions
        insurance_descriptions = {
            'mortgage_protection': 'Mortgage Protection Insurance - helps pay off mortgage if policyholder dies',
            'index_universal_life': 'Index Universal Life Insurance - permanent life insurance with investment component',
            'term_life_living_benefits': 'Term Life Insurance with Living Benefits - temporary coverage with accelerated death benefits',
            'final_expense': 'Final Expense Insurance - covers funeral and burial costs',
            'annuities': 'Annuities - retirement income products for secure retirement',
            'health_insurance': 'Health Insurance - medical coverage and benefits'
        }
        
        selected_types = [insurance_descriptions.get(t, t) for t in insurance_types]
        types_text = ', '.join(selected_types)
        
        # Get contextual information
        current_month = week_start.strftime('%B')
        current_season = self._get_season(week_start)
        week_end = week_start + timedelta(days=6)
        
        # Get relevant events/themes for the time period
        themes = self._get_seasonal_themes(week_start)
        
        prompt = f"""
Create 7 social media posts (one for each day from {week_start.strftime('%B %d')} to {week_end.strftime('%B %d, %Y')}) for an insurance agent who specializes in: {types_text}

REQUIREMENTS:
- Tone: {tone.replace('_', ' ').title()}
- Target: Warm market (people who already know and trust the agent)
- Focus: Education, relationship building, trust development
- Compliance: No misleading claims, avoid pressure tactics
- Variety: Mix educational, personal, seasonal, and industry insights
- Current context: {current_month}, {current_season}, {', '.join(themes)}

CONTENT GUIDELINES:
1. Educational posts: Explain insurance concepts simply
2. Personal posts: Share relatable stories or experiences
3. Seasonal posts: Connect insurance to current events/seasons
4. Industry insights: Share relevant news or trends
5. Community posts: Highlight local events or causes
6. Testimonial-style: Share success stories (anonymized)
7. Question posts: Engage audience with thoughtful questions

Additional requirements: {additional_prompt if additional_prompt else 'None specified'}

RESPONSE FORMAT (JSON array with exactly 7 objects):
[
  {{
    "day": 1,
    "post_text": "Engaging post text with natural hashtags integrated",
    "image_description": "Detailed description for AI image generation",
    "hashtags": ["#InsuranceEducation", "#LifeInsurance", "#FinancialPlanning"],
    "insurance_focus": "mortgage_protection",
    "content_theme": "educational",
    "engagement_hook": "Question or call-to-action to encourage interaction"
  }}
]

Ensure each post is unique, valuable, and builds trust without being salesy.
"""
        
        return prompt
    
    def _create_image_prompt(self, post_text: str, image_description: str, 
                            insurance_type: str = None) -> str:
        """Create an enhanced prompt for image generation"""
        
        # Base style guidelines
        style_elements = [
            "professional but approachable",
            "clean modern design",
            "warm and trustworthy feeling",
            "suitable for social media",
            "high quality and polished"
        ]
        
        # Insurance-specific visual elements
        insurance_visuals = {
            'mortgage_protection': 'family home, protection shield, happy family',
            'index_universal_life': 'growth charts, financial security, future planning',
            'term_life_living_benefits': 'family protection, life stages, security umbrella',
            'final_expense': 'dignity, peace of mind, family comfort',
            'annuities': 'retirement lifestyle, financial freedom, golden years',
            'health_insurance': 'healthcare, wellness, medical protection'
        }
        
        visual_context = insurance_visuals.get(insurance_type, 'financial security, trust, protection')
        
        enhanced_prompt = f"""
Create a professional social media image that is {', '.join(style_elements)}.

Image concept: {image_description}

Visual elements to include: {visual_context}

Style requirements:
- Avoid overly corporate or stock photo appearance
- Include subtle insurance/financial themes
- Use calming, trustworthy colors (blues, greens, warm neutrals)
- Ensure text overlay space if needed
- Make it engaging and scroll-stopping
- Suitable for LinkedIn, Facebook, and Instagram

The image should complement this social media post: "{post_text[:100]}..."

Avoid: Generic stock photos, overly salesy imagery, complex charts, small text
"""
        
        return enhanced_prompt
    
    def _parse_ai_response(self, content_text: str) -> List[Dict[str, Any]]:
        """Parse the AI response and extract JSON"""
        try:
            # Try direct JSON parsing first
            posts_data = json.loads(content_text)
            return posts_data
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                try:
                    posts_data = json.loads(json_match.group())
                    return posts_data
                except:
                    pass
            
            # If all else fails, create fallback content
            return self._create_fallback_content()
    
    def _enhance_posts(self, posts_data: List[Dict[str, Any]], week_start: datetime.date, 
                      insurance_types: List[str]) -> List[Dict[str, Any]]:
        """Enhance posts with additional metadata and validation"""
        enhanced_posts = []
        
        for i, post_data in enumerate(posts_data[:7]):  # Ensure max 7 posts
            post_date = week_start + timedelta(days=i)
            
            # Ensure required fields exist
            enhanced_post = {
                'day': i + 1,
                'post_date': post_date.isoformat(),
                'post_text': post_data.get('post_text', ''),
                'image_description': post_data.get('image_description', 'Professional insurance-related image'),
                'hashtags': post_data.get('hashtags', ['#Insurance', '#FinancialPlanning']),
                'insurance_focus': post_data.get('insurance_focus', random.choice(insurance_types)),
                'content_theme': post_data.get('content_theme', 'general'),
                'engagement_hook': post_data.get('engagement_hook', 'What are your thoughts?')
            }
            
            # Validate and clean hashtags
            enhanced_post['hashtags'] = self._validate_hashtags(enhanced_post['hashtags'])
            
            # Ensure insurance focus is valid
            if enhanced_post['insurance_focus'] not in insurance_types:
                enhanced_post['insurance_focus'] = random.choice(insurance_types)
            
            enhanced_posts.append(enhanced_post)
        
        return enhanced_posts
    
    def _validate_hashtags(self, hashtags: List[str]) -> List[str]:
        """Validate and clean hashtags"""
        cleaned_hashtags = []
        for tag in hashtags:
            # Ensure hashtag starts with #
            if not tag.startswith('#'):
                tag = '#' + tag
            # Remove spaces and special characters
            tag = ''.join(c for c in tag if c.isalnum() or c == '#')
            if len(tag) > 1:  # Must have content after #
                cleaned_hashtags.append(tag)
        
        # Ensure we have at least some hashtags
        if not cleaned_hashtags:
            cleaned_hashtags = ['#Insurance', '#FinancialPlanning', '#TrustYourAgent']
        
        return cleaned_hashtags[:10]  # Limit to 10 hashtags
    
    def _get_season(self, date: datetime.date) -> str:
        """Get the season for a given date"""
        month = date.month
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"
    
    def _get_seasonal_themes(self, date: datetime.date) -> List[str]:
        """Get relevant themes for the time period"""
        month = date.month
        themes = []
        
        # Monthly themes
        monthly_themes = {
            1: ["New Year resolutions", "fresh starts", "financial planning"],
            2: ["Heart health", "Valentine's Day", "love and protection"],
            3: ["Spring cleaning", "renewal", "Women's History Month"],
            4: ["Easter", "spring renewal", "tax season"],
            5: ["Mother's Day", "graduation season", "spring activities"],
            6: ["Father's Day", "graduation", "summer planning"],
            7: ["summer vacation", "family time", "Independence Day"],
            8: ["back to school", "summer activities", "family preparation"],
            9: ["Life Insurance Awareness Month", "back to school", "fall preparation"],
            10: ["Halloween", "autumn", "Breast Cancer Awareness"],
            11: ["Thanksgiving", "gratitude", "family gatherings"],
            12: ["holidays", "year-end planning", "family traditions"]
        }
        
        themes.extend(monthly_themes.get(month, ["general financial wellness"]))
        
        # Add general themes
        themes.extend(["financial literacy", "family protection", "peace of mind"])
        
        return themes
    
    def _create_fallback_content(self) -> List[Dict[str, Any]]:
        """Create fallback content if AI generation fails"""
        fallback_posts = [
            {
                "day": 1,
                "post_text": "Starting the week thinking about the importance of protecting what matters most. Your family, your home, your future - they all deserve the security that comes with proper planning. What's your biggest financial priority right now? #FinancialPlanning #FamilyFirst",
                "image_description": "Warm family scene with protection theme",
                "hashtags": ["#FinancialPlanning", "#FamilyFirst", "#Insurance"],
                "insurance_focus": "term_life_living_benefits",
                "content_theme": "educational",
                "engagement_hook": "What's your biggest financial priority right now?"
            },
            {
                "day": 2,
                "post_text": "Did you know that many people are just one unexpected event away from financial hardship? It's not about being pessimistic - it's about being prepared. Small steps today can make a huge difference tomorrow. #FinancialWisdom #BePrepared",
                "image_description": "Umbrella protecting from storm, financial security concept",
                "hashtags": ["#FinancialWisdom", "#BePrepared", "#Insurance"],
                "insurance_focus": "mortgage_protection",
                "content_theme": "educational",
                "engagement_hook": "What small step will you take today?"
            }
            # Add more fallback posts as needed...
        ]
        
        # Generate 7 days of content
        while len(fallback_posts) < 7:
            fallback_posts.append({
                "day": len(fallback_posts) + 1,
                "post_text": f"Day {len(fallback_posts) + 1}: Remember, financial planning isn't just about money - it's about peace of mind and protecting the people you love. #FinancialPlanning #PeaceOfMind",
                "image_description": "Professional financial planning concept",
                "hashtags": ["#FinancialPlanning", "#PeaceOfMind", "#Insurance"],
                "insurance_focus": "final_expense",
                "content_theme": "general",
                "engagement_hook": "How do you find peace of mind in your financial planning?"
            })
        
        return fallback_posts[:7]
