from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from enum import Enum
import json

db = SQLAlchemy()

class SubscriptionStatus(Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class InsuranceType(Enum):
    MORTGAGE_PROTECTION = "mortgage_protection"
    INDEX_UNIVERSAL_LIFE = "index_universal_life"
    TERM_LIFE_LIVING_BENEFITS = "term_life_living_benefits"
    FINAL_EXPENSE = "final_expense"
    ANNUITIES = "annuities"
    HEALTH_INSURANCE = "health_insurance"

class ToneType(Enum):
    SERIOUS = "serious"
    FUNNY = "funny"
    DIRECT = "direct"
    SARCASTIC = "sarcastic"
    URGENT = "urgent"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Subscription information
    subscription_status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    trial_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    trial_end_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    subscription_start_date = db.Column(db.DateTime)
    subscription_end_date = db.Column(db.DateTime)
    stripe_customer_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100))
    
    # Agent preferences
    insurance_types = db.Column(db.Text)  # JSON string of selected insurance types
    default_tone = db.Column(db.Enum(ToneType), default=ToneType.PROFESSIONAL)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content_schedules = db.relationship('ContentSchedule', backref='agent', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Agent {self.email}>'
    
    def get_insurance_types(self):
        """Get insurance types as a list"""
        if self.insurance_types:
            return json.loads(self.insurance_types)
        return []
    
    def set_insurance_types(self, types_list):
        """Set insurance types from a list"""
        self.insurance_types = json.dumps(types_list)
    
    def is_trial_active(self):
        """Check if trial period is still active"""
        return (self.subscription_status == SubscriptionStatus.TRIAL and 
                datetime.utcnow() <= self.trial_end_date)
    
    def is_subscription_active(self):
        """Check if subscription is active (including trial)"""
        return (self.subscription_status in [SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE] and
                (self.subscription_status == SubscriptionStatus.ACTIVE or self.is_trial_active()))
    
    def can_generate_content(self):
        """Check if agent can generate content (active subscription or trial)"""
        return self.is_subscription_active()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'subscription_status': self.subscription_status.value,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'insurance_types': self.get_insurance_types(),
            'default_tone': self.default_tone.value,
            'created_at': self.created_at.isoformat()
        }

class ContentSchedule(db.Model):
    __tablename__ = 'content_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    
    # Schedule metadata
    week_start_date = db.Column(db.Date, nullable=False)
    week_end_date = db.Column(db.Date, nullable=False)
    generation_prompt = db.Column(db.Text)  # Additional prompting from user
    tone = db.Column(db.Enum(ToneType), nullable=False)
    insurance_types = db.Column(db.Text)  # JSON string of insurance types for this schedule
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('SocialMediaPost', backref='schedule', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ContentSchedule {self.week_start_date} - {self.week_end_date}>'
    
    def get_insurance_types(self):
        """Get insurance types as a list"""
        if self.insurance_types:
            return json.loads(self.insurance_types)
        return []
    
    def set_insurance_types(self, types_list):
        """Set insurance types from a list"""
        self.insurance_types = json.dumps(types_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'week_start_date': self.week_start_date.isoformat(),
            'week_end_date': self.week_end_date.isoformat(),
            'generation_prompt': self.generation_prompt,
            'tone': self.tone.value,
            'insurance_types': self.get_insurance_types(),
            'created_at': self.created_at.isoformat(),
            'posts': [post.to_dict() for post in self.posts]
        }

class SocialMediaPost(db.Model):
    __tablename__ = 'social_media_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('content_schedules.id'), nullable=False)
    
    # Post content
    post_date = db.Column(db.Date, nullable=False)
    post_text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))  # URL to generated image/gif/meme
    image_description = db.Column(db.Text)  # Description of the image for accessibility
    hashtags = db.Column(db.Text)  # JSON string of hashtags
    
    # Metadata
    insurance_type_focus = db.Column(db.Enum(InsuranceType))  # Primary insurance type for this post
    content_theme = db.Column(db.String(100))  # e.g., "holiday", "current_event", "educational"
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialMediaPost {self.post_date}>'
    
    def get_hashtags(self):
        """Get hashtags as a list"""
        if self.hashtags:
            return json.loads(self.hashtags)
        return []
    
    def set_hashtags(self, hashtags_list):
        """Set hashtags from a list"""
        self.hashtags = json.dumps(hashtags_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'post_date': self.post_date.isoformat(),
            'post_text': self.post_text,
            'image_url': self.image_url,
            'image_description': self.image_description,
            'hashtags': self.get_hashtags(),
            'insurance_type_focus': self.insurance_type_focus.value if self.insurance_type_focus else None,
            'content_theme': self.content_theme,
            'created_at': self.created_at.isoformat()
        }

class APIUsage(db.Model):
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    
    # Usage tracking
    endpoint = db.Column(db.String(100), nullable=False)  # e.g., "generate_content", "generate_image"
    tokens_used = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<APIUsage {self.endpoint} - {self.tokens_used} tokens>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'endpoint': self.endpoint,
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            'created_at': self.created_at.isoformat()
        }
