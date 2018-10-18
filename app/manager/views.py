from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from django.db.models import Q
from datetime import datetime
from .models import Secret
from .forms import SecretForm
from .vault import VaultClient
from .decorators import groups_required

vault_client = VaultClient()

@login_required
def index(request):
    return render(request, 'manager/index.html')

@login_required
def secrets(request):
    # we filter secrets owned by the session user having at least one group of the user or None
    secrets = Secret.objects.filter(
        Q(groups__in=request.user.groups.all()) | Q(groups__isnull=True)
        ).order_by('label')
    
    data = request.GET
    if data.get('search', '') != '':
        secrets = secrets.filter(label__icontains=data.get('search'))

    context = {'secrets': secrets, 'form': data}
    return render(request, 'manager/secrets.html', context)

@sensitive_variables('secret')
@login_required
@groups_required
def secret(request, secret_id):
    secret = get_object_or_404(Secret, id=secret_id)

    vault_data = vault_client.read('{0}'.format(secret.label))
    if vault_data != None:
        secret.password = vault_data['data'].get('password', None)
        secret.config = vault_data['data'].get('config', None)

    context = {'secret': secret}
    return render(request, 'manager/secret.html', context)

@sensitive_variables('new_secret')
@sensitive_post_parameters()
@login_required
def new_secret(request):
    if request.method != 'POST':
        form = SecretForm()
    else:
        form = SecretForm(data=request.POST)
        if form.is_valid():
            new_secret = form.save(commit=False)
            vault_client.write('{0}'.format(new_secret.label), 
                password=new_secret.password, 
                config=new_secret.config)
            
            new_secret.creator = request.user
            new_secret.password = ''
            new_secret.config = ''
            new_secret.save()
            return HttpResponseRedirect(reverse('manager:secrets'))

    context = {'form': form}
    return render(request, 'manager/new_secret.html', context)

@sensitive_variables('secret')
@sensitive_post_parameters()
@login_required
@groups_required
def edit_secret(request, secret_id):
    """Edit an existing secret."""
    secret = get_object_or_404(Secret, id=secret_id)

    vault_data = vault_client.read('{0}'.format(secret.label))
    if vault_data != None:
        secret.password = vault_data['data'].get('password', None)
        secret.config = vault_data['data'].get('config', None)

    if request.method != 'POST':
        form = SecretForm(instance=secret, initial={'confirm_password': secret.password})
    else:
        form = SecretForm(instance=secret, data=request.POST)
        if form.is_valid():
            secret = form.save(commit=False)
            vault_client.write('{0}'.format(secret.label), 
                password=secret.password, 
                config=secret.config)
            
            secret.date_changed = datetime.now()
            secret.creator = request.user
            secret.password = ''
            secret.config = ''
            secret.save()
            # since we are using commit=False, save the many-to-many data for the form.
            form.save_m2m()

            return HttpResponseRedirect(reverse('manager:secret', args=[secret.id]))

    context = {'secret': secret, 'form': form}
    return render(request, 'manager/edit_secret.html', context)

@login_required
@groups_required
def delete_secret(request, secret_id):
    secret = get_object_or_404(Secret, id=secret_id)

    if request.method == "POST":
        vault_client.delete('{0}'.format(secret.label))
        secret.delete()
        return HttpResponseRedirect(reverse('manager:secrets'))
    
    context = {'secret': secret}
    return render(request, 'manager/delete_secret.html', context)
    

def is_member_of(user, groups):
    user_groups = user.groups.all()
    for g in groups:
        if g in user_groups:
            return True
    return False