"""Tests for quotes views."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboard:
    """Dashboard view tests."""

    def test_dashboard_loads(self, auth_client):
        """Test dashboard page loads."""
        url = reverse('quotes:dashboard')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_dashboard_htmx(self, auth_client):
        """Test dashboard HTMX partial."""
        url = reverse('quotes:dashboard')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication."""
        url = reverse('quotes:dashboard')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestQuoteSeriesViews:
    """QuoteSeries view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('quotes:quote_serieses_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('quotes:quote_serieses_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('quotes:quote_serieses_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('quotes:quote_serieses_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('quotes:quote_serieses_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('quotes:quote_serieses_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('quotes:quote_series_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('quotes:quote_series_add')
        data = {
            'name': 'New Name',
            'prefix': 'New Prefix',
            'next_number': '5',
            'is_default': 'on',
            'is_active': 'on',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, quote_series):
        """Test edit form loads."""
        url = reverse('quotes:quote_series_edit', args=[quote_series.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, quote_series):
        """Test editing via POST."""
        url = reverse('quotes:quote_series_edit', args=[quote_series.pk])
        data = {
            'name': 'Updated Name',
            'prefix': 'Updated Prefix',
            'next_number': '5',
            'is_default': '',
            'is_active': '',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, quote_series):
        """Test soft delete via POST."""
        url = reverse('quotes:quote_series_delete', args=[quote_series.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        quote_series.refresh_from_db()
        assert quote_series.is_deleted is True

    def test_toggle_status(self, auth_client, quote_series):
        """Test toggle active status."""
        url = reverse('quotes:quote_series_toggle_status', args=[quote_series.pk])
        original = quote_series.is_active
        response = auth_client.post(url)
        assert response.status_code == 200
        quote_series.refresh_from_db()
        assert quote_series.is_active != original

    def test_bulk_delete(self, auth_client, quote_series):
        """Test bulk delete."""
        url = reverse('quotes:quote_serieses_bulk_action')
        response = auth_client.post(url, {'ids': str(quote_series.pk), 'action': 'delete'})
        assert response.status_code == 200
        quote_series.refresh_from_db()
        assert quote_series.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('quotes:quote_serieses_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestQuoteViews:
    """Quote view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('quotes:quotes_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('quotes:quotes_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('quotes:quotes_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('quotes:quotes_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('quotes:quotes_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('quotes:quotes_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('quotes:quote_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('quotes:quote_add')
        data = {
            'quote_number': 'New Quote Number',
            'title': 'New Title',
            'customer_name': 'New Customer Name',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, quote):
        """Test edit form loads."""
        url = reverse('quotes:quote_edit', args=[quote.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, quote):
        """Test editing via POST."""
        url = reverse('quotes:quote_edit', args=[quote.pk])
        data = {
            'quote_number': 'Updated Quote Number',
            'title': 'Updated Title',
            'customer_name': 'Updated Customer Name',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, quote):
        """Test soft delete via POST."""
        url = reverse('quotes:quote_delete', args=[quote.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        quote.refresh_from_db()
        assert quote.is_deleted is True

    def test_bulk_delete(self, auth_client, quote):
        """Test bulk delete."""
        url = reverse('quotes:quotes_bulk_action')
        response = auth_client.post(url, {'ids': str(quote.pk), 'action': 'delete'})
        assert response.status_code == 200
        quote.refresh_from_db()
        assert quote.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('quotes:quotes_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestSettings:
    """Settings view tests."""

    def test_settings_loads(self, auth_client):
        """Test settings page loads."""
        url = reverse('quotes:settings')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_settings_requires_auth(self, client):
        """Test settings requires authentication."""
        url = reverse('quotes:settings')
        response = client.get(url)
        assert response.status_code == 302

