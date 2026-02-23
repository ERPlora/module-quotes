from django.utils.translation import gettext_lazy as _

MODULE_ID = 'quotes'
MODULE_NAME = _('Quotes')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'document-text-outline'
MODULE_DESCRIPTION = _('Create and manage quotes, proposals and budgets')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'sales'

MENU = {
    'label': _('Quotes'),
    'icon': 'document-text-outline',
    'order': 20,
}

NAVIGATION = [
    {'id': 'dashboard', 'label': _('Dashboard'), 'icon': 'speedometer-outline', 'view': ''},
    {'id': 'list', 'label': _('Quotes'), 'icon': 'document-text-outline', 'view': 'list'},
    {'id': 'series', 'label': _('Series'), 'icon': 'layers-outline', 'view': 'series'},
    {'id': 'settings', 'label': _('Settings'), 'icon': 'settings-outline', 'view': 'settings'},
]

DEPENDENCIES = ['customers']

PERMISSIONS = [
    'quotes.view_quote',
    'quotes.add_quote',
    'quotes.change_quote',
    'quotes.delete_quote',
    'quotes.send_quote',
    'quotes.accept_quote',
    'quotes.convert_quote',
    'quotes.manage_settings',
]
