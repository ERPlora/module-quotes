"""AI tools for the Quotes module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListQuotes(AssistantTool):
    name = "list_quotes"
    description = "List quotes with optional filters. Returns quote number, customer, status, total."
    module_id = "quotes"
    required_permission = "quotes.view_quote"
    parameters = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Filter: draft, sent, accepted, rejected, expired, converted"},
            "search": {"type": "string", "description": "Search by customer name or quote number"},
            "limit": {"type": "integer", "description": "Max results (default 20)"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from quotes.models import Quote
        from django.db.models import Q
        qs = Quote.objects.all().order_by('-created_at')
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        if args.get('search'):
            s = args['search']
            qs = qs.filter(Q(customer_name__icontains=s) | Q(quote_number__icontains=s))
        limit = args.get('limit', 20)
        return {
            "quotes": [
                {
                    "id": str(q.id),
                    "quote_number": q.quote_number,
                    "title": q.title,
                    "customer_name": q.customer_name,
                    "status": q.status,
                    "total": str(q.total),
                    "valid_until": str(q.valid_until) if q.valid_until else None,
                }
                for q in qs[:limit]
            ],
            "total": qs.count(),
        }


@register_tool
class CreateQuote(AssistantTool):
    name = "create_quote"
    description = "Create a new quote for a customer with line items."
    module_id = "quotes"
    required_permission = "quotes.change_quote"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Quote title"},
            "customer_id": {"type": "string", "description": "Customer ID"},
            "customer_name": {"type": "string", "description": "Customer name (if no customer_id)"},
            "customer_email": {"type": "string", "description": "Customer email"},
            "notes": {"type": "string", "description": "Additional notes"},
            "valid_days": {"type": "integer", "description": "Days until expiry (default 30)"},
            "lines": {
                "type": "array",
                "description": "Quote lines",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "string"},
                    },
                    "required": ["description", "quantity", "unit_price"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["title"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from datetime import date, timedelta
        from decimal import Decimal
        from quotes.models import Quote, QuoteLine
        valid_days = args.get('valid_days', 30)
        q = Quote.objects.create(
            title=args['title'],
            customer_id=args.get('customer_id'),
            customer_name=args.get('customer_name', ''),
            customer_email=args.get('customer_email', ''),
            notes=args.get('notes', ''),
            valid_until=date.today() + timedelta(days=valid_days),
            status='draft',
        )
        for line in args.get('lines', []):
            QuoteLine.objects.create(
                quote=q,
                description=line['description'],
                quantity=line['quantity'],
                unit_price=Decimal(line['unit_price']),
                line_type='custom',
            )
        q.save()  # Triggers total recalculation if applicable
        return {"id": str(q.id), "quote_number": q.quote_number, "created": True}


@register_tool
class GetQuote(AssistantTool):
    name = "get_quote"
    description = "Get detailed quote info including line items and status timestamps."
    module_id = "quotes"
    required_permission = "quotes.view_quote"
    parameters = {
        "type": "object",
        "properties": {"quote_id": {"type": "string", "description": "Quote ID"}},
        "required": ["quote_id"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from quotes.models import Quote
        q = Quote.objects.select_related('customer').get(id=args['quote_id'])
        lines = q.lines.filter(is_deleted=False).order_by('sort_order')
        return {
            "id": str(q.id), "quote_number": q.quote_number, "title": q.title,
            "customer_name": q.customer_name, "customer_email": q.customer_email,
            "status": q.status, "subtotal": str(q.subtotal), "tax_amount": str(q.tax_amount),
            "total": str(q.total), "valid_until": str(q.valid_until) if q.valid_until else None,
            "notes": q.notes, "terms": q.terms,
            "sent_at": q.sent_at.isoformat() if q.sent_at else None,
            "accepted_at": q.accepted_at.isoformat() if q.accepted_at else None,
            "lines": [
                {"description": l.description, "quantity": str(l.quantity),
                 "unit_price": str(l.unit_price), "total": str(l.total)}
                for l in lines
            ],
        }


@register_tool
class UpdateQuoteStatus(AssistantTool):
    name = "update_quote_status"
    description = "Update quote status: send (draft→sent), accept (sent→accepted), reject (sent→rejected), convert (accepted→converted)."
    module_id = "quotes"
    required_permission = "quotes.change_quote"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "quote_id": {"type": "string", "description": "Quote ID"},
            "action": {"type": "string", "description": "Action: send, accept, reject, convert"},
            "reason": {"type": "string", "description": "Rejection reason (for reject action)"},
        },
        "required": ["quote_id", "action"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from quotes.models import Quote
        q = Quote.objects.get(id=args['quote_id'])
        action = args['action']
        if action == 'send':
            ok = q.mark_sent()
        elif action == 'accept':
            ok = q.mark_accepted()
        elif action == 'reject':
            ok = q.mark_rejected(reason=args.get('reason', ''))
        elif action == 'convert':
            ok = q.mark_converted()
        else:
            return {"error": f"Unknown action: {action}"}
        if not ok:
            return {"error": f"Cannot {action} a {q.status} quote"}
        return {"id": str(q.id), "quote_number": q.quote_number, "status": q.status}
