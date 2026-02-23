"""Quotes models."""

from decimal import Decimal
from datetime import date, timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.core.models import HubBaseModel


# ---------------------------------------------------------------------------
# Quote Series
# ---------------------------------------------------------------------------

class QuoteSeries(HubBaseModel):
    """
    Quote numbering series.

    Each series has a prefix and an auto-incrementing counter.
    Examples: QT (quotes), PR (proposals), BU (budgets).
    """

    name = models.CharField(_('Name'), max_length=100)
    prefix = models.CharField(_('Prefix'), max_length=10)
    next_number = models.PositiveIntegerField(
        _('Next Number'), default=1,
    )
    is_default = models.BooleanField(_('Default Series'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    number_digits = models.PositiveSmallIntegerField(
        _('Number Digits'), default=5,
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'quotes_series'
        verbose_name = _('Quote Series')
        verbose_name_plural = _('Quote Series')
        ordering = ['prefix']
        unique_together = [('hub_id', 'prefix')]

    def __str__(self):
        return f'{self.prefix} - {self.name}'

    def generate_number(self):
        """
        Get and increment the next quote number.

        Returns formatted quote number like "QT-00001".
        """
        number = self.next_number
        self.next_number += 1
        self.save(update_fields=['next_number', 'updated_at'])
        return f'{self.prefix}-{str(number).zfill(self.number_digits)}'

    def save(self, *args, **kwargs):
        # Ensure only one default series per hub
        if self.is_default:
            QuoteSeries.objects.filter(
                hub_id=self.hub_id, is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Quote Settings
# ---------------------------------------------------------------------------

class QuoteSettings(HubBaseModel):
    """Per-hub quote configuration."""

    default_validity_days = models.PositiveIntegerField(
        _('Default Validity (days)'), default=30,
    )
    default_series = models.ForeignKey(
        QuoteSeries, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Default Series'),
        related_name='+',
    )
    default_notes = models.TextField(
        _('Default Notes'), blank=True,
        help_text=_('Default notes included in new quotes'),
    )
    default_terms = models.TextField(
        _('Default Terms'), blank=True,
        help_text=_('Default terms and conditions for quotes'),
    )
    tax_rate = models.DecimalField(
        _('Default Tax Rate %'), max_digits=5, decimal_places=2,
        default=Decimal('21.00'),
    )
    show_tax = models.BooleanField(
        _('Show Tax'), default=True,
        help_text=_('Show tax breakdown on quotes'),
    )
    show_discount = models.BooleanField(
        _('Show Discount'), default=True,
        help_text=_('Show discount column on quotes'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'quotes_settings'
        verbose_name = _('Quote Settings')
        verbose_name_plural = _('Quote Settings')
        unique_together = [('hub_id',)]

    def __str__(self):
        return f'Quote Settings (hub={self.hub_id})'

    @classmethod
    def get_settings(cls, hub_id):
        """Get or create settings for a hub."""
        obj, _ = cls.all_objects.get_or_create(hub_id=hub_id)
        return obj


# ---------------------------------------------------------------------------
# Quote
# ---------------------------------------------------------------------------

class Quote(HubBaseModel):
    """Quote / Proposal / Budget document."""

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        SENT = 'sent', _('Sent')
        ACCEPTED = 'accepted', _('Accepted')
        REJECTED = 'rejected', _('Rejected')
        EXPIRED = 'expired', _('Expired')
        CONVERTED = 'converted', _('Converted')

    # Identification
    quote_number = models.CharField(
        _('Quote Number'), max_length=50, blank=True,
    )
    series = models.ForeignKey(
        QuoteSeries, on_delete=models.PROTECT,
        verbose_name=_('Series'),
    )
    title = models.CharField(
        _('Title'), max_length=255, blank=True,
    )

    # Customer (FK + denormalized snapshot for PDF stability)
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='quotes',
        verbose_name=_('Customer'),
    )
    customer_name = models.CharField(
        _('Customer Name'), max_length=255,
    )
    customer_email = models.EmailField(
        _('Customer Email'), blank=True,
    )
    customer_phone = models.CharField(
        _('Customer Phone'), max_length=50, blank=True,
    )
    customer_address = models.TextField(
        _('Customer Address'), blank=True,
    )

    # Related lead (optional, stores UUID without hard FK)
    related_lead = models.UUIDField(
        _('Related Lead'), null=True, blank=True,
        help_text=_('UUID of the related lead'),
    )

    # Status
    status = models.CharField(
        _('Status'), max_length=20,
        choices=Status.choices, default=Status.DRAFT,
    )

    # Content
    notes = models.TextField(_('Notes'), blank=True)
    terms = models.TextField(_('Terms & Conditions'), blank=True)

    # Amounts
    subtotal = models.DecimalField(
        _('Subtotal'), max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
    )
    discount_amount = models.DecimalField(
        _('Discount Amount'), max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
    )
    discount_percent = models.DecimalField(
        _('Discount %'), max_digits=5, decimal_places=2,
        default=Decimal('0.00'),
    )
    tax_amount = models.DecimalField(
        _('Tax Amount'), max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
    )
    tax_rate = models.DecimalField(
        _('Tax Rate %'), max_digits=5, decimal_places=2,
        default=Decimal('21.00'),
    )
    total = models.DecimalField(
        _('Total'), max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
    )

    # Validity
    valid_until = models.DateField(
        _('Valid Until'), null=True, blank=True,
    )

    # Timestamps for status transitions
    sent_at = models.DateTimeField(_('Sent At'), null=True, blank=True)
    accepted_at = models.DateTimeField(_('Accepted At'), null=True, blank=True)
    rejected_at = models.DateTimeField(_('Rejected At'), null=True, blank=True)
    converted_at = models.DateTimeField(_('Converted At'), null=True, blank=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    class Meta(HubBaseModel.Meta):
        db_table = 'quotes_quote'
        verbose_name = _('Quote')
        verbose_name_plural = _('Quotes')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hub_id', 'quote_number']),
            models.Index(fields=['hub_id', 'status']),
            models.Index(fields=['hub_id', 'valid_until']),
        ]

    def __str__(self):
        return f'{self.quote_number or "DRAFT"} - {self.customer_name}'

    @property
    def is_expired(self):
        """Check if quote has expired based on valid_until date."""
        if self.status != self.Status.SENT:
            return False
        if not self.valid_until:
            return False
        return self.valid_until < date.today()

    @property
    def days_until_expiry(self):
        """Return days until expiry, or None if no valid_until date."""
        if not self.valid_until:
            return None
        delta = self.valid_until - date.today()
        return delta.days

    def calculate_totals(self):
        """Recalculate totals from line items."""
        lines = self.lines.filter(is_deleted=False)
        self.subtotal = sum(line.total for line in lines)

        # Apply global discount
        if self.discount_percent > 0:
            self.discount_amount = self.subtotal * (self.discount_percent / Decimal('100'))
        after_discount = self.subtotal - self.discount_amount

        # Apply tax
        self.tax_amount = after_discount * (self.tax_rate / Decimal('100'))
        self.total = after_discount + self.tax_amount

    def mark_sent(self):
        """Mark quote as sent. Assigns quote number if not yet assigned."""
        if self.status != self.Status.DRAFT:
            return False
        if not self.quote_number:
            self.quote_number = self.series.generate_number()
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        if not self.valid_until:
            settings = QuoteSettings.get_settings(self.hub_id)
            self.valid_until = date.today() + timedelta(days=settings.default_validity_days)
        self.save(update_fields=[
            'quote_number', 'status', 'sent_at', 'valid_until', 'updated_at',
        ])
        return True

    def mark_accepted(self):
        """Mark quote as accepted."""
        if self.status != self.Status.SENT:
            return False
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save(update_fields=['status', 'accepted_at', 'updated_at'])
        return True

    def mark_rejected(self, reason=''):
        """Mark quote as rejected with optional reason."""
        if self.status != self.Status.SENT:
            return False
        self.status = self.Status.REJECTED
        self.rejected_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=[
            'status', 'rejected_at', 'rejection_reason', 'updated_at',
        ])
        return True

    def mark_expired(self):
        """Mark quote as expired."""
        if self.status != self.Status.SENT:
            return False
        self.status = self.Status.EXPIRED
        self.save(update_fields=['status', 'updated_at'])
        return True

    def mark_converted(self):
        """Mark an accepted quote as converted (e.g. to sale/invoice)."""
        if self.status != self.Status.ACCEPTED:
            return False
        self.status = self.Status.CONVERTED
        self.converted_at = timezone.now()
        self.save(update_fields=['status', 'converted_at', 'updated_at'])
        return True


# ---------------------------------------------------------------------------
# Quote Line
# ---------------------------------------------------------------------------

class QuoteLine(HubBaseModel):
    """Individual line item in a quote."""

    class LineType(models.TextChoices):
        PRODUCT = 'product', _('Product')
        SERVICE = 'service', _('Service')
        CUSTOM = 'custom', _('Custom')

    quote = models.ForeignKey(
        Quote, on_delete=models.CASCADE,
        related_name='lines', verbose_name=_('Quote'),
    )

    line_type = models.CharField(
        _('Type'), max_length=20,
        choices=LineType.choices, default=LineType.CUSTOM,
    )

    # Optional references to products/services
    product_id = models.UUIDField(
        _('Product'), null=True, blank=True,
        help_text=_('UUID of the referenced product'),
    )
    service_id = models.UUIDField(
        _('Service'), null=True, blank=True,
        help_text=_('UUID of the referenced service'),
    )

    # Line data
    description = models.CharField(_('Description'), max_length=500)
    quantity = models.DecimalField(
        _('Quantity'), max_digits=10, decimal_places=3,
        default=Decimal('1'),
    )
    unit_price = models.DecimalField(
        _('Unit Price'), max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
    )
    discount_percent = models.DecimalField(
        _('Discount %'), max_digits=5, decimal_places=2,
        default=Decimal('0.00'),
    )
    tax_rate = models.DecimalField(
        _('Tax Rate %'), max_digits=5, decimal_places=2,
        default=Decimal('21.00'),
    )

    # Calculated
    total = models.DecimalField(
        _('Line Total'), max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
    )

    # Order
    sort_order = models.PositiveSmallIntegerField(_('Sort Order'), default=0)

    class Meta(HubBaseModel.Meta):
        db_table = 'quotes_line'
        verbose_name = _('Quote Line')
        verbose_name_plural = _('Quote Lines')
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f'{self.description} x {self.quantity}'

    def calculate_total(self):
        """Calculate line total with discount."""
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percent / Decimal('100'))
        self.total = subtotal - discount
        return self.total

    def save(self, *args, **kwargs):
        self.calculate_total()
        super().save(*args, **kwargs)
