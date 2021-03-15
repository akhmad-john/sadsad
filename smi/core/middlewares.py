from django.utils.deprecation import MiddlewareMixin

from .utils.utils import set_current_user

from re import sub
from rest_framework.authtoken.models import Token


class CurrentUserMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        if header_token is not None:
            try:
                token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
                token_obj = Token.objects.get(key=token)
                request.user = token_obj.user
            except Token.DoesNotExist:
                pass
        # This is now the correct user
        set_current_user(getattr(request, 'user', None))


class GqlCurrentUserMiddleware(object):
    def resolve(self, next, root, info, **args):
        user = info.context.user
        if user.is_authenticated:
            set_current_user(user)
        return next(root, info, **args)
