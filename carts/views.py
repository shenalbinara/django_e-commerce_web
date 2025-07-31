from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

from django.http import HttpResponse

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

    
    
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(product = product, variation_category__iexact = key, variation_value__iexact=value)
                product_variation.append(variation)
                print(variation)
            except:
                pass
            
    
    
   
    try:
        #cart = Cart.objects.get(cart_id = cart_id(request))
        cart = Cart.objects.get(cart_id = _cart_id(request))

    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    
    #is_cart_item_exists = CartItem.objects.filter(product, cart=cart).exists()
    # ✅ Correct
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    cart_items = []  # 🔧 Fix: Ensure cart_items is defined

    if is_cart_item_exists:
        cart_items = CartItem.objects.filter(product=product, cart=cart)

    ex_var_list = []
    id_list = []

    for item in cart_items:
        existing_variation = item.variations.all()
        ex_var_list.append(list(existing_variation))
        id_list.append(item.id)

    if product_variation in ex_var_list:
        # Match found, increase quantity
        index = ex_var_list.index(product_variation)
        item_id = id_list[index]
        item = CartItem.objects.get(id=item_id)
        item.quantity += 1
        item.save()
    else:
        # No match found, create a new cart item
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.set(product_variation)
        cart_item.save()



    return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id)

        # Extract product variation from request
        product_variation = []
        if request.method == 'GET':
            for key in request.GET:
                value = request.GET[key]
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value
                    )
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

        # Filter cart items for the same product
        cart_items = CartItem.objects.filter(product=product, cart=cart)

        for cart_item in cart_items:
            existing_variation = list(cart_item.variations.all())
            if product_variation == existing_variation:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
                break  # exit after finding the matching item

    except Exception as e:
        print("Error in remove_cart:", str(e))  # Optional: helpful for debugging

    return redirect("cart")

        


#def remove_cart_item(request, product_id):
   # cart = Cart.objects.get(cart_id=_cart_id(request))
    #product = get_object_or_404(Product, id=product_id)
    #cart_item = CartItem.objects.get(product= product, cart=cart)
    #cart_item.delete()
    #return redirect("cart")



def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    # Extract variations from the request if available
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
            except Variation.DoesNotExist:
                pass

    # Loop through all matching cart items to find the exact variation match
    cart_items = CartItem.objects.filter(product=product, cart=cart)
    for cart_item in cart_items:
        existing_variation = list(cart_item.variations.all())
        if existing_variation == product_variation:
            cart_item.delete()
            break  # stop after deleting the correct one

    return redirect("cart")



    
    
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
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

 