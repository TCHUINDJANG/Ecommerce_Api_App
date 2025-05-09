from django.db import transaction
from .models import Order, OrderItem
from products.models import Product


def process_checkout(user, validated_data):
    with transaction.atomic():
        # Create or get addresses
        shipping_address = Address.objects.create(
            user=user,
            **validated_data['shipping_address']
        )
        
        if validated_data['billing_address_same_as_shipping']:
            billing_address = shipping_address
        else:
            billing_address = Address.objects.create(
                user=user,
                **validated_data['billing_address']
            )

        # Create or get payment method
        payment_method = PaymentMethod.objects.create(
            user=user,
            **validated_data['payment_method']
        )

        # Calculate totals
        items_data = validated_data['items']
        product_ids = [item['product_id'] for item in items_data]
        products = Product.objects.in_bulk(product_ids)

        subtotal = 0
        order_items = []
        
        for item_data in items_data:
            product = products[item_data['product_id']]
            quantity = item_data['quantity']
            price = product.price
            subtotal += quantity * price
            
            order_items.append(OrderItem(
                product=product,
                quantity=quantity,
                price=price
            ))

        # Calculate shipping and tax (simplified for example)
        shipping_cost = 9.99  # Could be calculated based on address, weight, etc.
        tax_rate = 0.1  # 10%
        tax = subtotal * tax_rate
        total = subtotal + shipping_cost + tax

        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total
        )

        # Create order items
        for item in order_items:
            item.order = order
        OrderItem.objects.bulk_create(order_items)

        # Update product stock
        for product_id, item_data in zip(product_ids, items_data):
            product = products[product_id]
            product.stock -= item_data['quantity']
            product.save()

        # Process payment (would integrate with payment gateway in real app)
        # For example:
        # payment_success = process_payment(total, payment_method)
        # if not payment_success:
        #     raise Exception("Payment failed")

        return order