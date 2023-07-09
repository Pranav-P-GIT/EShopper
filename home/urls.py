from django.urls import path
from home import views

urlpatterns = [
    path('', views.index,name='homepage'), 
    path('cart', views.cart,name='cartpage'),   
    path('checkout', views.checkout,name='checkoutpage'),   
    path('contact', views.contact,name='contactpage'),   
    path('details', views.details, name='detailpage'),     
    path('login', views.login_view, name='loginpage'),
    path('logout', views.logout,name='logoutpage'),   
    path('register', views.register,name='registerpage'), 
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  
    path('decrease-quantity/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('remove_item/<int:product_id>/', views.remove_item, name='remove_item'),
    path('search/', views.search, name='search'),
    path('autosearch/', views.autosearch, name='autosearch'),
    path('get_cart_number/', views.get_cart_number, name='get_cart_number'),

]