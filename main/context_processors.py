from .models import Category, Wishlist
from .cart import Cart


def categories_context(request):
    return {'categories': Category.objects.all()}


def wishlist_count(request):
    if request.user.is_authenticated:
        return {'wishlist_count': Wishlist.objects.filter(user=request.user).count()}
    return {'wishlist_count': 0}


def cart_count(request):
    return {'cart_count': Cart(request).count()}
