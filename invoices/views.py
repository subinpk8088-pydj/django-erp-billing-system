from decimal import Decimal
from .models import Invoice, InvoiceItem
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.db import transaction

from django.http import HttpResponse

from reportlab.pdfgen import canvas

from .models import Invoice
from .forms import InvoiceForm, InvoiceItemFormSet

from accounts.decorators import (
    admin_required,
    accountant_required
)

# invoices/views.py

from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.db import transaction

from django.http import HttpResponse

from reportlab.pdfgen import canvas

from inventory.utils import create_stock_movement

from .models import Invoice, InvoiceItem

from .forms import InvoiceForm, InvoiceItemFormSet

from accounts.decorators import (
    admin_required,
    accountant_required
)


@login_required
@accountant_required
def create_invoice(request):

    form = InvoiceForm(request.POST or None)

    formset = InvoiceItemFormSet(request.POST or None)

    if request.method == 'POST':

        if form.is_valid() and formset.is_valid():

            try:

                with transaction.atomic():

                    invoice = form.save(commit=False)

                    invoice.created_by = request.user

                    invoice.save()

                    items = formset.save(commit=False)

                    total = Decimal('0.00')

                    if not items:

                        messages.error(
                            request,
                            "At least one invoice item is required"
                        )

                        raise Exception()

                    for item in items:

                        if item in formset.deleted_objects:
                            continue

                        product = item.product

                        if item.quantity <= 0:

                            messages.error(
                                request,
                                f"Invalid quantity for {product.name}"
                            )

                            raise Exception()

                        if product.stock < item.quantity:

                            messages.error(
                                request,
                                f"Not enough stock for {product.name}"
                            )

                            raise Exception()

                        item.invoice = invoice

                        item.price = product.selling_price

                        item.save()

                        total += item.quantity * item.price

                        stock_before = product.stock

                        product.stock -= item.quantity

                        stock_after = product.stock

                        product.save()

                        create_stock_movement(

                            product=product,

                            movement_type='SALE',

                            quantity=item.quantity,

                            stock_before=stock_before,

                            stock_after=stock_after,

                            user=request.user,

                            reference=f"INV-{invoice.id}",

                            note='Invoice created'
                        )

                    gst = total * Decimal('0.18')

                    grand_total = total + gst

                    invoice.total_amount = total
                    invoice.gst_amount = gst
                    invoice.grand_total = grand_total

                    invoice.save()

                    messages.success(
                        request,
                        "Invoice created successfully"
                    )

                    return redirect('invoice_list')

            except Exception as e:

                print("Invoice Error:", e)

                messages.error(
                    request,
                    "Invoice creation failed"
                )

    return render(
        request,
        'invoices/invoice_form.html',
        {
            'form': form,
            'formset': formset
        }
    )
@login_required
def edit_invoice(request, pk):

    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )

    form = InvoiceForm(
        request.POST or None,
        instance=invoice
    )

    formset = InvoiceItemFormSet(
        request.POST or None,
        instance=invoice
    )

    if request.method == 'POST':

        if form.is_valid() and formset.is_valid():

            try:

                with transaction.atomic():

                    # 🔥 ROLLBACK OLD STOCK
                    old_items = InvoiceItem.objects.filter(
                        invoice=invoice
                    )

                    for old_item in old_items:

                        product = old_item.product

                        product.stock += old_item.quantity

                        product.save()

                    # delete old items
                    old_items.delete()

                    # update invoice
                    invoice = form.save(
                        commit=False
                    )

                    invoice.save()

                    items = formset.save(
                        commit=False
                    )

                    total = Decimal('0.00')

                    if not items:

                        messages.error(
                            request,
                            "At least one item required"
                        )

                        raise Exception()

                    for item in items:

                        product = item.product

                        # 🔥 STOCK VALIDATION
                        if product.stock < item.quantity:

                            messages.error(
                                request,
                                f"Not enough stock for {product.name}"
                            )

                            raise Exception()

                        item.invoice = invoice

                        item.price = product.selling_price

                        item.save()

                        # 🔥 REDUCE STOCK AGAIN
                        product.stock -= item.quantity

                        product.save()

                        total += (
                            item.quantity *
                            item.price
                        )

                    gst = total * Decimal('0.18')

                    grand_total = total + gst

                    invoice.total_amount = total
                    invoice.gst_amount = gst
                    invoice.grand_total = grand_total

                    invoice.save()

                    messages.success(
                        request,
                        "Invoice updated successfully"
                    )

                    return redirect(
                        'invoice_list'
                    )

            except Exception as e:

                print(e)

                messages.error(
                    request,
                    "Invoice update failed"
                )

    return render(
        request,
        'invoices/invoice_form.html',
        {
            'form': form,
            'formset': formset
        }
    )
    
