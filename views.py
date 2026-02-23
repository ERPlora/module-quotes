"""Quotes views."""

from datetime import date, timedelta
from decimal import Decimal

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render as django_render
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum, Count
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib import messages

from apps.accounts.decorators import login_required
from apps.core.htmx import htmx_view, htmx_redirect
from apps.modules_runtime.navigation import with_module_nav

from .models import QuoteSeries, QuoteSettings, Quote, QuoteLine
from .forms import QuoteSeriesForm, QuoteForm, QuoteLineForm, QuoteSettingsForm


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PER_PAGE_CHOICES = [10, 25, 50, 100]

QUOTE_SORT_FIELDS = {
    'number': 'quote_number',
    'customer': 'customer_name',
    'total': 'total',
    'date': 'created_at',
    'valid': 'valid_until',
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hub(request):
    return request.session.get('hub_id')


def _employee(request):
    from apps.accounts.models import LocalUser
    uid = request.session.get('local_user_id')
    if uid:
        return LocalUser.objects.filter(pk=uid).first()
    return None


def _render_quotes_list(request, hub):
    """Re-render the quotes table partial after a mutation."""
    quotes = Quote.objects.filter(hub_id=hub, is_deleted=False).order_by('-created_at')
    paginator = Paginator(quotes, 10)
    page_obj = paginator.get_page(1)
    return django_render(request, 'quotes/partials/quotes_list.html', {
        'quotes': page_obj,
        'page_obj': page_obj,
        'search': '',
        'sort_field': 'date',
        'sort_dir': 'desc',
        'status_filter': '',
        'series_filter': '',
        'per_page': 10,
    })


def _render_series_list(request, hub):
    """Re-render the series table partial after a mutation."""
    series = QuoteSeries.objects.filter(
        hub_id=hub, is_deleted=False,
    ).annotate(
        quote_count=Count(
            'quote', filter=Q(quote__is_deleted=False),
        ),
    ).order_by('prefix')
    return django_render(request, 'quotes/partials/series_content.html', {
        'series_list': series,
    })


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
@with_module_nav('quotes', 'dashboard')
@htmx_view('quotes/pages/dashboard.html', 'quotes/partials/dashboard_content.html')
def dashboard(request):
    hub = _hub(request)
    quotes = Quote.objects.filter(hub_id=hub, is_deleted=False)

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Monthly stats
    monthly_qs = quotes.filter(created_at__gte=month_start)
    monthly_total = monthly_qs.count()

    # Sent & awaiting
    sent_count = quotes.filter(status='sent').count()

    # Accepted
    accepted_qs = quotes.filter(status='accepted')
    accepted_count = accepted_qs.count()
    accepted_value = accepted_qs.aggregate(
        total=Sum('total'),
    )['total'] or Decimal('0.00')

    # Rejected
    rejected_count = quotes.filter(status='rejected').count()

    # Acceptance rate
    decided = accepted_count + rejected_count
    acceptance_rate = round((accepted_count / decided * 100), 1) if decided > 0 else 0

    # Expiring soon (next 7 days)
    today = date.today()
    expiring_soon = quotes.filter(
        status='sent',
        valid_until__gte=today,
        valid_until__lte=today + timedelta(days=7),
    ).count()

    # Draft count
    draft_count = quotes.filter(status='draft').count()

    # Converted count
    converted_count = quotes.filter(status='converted').count()

    # Recent quotes
    recent_quotes = quotes.order_by('-created_at')[:10]

    return {
        'monthly_total': monthly_total,
        'sent_count': sent_count,
        'accepted_count': accepted_count,
        'accepted_value': accepted_value,
        'rejected_count': rejected_count,
        'acceptance_rate': acceptance_rate,
        'expiring_soon': expiring_soon,
        'draft_count': draft_count,
        'converted_count': converted_count,
        'recent_quotes': recent_quotes,
    }


# ---------------------------------------------------------------------------
# Quotes List
# ---------------------------------------------------------------------------

@login_required
@with_module_nav('quotes', 'list')
@htmx_view('quotes/pages/list.html', 'quotes/partials/quotes_content.html')
def quote_list(request):
    hub = _hub(request)
    qs = Quote.objects.filter(hub_id=hub, is_deleted=False)

    # --- Search ---
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(quote_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(title__icontains=search)
        )

    # --- Filters ---
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    series_filter = request.GET.get('series', '')
    if series_filter:
        qs = qs.filter(series_id=series_filter)

    # --- Sort ---
    sort_field = request.GET.get('sort', 'date')
    sort_dir = request.GET.get('dir', 'desc')
    order_by = QUOTE_SORT_FIELDS.get(sort_field, 'created_at')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    # --- Pagination ---
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10
    page_number = request.GET.get('page', 1)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    # Series for filter dropdown
    series_list = QuoteSeries.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    ).order_by('prefix')

    context = {
        'quotes': page_obj,
        'page_obj': page_obj,
        'search': search,
        'sort_field': sort_field,
        'sort_dir': sort_dir,
        'status_filter': status_filter,
        'series_filter': series_filter,
        'series_list': series_list,
        'per_page': per_page,
    }

    # HTMX partial: swap only datatable body
    if request.headers.get('HX-Request') and request.headers.get('HX-Target') == 'datatable-body':
        return django_render(request, 'quotes/partials/quotes_list.html', context)

    return context


