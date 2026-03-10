"""
Quotes Module Views
"""
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render as django_render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.core.services import export_to_csv, export_to_excel
from apps.modules_runtime.navigation import with_module_nav

from .models import QuoteSeries, QuoteSettings, Quote, QuoteLine

PER_PAGE_CHOICES = [12, 24, 48, 96, 0]


# ======================================================================
# Dashboard
# ======================================================================

@login_required
@with_module_nav('quotes', 'dashboard')
@htmx_view('quotes/pages/index.html', 'quotes/partials/dashboard_content.html')
def dashboard(request):
    hub_id = request.session.get('hub_id')
    return {
        'total_quote_serieses': QuoteSeries.objects.filter(hub_id=hub_id, is_deleted=False).count(),
        'total_quotes': Quote.objects.filter(hub_id=hub_id, is_deleted=False).count(),
    }


# ======================================================================
# QuoteSeries
# ======================================================================

QUOTE_SERIES_SORT_FIELDS = {
    'name': 'name',
    'is_default': 'is_default',
    'is_active': 'is_active',
    'next_number': 'next_number',
    'prefix': 'prefix',
    'number_digits': 'number_digits',
    'created_at': 'created_at',
}

def _build_quote_serieses_context(hub_id, per_page=10):
    qs = QuoteSeries.objects.filter(hub_id=hub_id, is_deleted=False).order_by('name')
    paginator = Paginator(qs, per_page if per_page > 0 else max(qs.count(), 1))
    page_obj = paginator.get_page(1)
    return {
        'quote_serieses': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'name',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_quote_serieses_list(request, hub_id, per_page=10):
    ctx = _build_quote_serieses_context(hub_id, per_page)
    return django_render(request, 'quotes/partials/quote_serieses_list.html', ctx)

@login_required
@with_module_nav('quotes', 'list')
@htmx_view('quotes/pages/quote_serieses.html', 'quotes/partials/quote_serieses_content.html')
def quote_serieses_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'name')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 12))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 12

    qs = QuoteSeries.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(name__icontains=search_query) | Q(prefix__icontains=search_query))

    order_by = QUOTE_SERIES_SORT_FIELDS.get(sort_field, 'name')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['name', 'is_default', 'is_active', 'next_number', 'prefix', 'number_digits']
        headers = ['Name', 'Default Series', 'Active', 'Next Number', 'Prefix', 'Number Digits']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='quote_serieses.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='quote_serieses.xlsx')

    paginator = Paginator(qs, per_page if per_page > 0 else max(qs.count(), 1))
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'quotes/partials/quote_serieses_list.html', {
            'quote_serieses': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'quote_serieses': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
@htmx_view('quotes/pages/quote_series_add.html', 'quotes/partials/quote_series_add_content.html')
def quote_series_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        prefix = request.POST.get('prefix', '').strip()
        next_number = int(request.POST.get('next_number', 0) or 0)
        is_default = request.POST.get('is_default') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        number_digits = request.POST.get('number_digits', '').strip()
        obj = QuoteSeries(hub_id=hub_id)
        obj.name = name
        obj.prefix = prefix
        obj.next_number = next_number
        obj.is_default = is_default
        obj.is_active = is_active
        obj.number_digits = number_digits
        obj.save()
        response = HttpResponse(status=204)
        response['HX-Redirect'] = reverse('quotes:series')
        return response
    return {}

@login_required
@htmx_view('quotes/pages/quote_series_edit.html', 'quotes/partials/quote_series_edit_content.html')
def quote_series_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(QuoteSeries, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.name = request.POST.get('name', '').strip()
        obj.prefix = request.POST.get('prefix', '').strip()
        obj.next_number = int(request.POST.get('next_number', 0) or 0)
        obj.is_default = request.POST.get('is_default') == 'on'
        obj.is_active = request.POST.get('is_active') == 'on'
        obj.number_digits = request.POST.get('number_digits', '').strip()
        obj.save()
        return _render_quote_serieses_list(request, hub_id)
    return {'obj': obj}

@login_required
@require_POST
def quote_series_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(QuoteSeries, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_quote_serieses_list(request, hub_id)

@login_required
@require_POST
def quote_series_toggle_status(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(QuoteSeries, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_active = not obj.is_active
    obj.save(update_fields=['is_active', 'updated_at'])
    return _render_quote_serieses_list(request, hub_id)

@login_required
@require_POST
def quote_serieses_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = QuoteSeries.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'activate':
        qs.update(is_active=True)
    elif action == 'deactivate':
        qs.update(is_active=False)
    elif action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_quote_serieses_list(request, hub_id)


# ======================================================================
# Quote
# ======================================================================

QUOTE_SORT_FIELDS = {
    'title': 'title',
    'quote_number': 'quote_number',
    'series': 'series',
    'customer': 'customer',
    'status': 'status',
    'total': 'total',
    'created_at': 'created_at',
}

def _build_quotes_context(hub_id, per_page=10):
    qs = Quote.objects.filter(hub_id=hub_id, is_deleted=False).order_by('title')
    paginator = Paginator(qs, per_page if per_page > 0 else max(qs.count(), 1))
    page_obj = paginator.get_page(1)
    return {
        'quotes': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'title',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_quotes_list(request, hub_id, per_page=10):
    ctx = _build_quotes_context(hub_id, per_page)
    return django_render(request, 'quotes/partials/quotes_list.html', ctx)

@login_required
@with_module_nav('quotes', 'list')
@htmx_view('quotes/pages/quotes.html', 'quotes/partials/quotes_content.html')
def quotes_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'title')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 12))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 12

    qs = Quote.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(quote_number__icontains=search_query) | Q(title__icontains=search_query) | Q(customer_name__icontains=search_query) | Q(customer_email__icontains=search_query))

    order_by = QUOTE_SORT_FIELDS.get(sort_field, 'title')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['title', 'quote_number', 'series', 'customer', 'status', 'total']
        headers = ['Title', 'Quote Number', "Name(id='QuoteSeries', ctx=Load())", 'customers.Customer', 'Status', 'Total']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='quotes.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='quotes.xlsx')

    paginator = Paginator(qs, per_page if per_page > 0 else max(qs.count(), 1))
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'quotes/partials/quotes_list.html', {
            'quotes': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'quotes': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
@htmx_view('quotes/pages/quote_add.html', 'quotes/partials/quote_add_content.html')
def quote_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        quote_number = request.POST.get('quote_number', '').strip()
        title = request.POST.get('title', '').strip()
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        customer_address = request.POST.get('customer_address', '').strip()
        related_lead = request.POST.get('related_lead', '').strip()
        status = request.POST.get('status', '').strip()
        notes = request.POST.get('notes', '').strip()
        terms = request.POST.get('terms', '').strip()
        subtotal = request.POST.get('subtotal', '0') or '0'
        discount_amount = request.POST.get('discount_amount', '0') or '0'
        discount_percent = request.POST.get('discount_percent', '0') or '0'
        tax_amount = request.POST.get('tax_amount', '0') or '0'
        tax_rate = request.POST.get('tax_rate', '0') or '0'
        total = request.POST.get('total', '0') or '0'
        valid_until = request.POST.get('valid_until') or None
        sent_at = request.POST.get('sent_at') or None
        accepted_at = request.POST.get('accepted_at') or None
        rejected_at = request.POST.get('rejected_at') or None
        converted_at = request.POST.get('converted_at') or None
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        obj = Quote(hub_id=hub_id)
        obj.quote_number = quote_number
        obj.title = title
        obj.customer_name = customer_name
        obj.customer_email = customer_email
        obj.customer_phone = customer_phone
        obj.customer_address = customer_address
        obj.related_lead = related_lead
        obj.status = status
        obj.notes = notes
        obj.terms = terms
        obj.subtotal = subtotal
        obj.discount_amount = discount_amount
        obj.discount_percent = discount_percent
        obj.tax_amount = tax_amount
        obj.tax_rate = tax_rate
        obj.total = total
        obj.valid_until = valid_until
        obj.sent_at = sent_at
        obj.accepted_at = accepted_at
        obj.rejected_at = rejected_at
        obj.converted_at = converted_at
        obj.rejection_reason = rejection_reason
        obj.save()
        return _render_quotes_list(request, hub_id)
    return {}

@login_required
@htmx_view('quotes/pages/quote_edit.html', 'quotes/partials/quote_edit_content.html')
def quote_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Quote, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.quote_number = request.POST.get('quote_number', '').strip()
        obj.title = request.POST.get('title', '').strip()
        obj.customer_name = request.POST.get('customer_name', '').strip()
        obj.customer_email = request.POST.get('customer_email', '').strip()
        obj.customer_phone = request.POST.get('customer_phone', '').strip()
        obj.customer_address = request.POST.get('customer_address', '').strip()
        obj.related_lead = request.POST.get('related_lead', '').strip()
        obj.status = request.POST.get('status', '').strip()
        obj.notes = request.POST.get('notes', '').strip()
        obj.terms = request.POST.get('terms', '').strip()
        obj.subtotal = request.POST.get('subtotal', '0') or '0'
        obj.discount_amount = request.POST.get('discount_amount', '0') or '0'
        obj.discount_percent = request.POST.get('discount_percent', '0') or '0'
        obj.tax_amount = request.POST.get('tax_amount', '0') or '0'
        obj.tax_rate = request.POST.get('tax_rate', '0') or '0'
        obj.total = request.POST.get('total', '0') or '0'
        obj.valid_until = request.POST.get('valid_until') or None
        obj.sent_at = request.POST.get('sent_at') or None
        obj.accepted_at = request.POST.get('accepted_at') or None
        obj.rejected_at = request.POST.get('rejected_at') or None
        obj.converted_at = request.POST.get('converted_at') or None
        obj.rejection_reason = request.POST.get('rejection_reason', '').strip()
        obj.save()
        return _render_quotes_list(request, hub_id)
    return {'obj': obj}

@login_required
@require_POST
def quote_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Quote, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_quotes_list(request, hub_id)

@login_required
@require_POST
def quotes_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = Quote.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_quotes_list(request, hub_id)


# ======================================================================
# Settings
# ======================================================================

@login_required
@permission_required('quotes.manage_settings')
@with_module_nav('quotes', 'settings')
@htmx_view('quotes/pages/settings.html', 'quotes/partials/settings_content.html')
def settings_view(request):
    hub_id = request.session.get('hub_id')
    config, _ = QuoteSettings.objects.get_or_create(hub_id=hub_id)
    if request.method == 'POST':
        config.default_validity_days = request.POST.get('default_validity_days', config.default_validity_days)
        config.default_series = request.POST.get('default_series', '').strip()
        config.default_notes = request.POST.get('default_notes', '').strip()
        config.default_terms = request.POST.get('default_terms', '').strip()
        config.tax_rate = request.POST.get('tax_rate', config.tax_rate)
        config.show_tax = request.POST.get('show_tax') == 'on'
        config.show_discount = request.POST.get('show_discount') == 'on'
        config.save()
    return {'config': config}

