from django.http import JsonResponse
from django.urls import resolve
from .models import UsageSession
import logging

logger = logging.getLogger(__name__)

class UsageLimitMiddleware:
    """Track and enforce usage limits for anonymous users"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.tracked_endpoints = {
            'generate-image': 'match',
            'randomize-image': 'randomize',
        }
    
    def __call__(self, request):
        # Skip for authenticated users
        if request.user.is_authenticated:
            logger.debug("🔐 User authenticated - skipping usage limits")
            return self.get_response(request)
            
        # Only check POST requests
        if request.method != 'POST':
            return self.get_response(request)
            
        # Check if this is a tracked endpoint
        try:
            resolved = resolve(request.path_info)
            endpoint_name = resolved.url_name
        except:
            return self.get_response(request)
            
        if endpoint_name not in self.tracked_endpoints:
            return self.get_response(request)
            
        logger.debug(f"🎯 Processing tracked endpoint: {endpoint_name}")
        
        # 🔥 CRITICAL FIX: Ensure session exists BEFORE checking usage
        if not request.session.session_key:
            request.session.create()
            logger.debug(f"🔑 Created new session: {request.session.session_key}")
        else:
            logger.debug(f"🔑 Using existing session: {request.session.session_key}")
            
        # FORCE session save to ensure it persists
        request.session.save()
        
        # Get or create usage session
        usage_session = UsageSession.get_or_create_for_session(request.session.session_key)
        logger.debug(f"📊 Usage session: matches={usage_session.matches_used}/{usage_session.MAX_MATCHES}, randomizes={usage_session.randomizes_used}/{usage_session.MAX_RANDOMIZES}")
        
        # Check limits BEFORE processing
        feature_type = self.tracked_endpoints[endpoint_name]
        
        if feature_type == 'match' and not usage_session.can_match:
            logger.debug("🚫 Match limit reached")
            return self.create_limit_response('match', usage_session)
        elif feature_type == 'randomize' and not usage_session.can_randomize:
            logger.debug("🚫 Randomize limit reached")
            return self.create_limit_response('randomize', usage_session)
            
        # Store usage session for view to use
        request.usage_session = usage_session
        logger.debug(f"✅ Request approved - feature: {feature_type}")
        
        return self.get_response(request)
    
    def create_limit_response(self, feature_type, usage_session):
        """Create response when user hits limit"""
        logger.info(f"🚫 Limit reached for {feature_type}")
        return JsonResponse({
            'error': 'Usage limit reached',
            'message': f'You have reached your limit for {feature_type}. Please sign up to continue.',
            'feature_type': feature_type,
            'usage': {
                'matches_used': usage_session.matches_used,
                'matches_limit': usage_session.MAX_MATCHES,
                'randomizes_used': usage_session.randomizes_used,
                'randomizes_limit': usage_session.MAX_RANDOMIZES,
                'can_match': usage_session.can_match,
                'can_randomize': usage_session.can_randomize,
                'is_limited': usage_session.is_limited,
            },
            'registration_required': True
        }, status=429)