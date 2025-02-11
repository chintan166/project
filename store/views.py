from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.decorators import login_required
from .models import Product, Cart,Category,Order,UserProfile
from .forms import ProductForm,CustomUserCreationForm
from django.http import Http404,HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


def home(request):
    
    
    # Fetching two specific categories
    category_1 = get_object_or_404(Category, id=1)  # Assuming category_id = 1 for the first category
    category_2 = get_object_or_404(Category, id=2)  # Assuming category_id = 2 for the second category

    # Fetching products based on categories
    products_category_1 = Product.objects.filter(category=category_1)
    products_category_2 = Product.objects.filter(category=category_2)
    
    #fetch all category
    categories = Category.objects.all()
    
    
    
    
    # Passing categories and products to the template
    return render(request, 'home.html', {
        'category_1': category_1,
        'category_2': category_2,
        'products_category_1': products_category_1,
        'products_category_2': products_category_2,
        'categories': categories,
    })

# Category page displaying products of a specific category
def category_detail(request, url):
    category = get_object_or_404(Category, url=url)  # Fetch by 'url' field
    products = Product.objects.filter(category=category)  # Fetch products by category
    return render(request, 'category_detail.html', {'category': category, 'products': products})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a UserProfile for the newly registered user
            UserProfile.objects.create(user=user,address=form.cleaned_data['address'], contact_number=form.cleaned_data['contact_number'])
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use .get() to avoid key errors
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'login.html')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            messages.success(request, 'Login successful!')
            # Redirect to the select_template page (or any other page)
            return redirect('home')
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)  # Logs the user out
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')  # Redirect to home or any page you prefer

def product_list(request):
    products = Product.objects.all()  # Get all products from the database
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, product_id):
    # Fetch the product by ID
    product = get_object_or_404(Product, pk=product_id)
    
    context = {
        'product': product,
    }

    return render(request, 'product_detail.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Ensure to handle uploaded files
        if form.is_valid():
            form.save()
            return redirect('product_list')  # Redirect to the product list or detail page
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found!')
        return redirect('product_list')

    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not logged in

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.products.add(product)
    cart.save()
    messages.success(request, 'Product added to cart!')
    return redirect('cart')

@login_required
def cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None
        messages.error(request, "No cart found!")
        return redirect('home')

    total_price = sum([product.price for product in cart.products.all()])  # Calculate total price

    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})


@login_required
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None
        messages.error(request, "No cart found!")
        return redirect('home')

    if not cart.products.all():
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    total_price = sum([product.price for product in cart.products.all()])

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_price=total_price)
        order.products.set(cart.products.all())
        order.status = Order.PENDING
        
         # Handle QR Code Upload
        qr_code_image = request.FILES.get('qr_code')
        if qr_code_image:
            order.qr_code_image = qr_code_image
        order.save()
    

        # Send email notification to the admin

        # Clear the cart after the order is placed
        cart.products.clear()
        cart.save()

        messages.success(request, 'Your order has been placed successfully and is awaiting approval!')
        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'checkout.html', {
        'cart': cart,
        'total_price': total_price
    })

@login_required
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def admin_approve_order(request, order_id, action):
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to perform this action.", status=403)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    if action == 'approve':
        order.status = Order.APPROVED
        order.save()

        # Notify the user that the order is approved
       

    elif action == 'reject':
        order.status = Order.REJECTED
        order.save()

        # Notify the user that the order is rejected
        

    return redirect('admin_orders')



@login_required
def my_account(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('home')

    cart = None  # Initialize the cart variable to None

    # Check if the user has any pending orders
    if Order.objects.filter(user=request.user, status=Order.PENDING).exists():
        messages.error(request, "You cannot access your account while your order is pending approval.")
        return redirect(my_accounts)  # No need to check for cart here


    orders = Order.objects.filter(user=request.user)
    
    return render(request, 'my_account.html', {'orders': orders})


def my_accounts(request):
    message = "Your account is currently in pending mode. The admin will review your details, and once approved, you'll be able to download your project. Thank you for your patience!"
    return render(request, 'my_accounts.html', {'message': message})

    