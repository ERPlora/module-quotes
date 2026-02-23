"""Quotes admin configuration."""

from django.contrib import admin
from .models import QuoteSeries, QuoteSettings, Quote, QuoteLine


@admin.register(QuoteSeries)
class QuoteSeriesAdmin(admin.ModelAdmin):
    list_display = ('prefix', 'name', 'next_number', 'is_default', 'is_active')
    list_filter = ('is_active', 'is_default')
    search_fields = ('prefix', 'name')


@admin.register(QuoteSettings)
class QuoteSettingsAdmin(admin.ModelAdmin):
    list_display = ('hub_id', 'default_validity_days', 'tax_rate')


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'customer_name', 'title', 'status', 'total', 'valid_until')
    list_filter = ('status',)
    search_fields = ('quote_number', 'customer_name', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(QuoteLine)
class QuoteLineAdmin(admin.ModelAdmin):
    list_display = ('quote', 'description', 'quantity', 'unit_price', 'total')
    list_filter = ('line_type',)
    search_fields = ('description',)