# ---------------------------------------------------------------------------
# Quote Add
# ---------------------------------------------------------------------------

@login_required
@with_module_nav('quotes', 'list')
@htmx_view('quotes/pages/list.html', 'quotes/partials/panel_quote_add.html')
def quote_add(request):
    hub = _hub(request)
    settings = QuoteSettings.get_settings(hub)

    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.hub_id = hub
            quote.created_by = request.session.get('local_user_id')

            # Denormalize customer info if customer FK set
            if quote.customer:
                if not quote.customer_name:
                    quote.customer_name = quote.customer.name
                if not quote.customer_email:
                    quote.customer_email = quote.customer.email or ''
                if not quote.customer_phone:
                    quote.customer_phone = quote.customer.phone or ''
                if not quote.customer_address:
                    parts = [
                        quote.customer.address,
                        quote.customer.city,
                        quote.customer.postal_code,
                    ]
                    quote.customer_address = ', '.join(p for p in parts if p)

            # Apply defaults
            if not quote.notes and settings.default_notes:
                quote.notes = settings.default_notes
            if not quote.terms and settings.default_terms:
                quote.terms = settings.default_terms
            if not quote.valid_until:
                quote.valid_until = date.today() + timedelta(days=settings.default_validity_days)

            quote.save()
            return htmx_redirect(f'/m/quotes/{quote.pk}/')

        return django_render(request, 'quotes/partials/panel_quote_add.html', {
            'form': form,
            'series_list': QuoteSeries.objects.filter(
                hub_id=hub, is_deleted=False, is_active=True,
            ),
            'settings': settings,
            'errors': form.errors,
        })

    # GET — render add form
    series_list = QuoteSeries.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    )
    default_series = settings.default_series or series_list.filter(is_default=True).first()

    form = QuoteForm(initial={
        'series': default_series,
        'tax_rate': settings.tax_rate,
        'notes': settings.default_notes,
        'terms': settings.default_terms,
        'valid_until': date.today() + timedelta(days=settings.default_validity_days),
    })
    form.fields['series'].queryset = series_list

    return {
        'form': form,
        'series_list': series_list,
        'settings': settings,
    }


# ---------------------------------------------------------------------------
# Quote Detail
# ---------------------------------------------------------------------------

@login_required
@with_module_nav('quotes', 'list')
@htmx_view('quotes/pages/detail.html', 'quotes/partials/detail_content.html')
def quote_detail(request, quote_id):
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False,
    ).select_related('series', 'customer').first()

    if not quote:
        return {'error': _('Quote not found')}

    lines = QuoteLine.objects.filter(
        quote=quote, is_deleted=False,
    ).order_by('sort_order', 'created_at')

    return {
        'quote': quote,
        'lines': lines,
    }


# ---------------------------------------------------------------------------
# Quote Edit
# ---------------------------------------------------------------------------

