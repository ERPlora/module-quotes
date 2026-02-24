"""Tests for quotes models."""
import pytest
from django.utils import timezone

from quotes.models import QuoteSeries, Quote


@pytest.mark.django_db
class TestQuoteSeries:
    """QuoteSeries model tests."""

    def test_create(self, quote_series):
        """Test QuoteSeries creation."""
        assert quote_series.pk is not None
        assert quote_series.is_deleted is False

    def test_str(self, quote_series):
        """Test string representation."""
        assert str(quote_series) is not None
        assert len(str(quote_series)) > 0

    def test_soft_delete(self, quote_series):
        """Test soft delete."""
        pk = quote_series.pk
        quote_series.is_deleted = True
        quote_series.deleted_at = timezone.now()
        quote_series.save()
        assert not QuoteSeries.objects.filter(pk=pk).exists()
        assert QuoteSeries.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, quote_series):
        """Test default queryset excludes deleted."""
        quote_series.is_deleted = True
        quote_series.deleted_at = timezone.now()
        quote_series.save()
        assert QuoteSeries.objects.filter(hub_id=hub_id).count() == 0

    def test_toggle_active(self, quote_series):
        """Test toggling is_active."""
        original = quote_series.is_active
        quote_series.is_active = not original
        quote_series.save()
        quote_series.refresh_from_db()
        assert quote_series.is_active != original


@pytest.mark.django_db
class TestQuote:
    """Quote model tests."""

    def test_create(self, quote):
        """Test Quote creation."""
        assert quote.pk is not None
        assert quote.is_deleted is False

    def test_str(self, quote):
        """Test string representation."""
        assert str(quote) is not None
        assert len(str(quote)) > 0

    def test_soft_delete(self, quote):
        """Test soft delete."""
        pk = quote.pk
        quote.is_deleted = True
        quote.deleted_at = timezone.now()
        quote.save()
        assert not Quote.objects.filter(pk=pk).exists()
        assert Quote.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, quote):
        """Test default queryset excludes deleted."""
        quote.is_deleted = True
        quote.deleted_at = timezone.now()
        quote.save()
        assert Quote.objects.filter(hub_id=hub_id).count() == 0


