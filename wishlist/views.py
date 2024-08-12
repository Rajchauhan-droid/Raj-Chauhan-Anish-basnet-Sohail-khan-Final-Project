from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Wishlist, WishlistItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


def _wishlist_id(request):
    wishlist = request.session.get('wishlist_id')
    if not wishlist:
        wishlist = Wishlist.objects.create()
        request.session['wishlist_id'] = wishlist.wishlist_id
    return wishlist


from django.contrib import messages
from carts.models import CartItem
from carts.utils import _cart_id  # Import the cart utility function

@login_required(login_url="login")
def add_to_wishlist(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    wishlist = _wishlist_id(request)

    is_wishlist_item_exists = WishlistItem.objects.filter(product=product, user=current_user).exists()
    if is_wishlist_item_exists:
        messages.warning(request, 'This product is already in your wishlist.')
    else:
        # Check if any WishlistItem with the same product already exists
        existing_wishlist_item = WishlistItem.objects.filter(product=product, user=current_user).first()

        if existing_wishlist_item:
            messages.warning(request, 'This product is already in your wishlist.')
        else:
            wishlist_item = WishlistItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
                wishlist=wishlist,
            )

            wishlist_item.save()
            messages.success(request, 'Product added to wishlist successfully.')

            # Check if the product is in the wishlist and remove it from the wishlist
            cart_id = _cart_id(request)
            cart_item_exists = CartItem.objects.filter(cart__cart_id=cart_id, product=product).exists()

            if cart_item_exists:
                # Clear the entire wishlist as one item is added to the cart
                WishlistItem.objects.filter(user=current_user).delete()
                messages.info(request, 'Wishlist cleared as the product is added to the cart.')

    return redirect('wishlist')











@login_required(login_url="login")
def remove_from_wishlist(request, product_id, wishlist_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            wishlist_item = get_object_or_404(WishlistItem, id=wishlist_item_id, product_id=product_id)
        else:
            wishlist = Wishlist.objects.get(wishlist_id = _wishlist_id(request))
            wishlist_item = WishlistItem.objects.get(product=product, wishlist=wishlist, id=wishlist_item_id)
        if wishlist_item.quantity > 1:
            wishlist_item.quantity -= 1
            wishlist_item.save()
        else:
            wishlist_item.delete()
    except:
        pass
    return redirect('cart')


@login_required(login_url="login")
def remove_wishlist_item(request, product_id, wishlist_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        wishlist_item = get_object_or_404(WishlistItem, product=product, user=request.user, id=wishlist_item_id)
    else:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_item = WishlistItem.objects.get(product=product, wishlist=wishlist, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')


@login_required(login_url="login")
def wishlist(request, total=0, quantity=0, wishlist_items=None):
    try:
        if request.user.is_authenticated:
            wishlist_items = WishlistItem.objects.filter(user=request.user)
        else:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
            wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)

        for wishlist_item in wishlist_items:
            total += (wishlist_item.product.marked_price * wishlist_item.quantity)
            quantity += wishlist_item.quantity
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'store/wishlist.html', context)