@login_required
@with_module_nav('quotes', 'list')
@htmx_view('quotes/pages/detail.html', 'quotes/partials/panel_quote_edit.html')
def quote_edit(request, quote_id):
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False,
    ).first()

    if not quote:
        return {'error': _('Quote not found')}

    if quote.status not in ('draft', 'sent'):
        return {'error': _('Only draft or sent quotes can be edited')}

    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        if form.is_valid():
            q = form.save(commit=False)
            q.updated_by = request.session.get('local_user_id')
            q.save()
            q.calculate_totals()
            q.save(update_fields=[
                'subtotal', 'discount_amount', 'tax_amount', 'total', 'updated_at',
            ])
            return htmx_redirect(f'/m/quotes/{quote.pk}/')

        series_list = QuoteSeries.objects.filter(
            hub_id=hub, is_deleted=False, is_active=True,
        )
        return django_render(request, 'quotes/partials/panel_quote_edit.html', {
            'form': form,
            'quote': quote,
            'series_list': series_list,
            'errors': form.errors,
        })

    series_list = QuoteSeries.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    )
    form = QuoteForm(instance=quote)
    form.fields['series'].queryset = series_list

    return {
        'form': form,
        'quote': quote,
        'series_list': series_list,
    }


# ---------------------------------------------------------------------------
# Quote Delete
# ---------------------------------------------------------------------------

@login_required
@require_POST
def quote_delete(request, quote_id):
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False,
    ).first()

    if not quote:
        return JsonResponse({'ok': False}, status=404)

    if quote.status not in ('draft',):
        messages.error(request, _('Only draft quotes can be deleted'))
        return _render_quotes_list(request, hub)

    quote.is_deleted = True
    quote.deleted_at = timezone.now()
    quote.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    messages.success(request, _('Quote deleted successfully'))
    return _render_quotes_list(request, hub)


# ---------------------------------------------------------------------------
# Quote Status Actions
# ---------------------------------------------------------------------------

@login_required
@require_POST
def quote_send(request, quote_id):
    """Mark quote as sent."""
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False, status='draft',
    ).select_related('series').first()

    if not quote:
        return JsonResponse({
            'ok': False,
            'error': _('Quote not found or not a draft'),
        }, status=400)

    success = quote.mark_sent()
    if not success:
        return JsonResponse({
            'ok': False,
            'error': _('Could not mark quote as sent'),
        }, status=400)

    return JsonResponse({'ok': True, 'number': quote.quote_number})


@login_required
@require_POST
def quote_accept(request, quote_id):
    """Mark quote as accepted."""
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False, status='sent',
    ).first()

    if not quote:
        return JsonResponse({
            'ok': False,
            'error': _('Quote not found or not in sent status'),
        }, status=400)

    success = quote.mark_accepted()
    if not success:
        return JsonResponse({
            'ok': False,
            'error': _('Could not accept quote'),
        }, status=400)

    return JsonResponse({'ok': True})


@login_required
@require_POST
def quote_reject(request, quote_id):
    """Mark quote as rejected."""
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False, status='sent',
    ).first()

    if not quote:
        return JsonResponse({
            'ok': False,
            'error': _('Quote not found or not in sent status'),
        }, status=400)

    reason = request.POST.get('reason', '')
    success = quote.mark_rejected(reason=reason)
    if not success:
        return JsonResponse({
            'ok': False,
            'error': _('Could not reject quote'),
        }, status=400)

    return JsonResponse({'ok': True})


# ---------------------------------------------------------------------------
# Quote Duplicate
# ---------------------------------------------------------------------------

@login_required
@require_POST
def quote_duplicate(request, quote_id):
    """Duplicate an existing quote as a new draft."""
    hub = _hub(request)
    original = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False,
    ).first()

    if not original:
        return JsonResponse({'ok': False, 'error': _('Quote not found')}, status=404)

    settings = QuoteSettings.get_settings(hub)

    # Create new quote with same data
    new_quote = Quote(
        hub_id=hub,
        series=original.series,
        title=_('Copy of %(title)s') % {'title': original.title} if original.title else '',
        customer=original.customer,
        customer_name=original.customer_name,
        customer_email=original.customer_email,
        customer_phone=original.customer_phone,
        customer_address=original.customer_address,
        status='draft',
        notes=original.notes,
        terms=original.terms,
        discount_percent=original.discount_percent,
        tax_rate=original.tax_rate,
        valid_until=date.today() + timedelta(days=settings.default_validity_days),
        created_by=request.session.get('local_user_id'),
    )
    new_quote.save()

    # Duplicate lines
    original_lines = QuoteLine.objects.filter(
        quote=original, is_deleted=False,
    ).order_by('sort_order')

    for line in original_lines:
        QuoteLine.objects.create(
            hub_id=hub,
            quote=new_quote,
            line_type=line.line_type,
            product_id=line.product_id,
            service_id=line.service_id,
            description=line.description,
            quantity=line.quantity,
            unit_price=line.unit_price,
            discount_percent=line.discount_percent,
            tax_rate=line.tax_rate,
            sort_order=line.sort_order,
        )

    # Recalculate totals
    new_quote.calculate_totals()
    new_quote.save(update_fields=[
        'subtotal', 'discount_amount', 'tax_amount', 'total', 'updated_at',
    ])

    return JsonResponse({'ok': True, 'id': str(new_quote.pk)})


