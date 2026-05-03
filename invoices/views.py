# invoices/views.py

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import Invoice
from .forms import InvoiceForm, InvoiceItemFormSet


@login_required
def create_invoice(request):
    form = InvoiceForm(request.POST or None)
    formset = InvoiceItemFormSet(request.POST or None)

    if request.method == 'POST':
        if form.is_valid() and formset.is_valid():

            try:
                with transaction.atomic():

                    invoice = form.save()

                    items = formset.save(commit=False)

                    total = Decimal('0.00')

                    if not items:
                        form.add_error(None, "At least one item is required")
                        raise Exception("No items")

                    for item in items:

                        # skip deleted rows
                        if item in formset.deleted_objects:
                            continue

                        # 🔥 stock validation
                        if item.product.stock < item.quantity:
                            form.add_error(None, f"Not enough stock for {item.product.name}")
                            raise Exception("Stock error")

                        # set invoice + price
                        item.invoice = invoice
                        item.price = item.product.selling_price
                        item.save()

                        # calculate total
                        total += item.quantity * item.price

                        # 🔥 stock reduction
                        product = item.product
                        product.stock -= item.quantity
                        product.save()

                    # 🔥 GST (Decimal safe)
                    gst = total * Decimal('0.18')
                    grand_total = total + gst

                    invoice.total_amount = total
                    invoice.gst_amount = gst
                    invoice.grand_total = grand_total
                    invoice.save()

                return redirect('invoice_list')

            except Exception:
                # transaction will rollback automatically
                pass

    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset
    })


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
def mark_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    invoice.status = 'paid'
    invoice.save()

    return redirect('invoice_detail', pk=pk)

from django.http import HttpResponse
from reportlab.pdfgen import canvas

@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'

    p = canvas.Canvas(response)

    y = 800
    p.drawString(100, y, f"Invoice #{invoice.id}")
    y -= 30

    p.drawString(100, y, f"Customer: {invoice.customer.name}")
    y -= 30

    for item in items:
        p.drawString(100, y, f"{item.product.name} - {item.quantity} x {item.price}")
        y -= 20

    y -= 20
    p.drawString(100, y, f"Total: {invoice.total_amount}")
    y -= 20
    p.drawString(100, y, f"GST: {invoice.gst_amount}")
    y -= 20
    p.drawString(100, y, f"Grand Total: {invoice.grand_total}")

    p.showPage()
    p.save()

    return response