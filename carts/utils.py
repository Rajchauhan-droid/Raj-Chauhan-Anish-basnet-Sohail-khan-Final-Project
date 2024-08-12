# carts/utils.py

def _cart_id(request):
    cart = request.session.get('cart_id', None)
    if not cart:
        cart = request.session.create()
        request.session['cart_id'] = cart
    return cart
