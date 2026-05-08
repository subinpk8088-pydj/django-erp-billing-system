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


@login_required
def invoice_pdf(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)

    items = invoice.items.all()

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="invoice_{invoice.id}.pdf"'
    )

    p = canvas.Canvas(response)

    y = 800

    p.setFont("Helvetica-Bold", 16)

    p.drawString(200, y, "INVOICE")

    y -= 40

    p.setFont("Helvetica", 12)

    p.drawString(50, y, f"Invoice ID: {invoice.id}")

    y -= 25

    p.drawString(
        50,
        y,
        f"Customer: {invoice.customer.name}"
    )

    y -= 25

    p.drawString(
        50,
        y,
        f"Created By: {invoice.created_by}"
    )

    y -= 40

    # 🔥 TABLE HEADER
    p.drawString(50, y, "Product")
    p.drawString(250, y, "Qty")
    p.drawString(320, y, "Price")
    p.drawString(420, y, "Total")

    y -= 20

    for item in items:

        p.drawString(50, y, item.product.name)

        p.drawString(250, y, str(item.quantity))

        p.drawString(320, y, str(item.price))

        p.drawString(
            420,
            y,
            str(item.get_total())
        )

        y -= 20

    y -= 30

    p.drawString(
        320,
        y,
        f"Subtotal: {invoice.total_amount}"
    )

    y -= 20

    p.drawString(
        320,
        y,
        f"GST: {invoice.gst_amount}"
    )

    y -= 20

    p.drawString(
        320,
        y,
        f"Grand Total: {invoice.grand_total}"
    )

    p.showPage()

    p.save()

    return response