@login_required
def delete_invoice(request, pk):

    invoice = get_object_or_404(
        Invoice,
        pk=pk
    )

    if request.method == 'POST':

        try:

            with transaction.atomic():

                items = InvoiceItem.objects.filter(
                    invoice=invoice
                )

                # 🔥 RESTORE STOCK
                for item in items:

                    product = item.product

                    product.stock += item.quantity

                    product.save()

                invoice.delete()

                messages.success(
                    request,
                    "Invoice deleted successfully"
                )

                return redirect(
                    'invoice_list'
                )

        except Exception as e:

            print(e)

            messages.error(
                request,
                "Invoice delete failed"
            )

    return render(
        request,
        'invoices/delete_invoice.html',
        {
            'invoice': invoice
        }
    )    

@login_required
def invoice_list(request):

    invoices = Invoice.objects.all().order_by('-id')

    return render(request, 'invoices/invoice_list.html', {
        'invoices': invoices
    })


@login_required
def invoice_detail(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)

    items = invoice.items.all()

    return render(request, 'invoices/invoice_detail.html', {
        'invoice': invoice,
        'items': items
    })


@login_required
@accountant_required
def mark_paid(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)

    invoice.status = 'paid'

    invoice.save()

    messages.success(
        request,
        "Invoice marked as paid"
    )

    return redirect('invoice_detail', pk=pk)


from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER

from invoices.models import Invoice

# ── Palette ────────────────────────────────────────────────────────────────
BRAND      = colors.HexColor('#1E3A5F')   # deep navy  – header / accents
BRAND_LIGHT= colors.HexColor('#EBF2FA')   # pale blue  – table header bg
MUTED      = colors.HexColor('#6B7280')   # grey       – sub-labels
LINE       = colors.HexColor('#E5E7EB')   # light grey – dividers / row borders
WHITE      = colors.white
BLACK      = colors.HexColor('#111827')


# ── Paragraph styles ───────────────────────────────────────────────────────
def _styles():
    base = dict(fontName='Helvetica', textColor=BLACK, leading=14)
    bold = dict(fontName='Helvetica-Bold')

    return {
        'company':  ParagraphStyle('company',  **{**base, **bold}, fontSize=18, textColor=BRAND),
        'tagline':  ParagraphStyle('tagline',  **base, fontSize=9,  textColor=MUTED),
        'label':    ParagraphStyle('label',    **base, fontSize=8,  textColor=MUTED, spaceAfter=1),
        'value':    ParagraphStyle('value',    **{**base, **bold}, fontSize=10),
        'badge':    ParagraphStyle('badge',    **{**base, **bold}, fontSize=11, textColor=BRAND),
        'th':       ParagraphStyle('th',       **{**base, **bold}, fontSize=9,  textColor=WHITE),
        'td':       ParagraphStyle('td',       **base, fontSize=9),
        'td_r':     ParagraphStyle('td_r',     **base, fontSize=9,  alignment=TA_RIGHT),
        'total_lbl':ParagraphStyle('total_lbl',**{**base, **bold}, fontSize=9,  textColor=MUTED, alignment=TA_RIGHT),
        'total_val':ParagraphStyle('total_val',**{**base, **bold}, fontSize=9,  alignment=TA_RIGHT),
        'grand_lbl':ParagraphStyle('grand_lbl',**{**base, **bold}, fontSize=11, textColor=WHITE, alignment=TA_RIGHT),
        'grand_val':ParagraphStyle('grand_val',**{**base, **bold}, fontSize=11, textColor=WHITE, alignment=TA_RIGHT),
        'footer':   ParagraphStyle('footer',   **base, fontSize=8,  textColor=MUTED, alignment=TA_CENTER),
    }


