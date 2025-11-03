from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from .forms import CustomUserCreationForm
from .models import UserWarning
from notifications.utils import create_notification

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin_users.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, f'User {username} created successfully.')
            return redirect('accounts:admin_users')
    
    return render(request, 'accounts/create_user.html')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'User {username} deleted successfully.')
    return redirect('accounts:admin_users')

@user_passes_test(lambda u: u.is_superuser)
def warn_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        warning = UserWarning.objects.create(
            user=user,
            issued_by=request.user,
            severity=request.POST['severity'],
            reason=request.POST['reason'],
            description=request.POST['description']
        )
        
        # Notify user about warning
        create_notification(
            recipient=user,
            notification_type='warning_issued',
            title=f'{warning.get_severity_display()} Warning',
            message=f'Reason: {warning.reason}',
            url='/accounts/my-warnings/'
        )
        
        messages.success(request, f'Warning issued to {user.username}.')
        return redirect('accounts:admin_users')
    
    return render(request, 'accounts/warn_user.html', {'target_user': user})

@user_passes_test(lambda u: u.is_superuser)
def user_warnings(request, pk):
    user = get_object_or_404(User, pk=pk)
    warnings = user.warnings.all()
    return render(request, 'accounts/user_warnings.html', {'target_user': user, 'warnings': warnings})