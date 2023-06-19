from .models import *

def cart_item_count(request):
    if request.user.is_authenticated:
        if not hasattr(request.user, 'customer'):
            customer = Customer.objects.create(user=request.user)
        else:
            customer = request.user.customer
        order = Order.objects.filter(customer=customer, complete=False).first()
        if order:
            item_count = order.get_cart_items
        else:
            item_count = 0
    else:
        item_count = 0
    return {'cart_item_count': item_count}
