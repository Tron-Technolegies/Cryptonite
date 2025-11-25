from .models import CartItem

def calculate_cart_total(user):
    cart_items = CartItem.objects.filter(user=user)

    total_price = 0
    for item in cart_items:
        if item.product:
            total_price += float(item.product.price) * item.quantity
        elif item.bundle:
            total_price += float(item.bundle.price) * item.quantity

    return total_price, cart_items
