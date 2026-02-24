from django.contrib import admin

from .models import QuoteSeries, Quote, QuoteLine

@admin.register(QuoteSeries)
class QuoteSeriesAdmin(admin.ModelAdmin):
    list_display = ['name', 'prefix', 'next_number', 'is_default', 'is_active', 'created_at']
    search_fields = ['name', 'prefix']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'series', 'title', 'customer', 'customer_name', 'created_at']
    search_fields = ['quote_number', 'title', 'customer_name', 'customer_email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(QuoteLine)
class QuoteLineAdmin(admin.ModelAdmin):
    list_display = ['quote', 'line_type', 'product_id', 'service_id', 'description', 'created_at']
    search_fields = ['line_type', 'description']
    readonly_fields = ['created_at', 'updated_at']

