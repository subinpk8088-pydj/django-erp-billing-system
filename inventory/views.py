from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from .models import StockMovement


@login_required
def stock_movement_list(request):

    movements = StockMovement.objects.select_related(
        'product'
    ).order_by('-created_at')

    return render(

        request,

        'inventory/stock_movement_list.html',

        {
            'movements': movements
        }
    )