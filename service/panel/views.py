from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from service.models import Services
from .forms import ServiceForm


def home(request):
    context = {
        'total': Services.objects.count(),
        'active': Services.objects.filter(status=Services.STATUS_ACTIVE).count(),
        'inactive': Services.objects.filter(status=Services.STATUS_INACTIVE).count(),
    }
    return render(request, 'home.html', context)


def service_list(request):
    services = Services.objects.all()

    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')

    if search:
        services = services.filter(service_name__icontains=search)
    if status in (Services.STATUS_ACTIVE, Services.STATUS_INACTIVE):
        services = services.filter(status=status)

    paginator = Paginator(services, settings.SERVICES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    # keep search & filter values when moving between pages
    params = request.GET.copy()
    params.pop('page', None)

    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'query_string': params.urlencode(),
        'total': paginator.count,
    }
    return render(request, 'service/service_list.html', context)


def service_detail(request, pk):
    service = get_object_or_404(Services, pk=pk)
    return render(request, 'service/service_detail.html', {'service': service})


def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.service_name}" added successfully.')
            return redirect('service_list')
    else:
        form = ServiceForm()

    return render(request, 'service/service_form.html', {'form': form, 'title': 'Add Service'})


def service_update(request, pk):
    service = get_object_or_404(Services, pk=pk)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f'Service "{service.service_name}" updated successfully.')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)

    context = {'form': form, 'title': 'Edit Service', 'service': service}
    return render(request, 'service/service_form.html', context)


def service_delete(request, pk):
    service = get_object_or_404(Services, pk=pk)

    if request.method == 'POST':
        name = service.service_name
        service.delete()
        messages.success(request, f'Service "{name}" deleted.')
        return redirect('service_list')

    return render(request, 'service/service_confirm_delete.html', {'service': service})
