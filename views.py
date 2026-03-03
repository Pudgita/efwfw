from django.shortcuts import render, get_object_or_404, redirect
from .forms import AddPostForm, LoginForm, RegisterForm, UserProfileForm, CartItemForm
from .models import Biblioteka, Cart, CartItem, Order, OrderItem
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction

def is_admin(user):
    return user.is_staff


def book_list(request):
    books = Biblioteka.objects.all().order_by('id')
    paginator = Paginator(books, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = AddPostForm()


    cart_items_count = 0
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            cart_items_count = cart.items.count()
        except Cart.DoesNotExist:
            pass

    data = {
        'form': form,
        'page_obj': page_obj,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'index.html', data)


@login_required(login_url='login')
def book_create(request):
    if request.method == 'POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            Biblioteka.objects.create(**form.cleaned_data)
    return redirect('book_list')


@user_passes_test(is_admin, login_url='book_list')
def book_update(request, book_id):
    book = get_object_or_404(Biblioteka, id=book_id)
    if request.method == 'POST':
        form = AddPostForm(request.POST)
        if form.is_valid():
            book.title = form.cleaned_data['title']
            book.author = form.cleaned_data['author']
            book.price = form.cleaned_data['price']
            book.save()
    return redirect('book_list')


@user_passes_test(is_admin, login_url='book_list')
def book_delete(request, book_id):
    book = get_object_or_404(Biblioteka, id=book_id)
    if request.method == 'POST':
        book.delete()
    return redirect('book_list')


def book_detail(request, book_id):
    book = get_object_or_404(Biblioteka, id=book_id)
    return render(request, 'add_book.html', {'book': book})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('book_list')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('book_list')
            else:
                pass
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('book_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )

            login(request, user)
            return redirect('book_list')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('book_list')


@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})


@login_required(login_url='login')
def add_to_cart(request, book_id):
    book = get_object_or_404(Biblioteka, id=book_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        book=book,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f'Количество товара "{book.title}" в корзине увеличено')
    else:
        messages.success(request, f'Товар "{book.title}" добавлен в корзину')

    return redirect('book_list')


@login_required(login_url='login')
def cart_view(request):
    try:
        cart = request.user.cart
        cart_items = cart.items.select_related('book').all()
        total_price = cart.get_total_price()
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
        cart_items = []
        total_price = 0

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required(login_url='login')
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Количество товара обновлено')
            else:
                cart_item.delete()
                messages.success(request, 'Товар удален из корзины')

    return redirect('cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.success(request, f'Товар "{book_title}" удален из корзины')
    return redirect('cart')


@login_required(login_url='login')
@transaction.atomic
def create_order(request):
    try:
        cart = request.user.cart
        cart_items = cart.items.select_related('book').all()

        if not cart_items:
            messages.warning(request, 'Корзина пуста')
            return redirect('cart')

        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            total_price=cart.get_total_price()
        )

        # Переносим товары из корзины в заказ
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=cart_item.book,
                quantity=cart_item.quantity,
                price_at_time=cart_item.book.price
            )

        # Очищаем корзину
        cart.items.all().delete()

        messages.success(request, f'Заказ #{order.id} успешно оформлен!')
        return redirect('order_detail', order_id=order.id)

    except Cart.DoesNotExist:
        messages.error(request, 'У вас нет корзины')
        return redirect('book_list')


@login_required(login_url='login')
def order_list(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})


@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('book').all()
    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items
    })



