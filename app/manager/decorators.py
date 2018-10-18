from functools import wraps
from .models import Secret
from django.shortcuts import get_object_or_404
from django.http import Http404

def groups_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        print(request.user)
        user_groups = request.user.groups.all()
        secret = get_object_or_404(Secret, pk=kwargs['secret_id'])
        if not secret.groups.exists():
            return function(request, *args, **kwargs)

        for g in secret.groups.all():
            if g in user_groups:
                return function(request, *args, **kwargs)
        raise Http404

    return wrap