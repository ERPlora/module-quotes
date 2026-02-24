from django import forms
from django.utils.translation import gettext_lazy as _

from .models import QuoteSeries, QuoteSettings, Quote

class QuoteSeriesForm(forms.ModelForm):
    class Meta:
        model = QuoteSeries
        fields = ['name', 'prefix', 'next_number', 'is_default', 'is_active', 'number_digits']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'prefix': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'next_number': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'number_digits': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
        }

class QuoteSettingsForm(forms.ModelForm):
    class Meta:
        model = QuoteSettings
        fields = ['default_validity_days', 'default_series', 'default_notes', 'default_terms', 'tax_rate', 'show_tax', 'show_discount']
        widgets = {
            'default_validity_days': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'default_series': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'default_notes': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'default_terms': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'tax_rate': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'show_tax': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'show_discount': forms.CheckboxInput(attrs={'class': 'toggle'}),
        }

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['quote_number', 'series', 'title', 'customer', 'customer_name', 'customer_email', 'customer_phone', 'customer_address', 'related_lead', 'status', 'notes', 'terms', 'subtotal', 'discount_amount', 'discount_percent', 'tax_amount', 'tax_rate', 'total', 'valid_until', 'sent_at', 'accepted_at', 'rejected_at', 'converted_at', 'rejection_reason']
        widgets = {
            'quote_number': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'series': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'title': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'customer': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'customer_name': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'customer_email': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'email'}),
            'customer_phone': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'customer_address': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'related_lead': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'status': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'notes': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'terms': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'subtotal': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'discount_amount': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'discount_percent': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'tax_amount': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'tax_rate': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'total': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'valid_until': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'date'}),
            'sent_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'accepted_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'rejected_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'converted_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
        }

