from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # QuoteSeries
    path('quote_serieses/', views.quote_serieses_list, name='quote_serieses_list'),
    path('quote_serieses/add/', views.quote_series_add, name='quote_series_add'),
    path('quote_serieses/<uuid:pk>/edit/', views.quote_series_edit, name='quote_series_edit'),
    path('quote_serieses/<uuid:pk>/delete/', views.quote_series_delete, name='quote_series_delete'),
    path('quote_serieses/<uuid:pk>/toggle/', views.quote_series_toggle_status, name='quote_series_toggle_status'),
    path('quote_serieses/bulk/', views.quote_serieses_bulk_action, name='quote_serieses_bulk_action'),

    # Quote
    path('quotes/', views.quotes_list, name='quotes_list'),
    path('quotes/add/', views.quote_add, name='quote_add'),
    path('quotes/<uuid:pk>/edit/', views.quote_edit, name='quote_edit'),
    path('quotes/<uuid:pk>/delete/', views.quote_delete, name='quote_delete'),
    path('quotes/bulk/', views.quotes_bulk_action, name='quotes_bulk_action'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
