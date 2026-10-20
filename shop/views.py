import json
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import RegistrationForm
from .models import Profile, Product
from .services.llm import generate_product_assistance
from .services.recommendations import recommend_products
from .services.serp import search_external_products

def _role(user):
    if not user.is_authenticated:
        return None
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.role

def home(request):
    products = Product.objects.filter(active=True, stock__gt=0).select_related("seller")[:24]
    return render(request, "shop/home.html", {"products": products})

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            Profile.objects.create(user=user, role=role, seller_approved=(role == "customer"))
            send_mail(
                "Welcome to ShopSmart AI",
                "Your account was created. Email verification can be enabled with a token-based flow before production.",
                None, [user.email], fail_silently=True,
            )
            messages.success(request, "Account created. You can now sign in.")
            return redirect("login")
    else:
        form = RegistrationForm()
    return render(request, "shop/register.html", {"form": form})

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("seller_dashboard" if _role(user) == "seller" else "home")
        error = "Invalid username or password."
    return render(request, "shop/login.html", {"error": error})

@login_required
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def seller_dashboard(request):
    if _role(request.user) != "seller":
        return HttpResponseForbidden("Seller account required.")
    profile = request.user.profile
    if not profile.seller_approved and not request.user.is_staff:
        return render(request, "shop/seller_pending.html")
    products = Product.objects.filter(seller=request.user)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "").strip()
        try:
            price = Decimal(request.POST.get("price", "0"))
            stock = int(request.POST.get("stock", "0"))
            if not name or price < 0 or stock < 0:
                raise ValueError
        except (ValueError, ArithmeticError):
            messages.error(request, "Enter a product name, valid non-negative price and stock.")
        else:
            Product.objects.create(seller=request.user, name=name, description=description,
                                   category=category, price=price, stock=stock)
            messages.success(request, "Product added.")
            return redirect("seller_dashboard")
    return render(request, "shop/seller_dashboard.html", {"products": products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id, active=True)
    return render(request, "shop/product_detail.html", {"product": product})

def search(request):
    query = request.GET.get("q", "").strip()[:200]
    products = Product.objects.filter(active=True).filter(
        Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query)
    ) if query else Product.objects.none()
    ranked = recommend_products(products, query=query, limit=20)
    external = search_external_products(query, limit=8) if query else {"results": [], "enabled": False}
    return render(request, "shop/search.html", {"query": query, "products": ranked, "external": external})

@require_POST
def assistant(request):
    if not request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"error": "AJAX request required."}, status=400)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    message = str(payload.get("message", "")).strip()[:4000]
    if not message:
        return JsonResponse({"error": "Enter a shopping question."}, status=400)
    context = "\n".join(f"{p.name} | ₹{p.price} | {p.category} | stock {p.stock}"
                         for p in Product.objects.filter(active=True, stock__gt=0)[:30])
    result = generate_product_assistance(message, context)
    return JsonResponse(result)
