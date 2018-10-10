from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters
from datetime import datetime
from .models import Secret
from .forms import SecretForm
from .vault import Vault

vault_client = Vault()

@login_required
def index(request):
    return render(request, 'manager/index.html')

@login_required
def secrets(request):
    secrets = Secret.objects.filter(creator=request.user).order_by('label')
    data = request.GET
    if data.get('search', '') != '':
        secrets = secrets.filter(label__icontains=data.get('search'))

    context = {'secrets': secrets, 'form': data}
    return render(request, 'manager/secrets.html', context)

@sensitive_variables('secret')
@login_required
def secret(request, secret_id):
    secret = get_object_or_404(Secret, id=secret_id)
    # check for private vault
    if secret.creator != request.user:
        raise Http404

    vault_data = vault_client.read('{0}/{1}'.format(request.user.pk, secret.label))
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
            vault_client.write('{0}/{1}'.format(request.user.pk, new_secret.label), 
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
def edit_secret(request, secret_id):
    """Edit an existing secret."""
    secret = get_object_or_404(Secret, id=secret_id)
    # check for private vault
    if secret.creator != request.user:
        raise Http404

    vault_data = vault_client.read('{0}/{1}'.format(request.user.pk, secret.label))
    if vault_data != None:
        secret.password = vault_data['data'].get('password', None)
        secret.config = vault_data['data'].get('config', None)

    if request.method != 'POST':
        form = SecretForm(instance=secret, initial={'confirm_password': secret.password})
    else:
        form = SecretForm(instance=secret, data=request.POST)
        if form.is_valid():
            secret = form.save(commit=False)
            vault_client.write('{0}/{1}'.format(request.user.pk, secret.label), 
                password=secret.password, 
                config=secret.config)
            
            secret.date_changed = datetime.now()
            secret.creator = request.user
            secret.password = ''
            secret.config = ''
            secret.save()
            return HttpResponseRedirect(reverse('manager:secret', args=[secret.id]))

    context = {'secret': secret, 'form': form}
    return render(request, 'manager/edit_secret.html', context)

@login_required
def delete_secret(request, secret_id):
    secret = get_object_or_404(Secret, id=secret_id)
    # check for private vault
    if secret.creator != request.user:
        raise Http404

    if request.method == "POST":
        vault_client.delete('{0}/{1}'.format(request.user.pk, secret.label))
        secret.delete()
        return HttpResponseRedirect(reverse('manager:secrets'))
    
    context = {'secret': secret}
    return render(request, 'manager/delete_secret.html', context)
    