# ── View ───────────────────────────────────────────────────────────────────
@login_required
def invoice_pdf(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)
    items   = invoice.items.all()
    S       = _styles()

    # HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="invoice_{invoice.id}.pdf"'
    )

    W, H = A4
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
    )

    usable = W - 36*mm   # total usable width
    story  = []


    # ── 1. Header row: Company info (left) + Invoice badge (right) ──────────
    header_data = [[
        # left cell
        [
            Paragraph('Your Company', S['company']),
            Paragraph('123 Business Street, City — GST: 29ABCDE1234F1Z5', S['tagline']),
            Paragraph('hello@yourcompany.com  |  +91 98765 43210', S['tagline']),
        ],
        # right cell
        [
            Paragraph('INVOICE', S['badge']),
            Paragraph(f'# {invoice.id}', S['value']),
            Paragraph(f'Date: {invoice.date.strftime("%d %b %Y") if hasattr(invoice.date, "strftime") else invoice.date}', S['tagline']),
        ],
    ]]

    header_tbl = Table(header_data, colWidths=[usable * 0.6, usable * 0.4])
    header_tbl.setStyle(TableStyle([
        ('VALIGN',     (0,0), (-1,-1), 'TOP'),
        ('ALIGN',      (1,0), (1,0),   'RIGHT'),
        ('LEFTPADDING',(0,0), (-1,-1), 0),
        ('RIGHTPADDING',(0,0),(-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1),0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=BRAND))
    story.append(Spacer(1, 5*mm))


    # ── 2. Bill-to / meta block ─────────────────────────────────────────────
    meta_data = [[
        [
            Paragraph('BILLED TO', S['label']),
            Paragraph(invoice.customer.name, S['value']),
        ],
        [
            Paragraph('CREATED BY', S['label']),
            Paragraph(str(invoice.created_by), S['value']),
        ],
        [
            Paragraph('STATUS', S['label']),
            Paragraph(getattr(invoice, 'status', 'Issued').upper(), S['value']),
        ],
    ]]

    meta_tbl = Table(meta_data, colWidths=[usable/3]*3)
    meta_tbl.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING',(0,0), (-1,-1), 0),
        ('TOPPADDING',  (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1), 0),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6*mm))


    # ── 3. Items table ──────────────────────────────────────────────────────
    col_w = [usable*0.42, usable*0.13, usable*0.20, usable*0.25]

    rows = [[
        Paragraph('Product',  S['th']),
        Paragraph('Qty',      S['th']),
        Paragraph('Price',    S['th']),
        Paragraph('Total',    S['th']),
    ]]

    for item in items:
        rows.append([
            Paragraph(item.product.name,       S['td']),
            Paragraph(str(item.quantity),      S['td']),
            Paragraph(f'₹{item.price}',        S['td_r']),
            Paragraph(f'₹{item.get_total()}',  S['td_r']),
        ])

    items_tbl = Table(rows, colWidths=col_w, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        # header row
        ('BACKGROUND',   (0,0), (-1,0),  BRAND),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [WHITE, BRAND_LIGHT]),

        ('ALIGN',  (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

        ('FONTNAME',  (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',  (0,0), (-1,-1), 9),

        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),

        ('GRID',     (0,0), (-1,-1), 0.3, LINE),
        ('LINEBELOW',(0,0), (-1,0),  0.8, BRAND),
        ('ROUNDEDCORNERS', [3]),
    ]))
    story.append(items_tbl)
    story.append(Spacer(1, 5*mm))


    # ── 4. Totals block (right-aligned) ─────────────────────────────────────
    def money(val): return f'₹ {val}'

    totals_data = [
        [Paragraph('Subtotal',   S['total_lbl']), Paragraph(money(invoice.total_amount), S['total_val'])],
        [Paragraph('GST',        S['total_lbl']), Paragraph(money(invoice.gst_amount),   S['total_val'])],
    ]
    totals_tbl = Table(totals_data, colWidths=[usable*0.75, usable*0.25])
    totals_tbl.setStyle(TableStyle([
        ('ALIGN',         (0,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING',    (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING',   (0,0), (-1,-1), 0),
        ('RIGHTPADDING',  (0,0), (-1,-1), 0),
    ]))
    story.append(totals_tbl)
    story.append(Spacer(1, 2*mm))

    # Grand total bar
    grand_data = [[
        Paragraph('Grand Total', S['grand_lbl']),
        Paragraph(money(invoice.grand_total), S['grand_val']),
    ]]
    grand_tbl = Table(grand_data, colWidths=[usable*0.75, usable*0.25])
    grand_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), BRAND),
        ('ALIGN',         (0,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(grand_tbl)
    story.append(Spacer(1, 10*mm))


    # ── 5. Footer ───────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=LINE))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        'Thank you for your business! · Payment due within 30 days · '
        'Questions? hello@yourcompany.com',
        S['footer']
    ))

    doc.build(story)
    return response