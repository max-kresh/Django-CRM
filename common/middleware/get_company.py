import jwt
from django.conf import settings
from django.contrib.auth import logout
from django.core.exceptions import ValidationError,PermissionDenied
from rest_framework import status
from rest_framework.response import Response
from crum import get_current_user
from django.utils.functional import SimpleLazyObject
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse

from common.models import Org, Profile, User
from common.utils import Constants


def get_actual_value(request):
    if request.user is None:
        return None

    return request.user #here should have value, so any code using request.user will work

class GetProfileAndOrg(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try: 
            self.process_request(request)
            return self.get_response(request)
        except AuthenticationFailed as e:
            return JsonResponse({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except PermissionDenied:
            return JsonResponse({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        except:
            return JsonResponse({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def process_request(self, request):
        try :
            request.profile = None
            user_id = None
            # here I am getting the the jwt token passing in header
            if request.headers.get("Authorization"):
                token1 = request.headers.get("Authorization")
                token = token1.split(" ")[1]  # getting the token value
                try:
                    decoded = jwt.decode(token, (settings.SECRET_KEY), algorithms=[settings.JWT_ALGO])
                except:
                    raise AuthenticationFailed('Invalid API Key', code=status.HTTP_401_UNAUTHORIZED)
                user_id = decoded['user_id']
            api_key = request.headers.get('Token')  # Get API key from request query params
            if api_key:
                try:
                    organization = Org.objects.get(api_key=api_key)
                    api_key_user = organization
                    request.META['org'] = api_key_user.id
                    profile = Profile.objects.filter(org=api_key_user, role=Constants.ADMIN).first()
                    user_id = profile.user.id
                except Org.DoesNotExist:
                    raise AuthenticationFailed('Invalid API Key', code=status.HTTP_401_UNAUTHORIZED)
            if user_id is not None:
                # Frontend app sends id of the org and Swagger UI sends name 
                # of the org. This blog is changed to meet both sides.
                org=request.headers.get("org")
                if org:
                    profile = None
                    try: 
                        profile = Profile.objects.get(
                            user_id=user_id, org=org, is_active=True
                        )
                    except:
                        org_by_name = Org.objects.get(name=str(org))
                        profile = Profile.objects.get(
                            user_id=user_id, org=org_by_name, is_active=True
                        )
                    if profile:
                        request.profile = profile
        except AuthenticationFailed as e:
            raise AuthenticationFailed(e)
        except:
            raise PermissionDenied()
            