# ---------------------------------------------------------------------------
# Quote Convert
# ---------------------------------------------------------------------------

@login_required
@require_POST
def quote_convert(request, quote_id):
    """Mark an accepted quote as converted."""
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False, status='accepted',
    ).first()

    if not quote:
        return JsonResponse({
            'ok': False,
            'error': _('Quote not found or not in accepted status'),
        }, status=400)

    success = quote.mark_converted()
    if not success:
        return JsonResponse({
            'ok': False,
            'error': _('Could not convert quote'),
        }, status=400)

    return JsonResponse({'ok': True, 'quote_id': str(quote.pk)})


# ---------------------------------------------------------------------------
# Quote Lines
# ---------------------------------------------------------------------------

@login_required
@require_POST
def quote_line_add(request, quote_id):
    """Add a line item to a quote."""
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False,
    ).first()

    if not quote:
        return JsonResponse({'ok': False, 'error': _('Quote not found')}, status=404)

    if quote.status not in ('draft', 'sent'):
        return JsonResponse({
            'ok': False,
            'error': _('Cannot modify lines on this quote'),
        }, status=400)

    form = QuoteLineForm(request.POST)
    if form.is_valid():
        line = form.save(commit=False)
        line.hub_id = hub
        line.quote = quote
        # Auto-set sort order if not provided
        if not line.sort_order:
            max_order = QuoteLine.objects.filter(
                quote=quote, is_deleted=False,
            ).order_by('-sort_order').values_list('sort_order', flat=True).first() or 0
            line.sort_order = max_order + 1
        line.save()

        # Recalculate quote totals
        quote.calculate_totals()
        quote.save(update_fields=[
            'subtotal', 'discount_amount', 'tax_amount', 'total', 'updated_at',
        ])

        # Return updated lines partial
        lines = QuoteLine.objects.filter(
            quote=quote, is_deleted=False,
        ).order_by('sort_order', 'created_at')
        return django_render(request, 'quotes/partials/quote_lines.html', {
            'quote': quote,
            'lines': lines,
        })

    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def quote_line_edit(request, quote_id, line_id):
    """Edit a line item."""
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False,
    ).first()

    if not quote:
        return JsonResponse({'ok': False, 'error': _('Quote not found')}, status=404)

    if quote.status not in ('draft', 'sent'):
        return JsonResponse({
            'ok': False,
            'error': _('Cannot modify lines on this quote'),
        }, status=400)

    line = QuoteLine.objects.filter(
        pk=line_id, quote=quote, is_deleted=False,
    ).first()

    if not line:
        return JsonResponse({'ok': False, 'error': _('Line not found')}, status=404)

    form = QuoteLineForm(request.POST, instance=line)
    if form.is_valid():
        form.save()

        # Recalculate quote totals
        quote.calculate_totals()
        quote.save(update_fields=[
            'subtotal', 'discount_amount', 'tax_amount', 'total', 'updated_at',
        ])

        lines = QuoteLine.objects.filter(
            quote=quote, is_deleted=False,
        ).order_by('sort_order', 'created_at')
        return django_render(request, 'quotes/partials/quote_lines.html', {
            'quote': quote,
            'lines': lines,
        })

    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def quote_line_delete(request, quote_id, line_id):
    """Delete a line item from a quote."""
    hub = _hub(request)
    quote = Quote.objects.filter(
        pk=quote_id, hub_id=hub, is_deleted=False,
    ).first()

    if not quote:
        return JsonResponse({'ok': False, 'error': _('Quote not found')}, status=404)

    if quote.status not in ('draft', 'sent'):
        return JsonResponse({
            'ok': False,
            'error': _('Cannot modify lines on this quote'),
        }, status=400)

    line = QuoteLine.objects.filter(
        pk=line_id, quote=quote, is_deleted=False,
    ).first()

    if not line:
        return JsonResponse({'ok': False, 'error': _('Line not found')}, status=404)

    line.is_deleted = True
    line.deleted_at = timezone.now()
    line.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    # Recalculate quote totals
    quote.calculate_totals()
    quote.save(update_fields=[
        'subtotal', 'discount_amount', 'tax_amount', 'total', 'updated_at',
    ])

    lines = QuoteLine.objects.filter(
        quote=quote, is_deleted=False,
    ).order_by('sort_order', 'created_at')
    return django_render(request, 'quotes/partials/quote_lines.html', {
        'quote': quote,
        'lines': lines,
    })


