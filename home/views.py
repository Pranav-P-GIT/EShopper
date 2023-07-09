from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse
from django.contrib import auth
from .models import *
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import HttpResponse


def index (request):
    products=Product.objects.all()
    context={'products':products}
    return render(request,"index.html",context)


def details(request):
    id = request.GET["id"]
    product = get_object_or_404(Product, id=id)
    comments = product.comments.filter(active=True)
    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.user.username
            email = request.user.email
            body = request.POST.get('body')
            comment = Comment.objects.create(product=product, name=name, email=email, body=body,active=True)
            return redirect(f'{reverse("detailpage")}?id={id}') 
    context = {'product': product, 'comments': comments}
    return render(request, 'detail.html', context)




def register(request):
    if request.method=="POST":
        username=request.POST["uname"]
        email=request.POST["email"]
        password=request.POST["psw"]
        repassword=request.POST["psw-repeat"]
        ucheck=User.objects.filter(username=username)
        echeck=User.objects.filter(email=email)
        if ucheck:
            msg="Username already exists."
            return render(request,"registerpage.html",{"msg":msg})
        elif echeck:
            msg="Email already exists."
            return render(request,"registerpage.html",{"msg":msg})
        elif password=="" or password!=repassword:
            msg="Re-password error."
            return render(request,"registerpage.html",{"msg":msg})
        else:
            user=User.objects.create_user(username=username,email=email,password=password)
            user.save();
            return redirect("loginpage")
    else:
        return render(request,"registerpage.html")

def login_view(request):
    if request.method=="POST":
        username=request.POST["uname"]
        password=request.POST["psw"]
        check=auth.authenticate(username=username,password=password)
        if check is not None:
            auth.login(request,check)
            return redirect("/")
        else:
            msg="Invalid username or password."
            return render(request,"loginpage.html",{"msg":msg})
    else:
        return render(request,"loginpage.html")
    
    
def logout(request):
    auth.logout(request)
    return redirect("/")


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
    context = {'items': items, 'order': order}
    return render(request, "cart.html", context)



def get_cart_number(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cart_number = order.get_cart_items
    else:
        cart_number = 0
    return JsonResponse({'cart_number': cart_number})


def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        product = get_object_or_404(Product, pk=product_id)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        order_item.quantity += 1
        order_item.save()
        return JsonResponse({})
    else:
        return redirect('loginpage')



def decrease_quantity(request, product_id):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.get(customer=customer, complete=False)
    product = get_object_or_404(Product, pk=product_id)
    order_item = OrderItem.objects.get(order=order, product=product)
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()
    cart_number = order.get_cart_items
    cart_subtotal = order.get_cart_total
    cart_total_items = order.get_cart_items
    cart_total = order.get_cart_total
    try:
        quantity = OrderItem.objects.get(order=order, product=product).quantity
    except OrderItem.DoesNotExist:
        quantity = 0
    return JsonResponse({
        'cart_number': cart_number,
        'cart_subtotal': cart_subtotal,
        'cart_total_items': cart_total_items,
        'cart_total': cart_total,
        'quantity': quantity,
    })



def increase_quantity(request, product_id):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.get(customer=customer, complete=False)
    product = get_object_or_404(Product, pk=product_id)
    order_item = OrderItem.objects.get(order=order, product=product)
    order_item.quantity += 1
    order_item.save()
    cart_number = order.get_cart_items
    cart_subtotal = order.get_cart_total
    cart_total_items = order.get_cart_items
    cart_total = order.get_cart_total
    singleitem_total=order_item.get_total
    return JsonResponse({
        'cart_number': cart_number,
        'cart_subtotal': cart_subtotal,
        'cart_total_items': cart_total_items,
        'cart_total': cart_total,
        "singleitem_total": singleitem_total,
    })


def remove_item(request, product_id):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.get(customer=customer, complete=False)
    product = get_object_or_404(Product, pk=product_id)
    order_item = OrderItem.objects.get(order=order, product=product)
    order_item.delete()
    cart_number = order.get_cart_items
    cart_subtotal = order.get_cart_total
    cart_total_items = order.get_cart_items
    cart_total = order.get_cart_total
    return JsonResponse({
        'cart_number': cart_number,
        'cart_subtotal': cart_subtotal,
        'cart_total_items': cart_total_items,
        'cart_total': cart_total,
    })



@never_cache
@login_required(login_url="loginpage")
def checkout(request):
    if request.method == 'POST' :
        try:
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']
        except KeyError as e:
            error_message = f"Missing field: {e.args[0]}"
            return render(request, 'checkout.html', {'error_message': error_message})
        
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        shipping_address = ShippingAddress(
            customer=customer,
            order=order,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode
        )
        shipping_address.save()
        order.complete = True
        order.save()
        messages.success(request,"Order succesfully placed")
        return redirect('homepage')
    
    if request.user.is_authenticated:
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        if not items:
            error_message = "Your cart is empty"
            return render(request, 'checkout.html', {'error_message': error_message})
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0}
    context={'items':items,'order':order}
    return render(request,"checkout.html",context)

def contact(request):
    if request.method=="POST":
        if request.user.is_authenticated:
            name = request.user.username
            email = request.user.email
            subject =request.POST["subject"] 
            message = request.POST["message"] 
            contacts=Contact(name=name,email=email,subject=subject,message=message)
            contacts.save()
            messages.success(request,"we will contact you soon")
            return redirect("homepage")
        else:
            name = request.POST["name"]
            email = request.POST["email"]
            subject =request.POST["subject"] 
            message = request.POST["message"] 
            contacts=Contact(name=name,email=email,subject=subject,message=message)
            contacts.save()
            messages.success(request,"we will contact you soon")
            return redirect("homepage")
    return render(request,"contact.html")



def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        products = Product.objects.filter(name__icontains=query)
        results = list(products)
    return render(request, 'search_results.html', {'results': results})

def autosearch(request):
    query = request.GET['term']
    product_names = []
    if query:
        products = Product.objects.filter(name__istartswith=query)
        for product in products:
            product_names.append(product.name)
        return JsonResponse(product_names, safe=False)
    return JsonResponse([], safe=False)
