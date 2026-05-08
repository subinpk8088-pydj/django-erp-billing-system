from .models import StockMovement


def create_stock_movement(

    product,
    movement_type,
    quantity,
    stock_before,
    stock_after,
    user=None,
    reference='',
    note=''

):

    StockMovement.objects.create(

        product=product,

        movement_type=movement_type,

        quantity=quantity,

        stock_before=stock_before,

        stock_after=stock_after,

        created_by=user,

        reference=reference,

        note=note
    )