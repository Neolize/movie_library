from django.http import HttpResponseForbidden


class StaffPermissionsMixin:
    def has_permissions(self):
        return self.request.user.is_staff

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            text = "<h1 style=\"width: 400px; margin: auto; margin-top: 50px; font-size: 44px;\" >" \
                   "Access is forbidden</h1>"
            return HttpResponseForbidden(text)
        return super().dispatch(request, *args, **kwargs)