# ---------------------------------------------------------------------------
# Series
# ---------------------------------------------------------------------------

@login_required
@with_module_nav('quotes', 'series')
@htmx_view('quotes/pages/series.html', 'quotes/partials/series_content.html')
def series_list(request):
    hub = _hub(request)
    series = QuoteSeries.objects.filter(
        hub_id=hub, is_deleted=False,
    ).annotate(
        quote_count=Count(
            'quote', filter=Q(quote__is_deleted=False),
        ),
    ).order_by('prefix')

    return {'series_list': series}


@login_required
@require_POST
def series_add(request):
    hub = _hub(request)
    form = QuoteSeriesForm(request.POST)
    if form.is_valid():
        series = form.save(commit=False)
        series.hub_id = hub
        series.save()
        messages.success(request, _('Series created successfully'))
        return _render_series_list(request, hub)
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def series_edit(request, series_id):
    hub = _hub(request)
    series = QuoteSeries.objects.filter(
        pk=series_id, hub_id=hub, is_deleted=False,
    ).first()

    if not series:
        return JsonResponse({'ok': False, 'error': _('Series not found')}, status=404)

    form = QuoteSeriesForm(request.POST, instance=series)
    if form.is_valid():
        form.save()
        messages.success(request, _('Series updated successfully'))
        return _render_series_list(request, hub)
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@login_required
@with_module_nav('quotes', 'settings')
@htmx_view('quotes/pages/settings.html', 'quotes/partials/settings_content.html')
def settings_view(request):
    hub = _hub(request)
    settings_obj = QuoteSettings.get_settings(hub)
    series_list = QuoteSeries.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    )
    return {
        'settings': settings_obj,
        'series_list': series_list,
    }


@login_required
@require_POST
def settings_save(request):
    """Save a single setting field via HTMX."""
    hub = _hub(request)
    settings_obj = QuoteSettings.get_settings(hub)
    field = request.POST.get('field')
    value = request.POST.get('value', '')

    text_fields = {
        'default_notes', 'default_terms',
    }
    number_fields = {
        'default_validity_days': int,
        'tax_rate': Decimal,
    }
    toggle_fields = {
        'show_tax', 'show_discount',
    }
    fk_fields = {
        'default_series',
    }

    if field in text_fields:
        setattr(settings_obj, field, value)
        settings_obj.save(update_fields=[field, 'updated_at'])
        return JsonResponse({'ok': True})

    elif field in number_fields:
        try:
            cast_fn = number_fields[field]
            setattr(settings_obj, field, cast_fn(value))
            settings_obj.save(update_fields=[field, 'updated_at'])
            return JsonResponse({'ok': True})
        except (ValueError, TypeError):
            return JsonResponse({'ok': False, 'error': _('Invalid value')}, status=400)

    elif field in toggle_fields:
        current = getattr(settings_obj, field)
        setattr(settings_obj, field, not current)
        settings_obj.save(update_fields=[field, 'updated_at'])
        return JsonResponse({'ok': True, 'value': not current})

    elif field in fk_fields:
        if field == 'default_series':
            if value:
                series = QuoteSeries.objects.filter(
                    pk=value, hub_id=hub, is_deleted=False,
                ).first()
                settings_obj.default_series = series
            else:
                settings_obj.default_series = None
            settings_obj.save(update_fields=['default_series', 'updated_at'])
            return JsonResponse({'ok': True})

    return JsonResponse({'ok': False, 'error': _('Invalid field')}, status=400)
