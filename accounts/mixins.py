from django.shortcuts import redirect

class RedirectAuthenticatedMixin:
    """
    Redirect to the home page if the user is authenticated.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)
