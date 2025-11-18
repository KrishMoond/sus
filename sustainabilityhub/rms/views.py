from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Report
# from django_ratelimit.decorators import ratelimit

@login_required
# @ratelimit(key='user', rate='5/h', method='POST')
def create_report(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        
        if category and subject and description:
            report = Report.objects.create(
                reporter=request.user,
                category=category,
                subject=subject,
                description=description
            )
            messages.success(request, f'Report #{report.id} submitted successfully. We will review it soon.')
            return redirect('rms:my_reports')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'rms/create.html')

@login_required
def my_reports(request):
    reports = Report.objects.filter(reporter=request.user)
    return render(request, 'rms/my_reports.html', {'reports': reports})

@user_passes_test(lambda u: u.is_superuser)
def admin_reports(request):
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'all':
        reports = Report.objects.all().order_by('-created_at')
    else:
        reports = Report.objects.filter(status=status_filter).order_by('-created_at')
    
    status_counts = {
        'pending': Report.objects.filter(status='pending').count(),
        'investigating': Report.objects.filter(status='investigating').count(),
        'resolved': Report.objects.filter(status='resolved').count(),
        'rejected': Report.objects.filter(status='rejected').count(),
    }
    
    return render(request, 'rms/admin_reports.html', {
        'reports': reports,
        'status_counts': status_counts,
        'current_status': status_filter
    })

@user_passes_test(lambda u: u.is_superuser)
def resolve_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    
    # Prevent editing resolved reports
    if report.status == 'resolved':
        messages.error(request, 'Cannot modify a resolved report.')
        return redirect('rms:admin_reports')
    
    if request.method == 'POST':
        old_status = report.status
        report.status = request.POST['status']
        report.admin_response = request.POST['response']
        report.resolved_by = request.user
        if report.status in ['resolved', 'rejected']:
            report.resolved_at = timezone.now()
        report.save()
        messages.success(request, f'Report moved from {old_status} to {report.status}.')
    
    # Redirect to current status view or pending if status changed
    redirect_status = request.POST.get('status', 'pending')
    return redirect(f'/reports/admin/?status={redirect_status}')

@login_required
# @ratelimit(key='user', rate='3/h', method='POST')
def submit_feedback(request):
    from .models import Feedback
    if request.method == 'POST':
        rating = request.POST.get('rating')
        message = request.POST.get('message')
        
        if rating and message:
            Feedback.objects.create(
                user=request.user,
                rating=int(rating),
                message=message
            )
            messages.success(request, 'Thank you for your feedback!')
            return redirect('home')
        else:
            messages.error(request, 'Please provide both rating and message.')
    
    return render(request, 'rms/feedback.html')

@user_passes_test(lambda u: u.is_superuser)
def view_feedbacks(request):
    from .models import Feedback
    feedbacks = Feedback.objects.all().select_related('user')
    return render(request, 'rms/view_feedbacks.html', {'feedbacks': feedbacks})