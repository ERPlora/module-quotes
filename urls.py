from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.quote_list, name='list'),
    path('add/', views.quote_add, name='add'),
    path('<uuid:quote_id>/', views.quote_detail, name='detail'),
    path('<uuid:quote_id>/edit/', views.quote_edit, name='edit'),
    path('<uuid:quote_id>/delete/', views.quote_delete, name='delete'),
    path('<uuid:quote_id>/send/', views.quote_send, name='send'),
    path('<uuid:quote_id>/accept/', views.quote_accept, name='accept'),
    path('<uuid:quote_id>/reject/', views.quote_reject, name='reject'),
    path('<uuid:quote_id>/duplicate/', views.quote_duplicate, name='duplicate'),
    path('<uuid:quote_id>/convert/', views.quote_convert, name='convert'),
    path('<uuid:quote_id>/lines/add/', views.quote_line_add, name='line_add'),
    path('<uuid:quote_id>/lines/<uuid:line_id>/edit/', views.quote_line_edit, name='line_edit'),
    path('<uuid:quote_id>/lines/<uuid:line_id>/delete/', views.quote_line_delete, name='line_delete'),
    path('series/', views.series_list, name='series'),
    path('series/add/', views.series_add, name='series_add'),
    path('series/<uuid:series_id>/edit/', views.series_edit, name='series_edit'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/save/', views.settings_save, name='settings_save'),
]
