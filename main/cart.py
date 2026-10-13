from django.shortcuts import get_object_or_404
from .models import Product

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get('cart')
        if cart is None:
            cart = {}
            self.session['cart'] = cart
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id] += quantity
        else:
            self.cart[product_id] = quantity
        self.session.modified = True

    def update(self, product, quantity):
        product_id = str(product.id)
        if quantity > 0:
            self.cart[product_id] = quantity
        else:
            self.cart.pop(product_id, None)
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        self.cart.pop(product_id, None)
        self.session.modified = True

    def get_items(self):
        items = []
        for product_id, quantity in self.cart.items():
            product = get_object_or_404(Product, pk=product_id)
            final_price = product.final_price
            item_total = float(final_price) * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total,
                'final_price': final_price,
            })
        return items

    def get_total(self):
        total = 0
        for product_id, quantity in self.cart.items():
            product = get_object_or_404(Product, pk=product_id)
            total += float(product.final_price) * quantity
        return round(total, 2)

    def count(self):
        return sum(self.cart.values())

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True
