from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


# Create your views here.

from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

    
    
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)

    # If user is logged in
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        cart_items = []

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, user=current_user)

        ex_var_list = []
        id_list = []

        for item in cart_items:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id_list.append(item.id)

        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]
            item = CartItem.objects.get(id=item_id)
            item.quantity += 1
            item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user
            )
            if len(product_variation) > 0:
                cart_item.variations.set(product_variation)
            cart_item.save()

        return redirect('cart')

    # If user is NOT logged in
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        cart_items = []

        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, cart=cart)

        ex_var_list = []
        id_list = []

        for item in cart_items:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation))
            id_list.append(item.id)

        if product_variation in ex_var_list:
            index = ex_var_list.index(product_variation)
            item_id = id_list[index]
            item = CartItem.objects.get(id=item_id)
            item.quantity += 1
            item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variation) > 0:
                cart_item.variations.set(product_variation)
            cart_item.save()

        return redirect('cart')




def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            # Logged-in user cart item
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # Guest user cart item
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        # Decrease quantity or delete
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except CartItem.DoesNotExist:
        pass

    return redirect("cart")

        


#def remove_cart_item(request, product_id):
   # cart = Cart.objects.get(cart_id=_cart_id(request))
    #product = get_object_or_404(Product, id=product_id)
    #cart_item = CartItem.objects.get(product= product, cart=cart)
    #cart_item.delete()
    #return redirect("cart")



def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            # Logged-in user: remove the specific cart_item
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # Guest user: remove the specific cart_item from their session cart
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

        cart_item.delete()

    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    return redirect("cart")




    
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)  # Add is_active=True if needed

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = round((2 * total) / 100, 2)
        grand_total = total + tax

    except ObjectDoesNotExist:
        cart_items = []  # fallback if cart doesn't exist

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)  # Add is_active=True if needed


        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = round((2 * total) / 100, 2)
        grand_total = total + tax

    except ObjectDoesNotExist:
        cart_items = []  # fallback if cart doesn't exist

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)

 