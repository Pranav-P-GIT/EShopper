from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse
from django.contrib import auth
from .models import *
from django.contrib import messages




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
            name = request.user.customer.name
            email = request.user.customer.email
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
            msg="USERNAME ALREADY EXISTS"
            return render(request,"registerpage.html",{"msg":msg})
        elif echeck:
            msg="EMAIL ALREADY EXITS"
            return render(request,"registerpage.html",{"msg":msg})
        elif password=="" or password!=repassword:
            msg="RE-PASSWORD ERROR"
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
            msg="INVALID USERNAME OR PASSWORD"
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






def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        customer = get_object_or_404(Customer, user=request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        product = get_object_or_404(Product, pk=product_id)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        order_item.quantity += 1
        order_item.save()
        messages.success(request, 'Product added to cart') 
        next_url = request.META.get('HTTP_REFERER', '/')
        return redirect(next_url)
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
        messages.success(request, 'Removed one quantity successfully')
    else:
        order_item.delete() 
        messages.success(request, 'Successfully removed item')
    return redirect('cartpage')



def increase_quantity(request, product_id):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.get(customer=customer, complete=False)
    product = get_object_or_404(Product, pk=product_id)
    order_item = OrderItem.objects.get(order=order, product=product)
    order_item.quantity += 1
    order_item.save()
    messages.success(request, 'Added quantity successfully')
    return redirect('cartpage')


def remove_item(request, product_id):
    customer = get_object_or_404(Customer, user=request.user)
    order = Order.objects.get(customer=customer, complete=False)
    product = get_object_or_404(Product, pk=product_id)
    order_item = OrderItem.objects.get(order=order, product=product)
    order_item.delete()
    messages.success(request, 'Successfully removed item')
    return redirect('cartpage')



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





def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        products = Product.objects.filter(name__icontains=query)
        results = list(products)
    return render(request, 'search_results.html', {'results': results})




def contact(request):
    if request.method=="POST":
        if request.user.is_authenticated:
            name = request.user.customer.name
            email = request.user.customer.email
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
