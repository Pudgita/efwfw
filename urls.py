from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.book_create, name='book_create'),
    path('update/<int:book_id>/', views.book_update, name='book_update'),
    path('delete/<int:book_id>/', views.book_delete, name='book_delete'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),

    # Профиль пользователя
    path('profile/', views.profile_view, name='profile'),

    # Корзина
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Заказы
    path('cart/checkout/', views.create_order, name='create_order'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]