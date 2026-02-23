"""Quotes forms."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import QuoteSeries, QuoteSettings, Quote, QuoteLine


class QuoteSeriesForm(forms.ModelForm):
    class Meta:
        model = QuoteSeries
        fields = [
            'name', 'prefix', 'number_digits',
            'is_active', 'is_default',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('e.g. Standard Quotes'),
            }),
            'prefix': forms.TextInput(attrs={
                'class': 'input', 'style': 'text-transform:uppercase',
                'placeholder': 'QT', 'maxlength': '10',
            }),
            'number_digits': forms.NumberInput(attrs={
                'class': 'input', 'min': '1', 'max': '10',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'toggle'}),
        }


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = [
            'title', 'series', 'customer', 'customer_name',
            'customer_email', 'customer_phone', 'customer_address',
            'notes', 'terms', 'valid_until',
            'discount_percent', 'tax_rate',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('Quote title'),
            }),
            'series': forms.Select(attrs={'class': 'select'}),
            'customer': forms.HiddenInput(),
            'customer_name': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('Customer name'),
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'input', 'placeholder': _('customer@example.com'),
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('+34 600 000 000'),
            }),
            'customer_address': forms.Textarea(attrs={
                'class': 'textarea', 'rows': 2,
                'placeholder': _('Street, City, Postal Code'),
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea', 'rows': 3,
                'placeholder': _('Additional notes for the customer'),
            }),
            'terms': forms.Textarea(attrs={
                'class': 'textarea', 'rows': 3,
                'placeholder': _('Terms and conditions'),
            }),
            'valid_until': forms.DateInput(attrs={
                'class': 'input', 'type': 'date',
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'input', 'step': '0.01', 'min': '0', 'max': '100',
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'input', 'step': '0.01', 'min': '0',
            }),
        }


class QuoteLineForm(forms.ModelForm):
    class Meta:
        model = QuoteLine
        fields = [
            'line_type', 'description', 'quantity',
            'unit_price', 'discount_percent', 'tax_rate', 'sort_order',
        ]
        widgets = {
            'line_type': forms.Select(attrs={'class': 'select'}),
            'description': forms.TextInput(attrs={
                'class': 'input', 'placeholder': _('Item description'),
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'input', 'step': '0.001', 'min': '0.001',
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'input', 'step': '0.01', 'min': '0',
            }),
            'discount_percent': forms.NumberInput(attrs={
                'class': 'input', 'step': '0.01', 'min': '0', 'max': '100',
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'input', 'step': '0.01', 'min': '0',
            }),
            'sort_order': forms.HiddenInput(),
        }


class QuoteSettingsForm(forms.ModelForm):
    class Meta:
        model = QuoteSettings
        fields = [
            'default_validity_days', 'default_series',
            'default_notes', 'default_terms',
            'tax_rate', 'show_tax', 'show_discount',
        ]
        widgets = {
            'default_validity_days': forms.NumberInput(attrs={
                'class': 'input', 'min': '1', 'max': '365',
            }),
            'default_series': forms.Select(attrs={'class': 'select'}),
            'default_notes': forms.Textarea(attrs={
                'class': 'textarea', 'rows': 3,
                'placeholder': _('Default notes for new quotes'),
            }),
            'default_terms': forms.Textarea(attrs={
                'class': 'textarea', 'rows': 3,
                'placeholder': _('Default terms and conditions'),
            }),
            'tax_rate': forms.NumberInput(attrs={
                'class': 'input', 'step': '0.01', 'min': '0',
            }),
            'show_tax': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'show_discount': forms.CheckboxInput(attrs={'class': 'toggle'}),
        }

    def __init__(self, *args, hub_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if hub_id:
            self.fields['default_series'].queryset = QuoteSeries.objects.filter(
                hub_id=hub_id, is_deleted=False, is_active=True,
            )
