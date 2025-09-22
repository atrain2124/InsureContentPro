from flask import Blueprint, request, jsonify
from src.models.insurance_models import db, SocialMediaPost, APIUsage
from src.routes.auth import require_auth, require_active_subscription
from src.services.ai_service import AIContentService
import requests
import os
from urllib.parse import urlparse

images_bp = Blueprint('images', __name__)

@images_bp.route('/generate-image/<int:post_id>', methods=['POST'])
@require_auth
@require_active_subscription
def generate_image_for_post(agent, post_id):
    """Generate an image for a specific social media post"""
    try:
        # Get the post
        post = SocialMediaPost.query.join(
            SocialMediaPost.schedule
        ).filter(
            SocialMediaPost.id == post_id,
            SocialMediaPost.schedule.has(agent_id=agent.id)
        ).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check if image already exists
        if post.image_url:
            return jsonify({
                'message': 'Image already exists for this post',
                'image_url': post.image_url
            }), 200
        
        # Generate image using AI service
        ai_service = AIContentService()
        
        try:
            image_url = ai_service.generate_image_for_post(
                post_text=post.post_text,
                image_description=post.image_description,
                insurance_type=post.insurance_type_focus.value if post.insurance_type_focus else None
            )
            
            # Update post with image URL
            post.image_url = image_url
            
            # Track API usage
            api_usage = APIUsage(
                agent_id=agent.id,
                endpoint='generate_image',
                tokens_used=0,  # DALL-E doesn't use tokens
                cost=0.04  # Approximate cost for DALL-E 3 standard quality
            )
            db.session.add(api_usage)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Image generated successfully',
                'image_url': image_url,
                'post_id': post_id
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Failed to generate image', 'details': str(e)}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500

@images_bp.route('/generate-all-images/<int:schedule_id>', methods=['POST'])
@require_auth
@require_active_subscription
def generate_all_images_for_schedule(agent, schedule_id):
    """Generate images for all posts in a schedule"""
    try:
        # Get all posts in the schedule
        posts = SocialMediaPost.query.join(
            SocialMediaPost.schedule
        ).filter(
            SocialMediaPost.schedule_id == schedule_id,
            SocialMediaPost.schedule.has(agent_id=agent.id),
            SocialMediaPost.image_url.is_(None)  # Only posts without images
        ).all()
        
        if not posts:
            return jsonify({'message': 'No posts found or all posts already have images'}), 200
        
        ai_service = AIContentService()
        generated_images = []
        failed_generations = []
        
        for post in posts:
            try:
                image_url = ai_service.generate_image_for_post(
                    post_text=post.post_text,
                    image_description=post.image_description,
                    insurance_type=post.insurance_type_focus.value if post.insurance_type_focus else None
                )
                
                post.image_url = image_url
                generated_images.append({
                    'post_id': post.id,
                    'image_url': image_url
                })
                
                # Track API usage
                api_usage = APIUsage(
                    agent_id=agent.id,
                    endpoint='generate_image',
                    tokens_used=0,
                    cost=0.04
                )
                db.session.add(api_usage)
                
            except Exception as e:
                failed_generations.append({
                    'post_id': post.id,
                    'error': str(e)
                })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Generated {len(generated_images)} images successfully',
            'generated_images': generated_images,
            'failed_generations': failed_generations,
            'total_cost': len(generated_images) * 0.04
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to generate images', 'details': str(e)}), 500

@images_bp.route('/download-image/<int:post_id>', methods=['GET'])
@require_auth
def download_image(agent, post_id):
    """Download and save an image locally for a post"""
    try:
        # Get the post
        post = SocialMediaPost.query.join(
            SocialMediaPost.schedule
        ).filter(
            SocialMediaPost.id == post_id,
            SocialMediaPost.schedule.has(agent_id=agent.id)
        ).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        if not post.image_url:
            return jsonify({'error': 'No image URL found for this post'}), 404
        
        # Download the image
        try:
            response = requests.get(post.image_url, timeout=30)
            response.raise_for_status()
            
            # Create filename
            parsed_url = urlparse(post.image_url)
            file_extension = '.png'  # Default to PNG
            if '.' in parsed_url.path:
                file_extension = '.' + parsed_url.path.split('.')[-1]
            
            filename = f"post_{post_id}_{post.post_date.strftime('%Y%m%d')}{file_extension}"
            
            return jsonify({
                'message': 'Image ready for download',
                'filename': filename,
                'image_data': response.content.hex(),  # Hex encoded binary data
                'content_type': response.headers.get('content-type', 'image/png')
            }), 200
            
        except requests.RequestException as e:
            return jsonify({'error': 'Failed to download image', 'details': str(e)}), 500
        
    except Exception as e:
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500

@images_bp.route('/regenerate-image/<int:post_id>', methods=['POST'])
@require_auth
@require_active_subscription
def regenerate_image(agent, post_id):
    """Regenerate an image for a post with optional new description"""
    try:
        data = request.get_json() or {}
        new_description = data.get('image_description')
        
        # Get the post
        post = SocialMediaPost.query.join(
            SocialMediaPost.schedule
        ).filter(
            SocialMediaPost.id == post_id,
            SocialMediaPost.schedule.has(agent_id=agent.id)
        ).first()
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Update description if provided
        if new_description:
            post.image_description = new_description
        
        # Generate new image
        ai_service = AIContentService()
        
        try:
            image_url = ai_service.generate_image_for_post(
                post_text=post.post_text,
                image_description=post.image_description,
                insurance_type=post.insurance_type_focus.value if post.insurance_type_focus else None
            )
            
            # Update post with new image URL
            post.image_url = image_url
            
            # Track API usage
            api_usage = APIUsage(
                agent_id=agent.id,
                endpoint='regenerate_image',
                tokens_used=0,
                cost=0.04
            )
            db.session.add(api_usage)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Image regenerated successfully',
                'image_url': image_url,
                'post_id': post_id
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Failed to regenerate image', 'details': str(e)}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500
