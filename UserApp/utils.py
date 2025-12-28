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



from decimal import Decimal
from django.utils import timezone

def calculate_rent_total(user, duration_days):
    """
    Returns:
    - total_rent_amount
    - detailed_snapshot (for invoice + webhook safety)
    """
    from .models import CartItem, Rental

    cart_items = CartItem.objects.filter(user=user)

    # 🔧 UPDATED: guard against empty cart
    if not cart_items.exists():
        return Decimal("0.00"), []

    snapshot = []
    total = Decimal("0.00")

    for item in cart_items:

        # PRODUCT RENT
        if item.product:
            temp_rental = Rental(
                user=user,
                product=item.product,
                duration_days=duration_days,
                end_date=timezone.now()
            )

            fee = temp_rental.calculate_rental_fee()

            snapshot.append({
                "type": "product",
                "id": item.product.id,
                "name": item.product.model_name,
                "duration_days": duration_days,
                "amount": str(fee)
            })

            total += fee

        # BUNDLE RENT (simple for now)
        elif item.bundle:
            # 🔧 UPDATED: Decimal-safe calculation
            fee = Decimal(item.bundle.price) * Decimal(item.quantity)

            snapshot.append({
                "type": "bundle",
                "id": item.bundle.id,
                "name": item.bundle.name,
                "duration_days": duration_days,
                "amount": str(fee)
            })

            total += fee

    # UPDATED: always return Decimal + snapshot
    return total.quantize(Decimal("0.01")), snapshot
