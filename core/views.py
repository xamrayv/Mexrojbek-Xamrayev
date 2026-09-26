from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import profile_required

from .forms import ProductForm
from .models import Category, Product
from .search import rank


def _products():
    return Product.objects.select_related("category", "author__profile")


def _own_products(user):
    """Admin hammasini, oddiy foydalanuvchi faqat o'zinikini ko'radi."""
    qs = _products()
    return qs if user.is_staff else qs.filter(author=user)


@login_required
def home(request):
    q = request.GET.get("q", "").strip()[:60]
    categories = list(Category.objects.all())
    products = _products().filter(is_vip=True)
    current = None
    found = 0

    slug = request.GET.get("category")
    if slug:
        current = get_object_or_404(Category, slug=slug)
        products = list(products.filter(category=current))
        if q:
            matched, rest = rank(products, q, lambda p: p.title)
            products = matched + rest
            found = len(matched)
    else:
        products = list(products)
        if q:
            matched, rest = rank(categories, q, lambda c: c.name)
            categories = matched + rest
            found = len(matched)

    return render(request, "core/home.html", {
        "categories": categories,
        "products": products,
        "current": current,
        "q": q,
        "found": found,
    })


@profile_required
def my_categories(request):
    categories = (
        Category.objects.filter(products__author=request.user)
        .annotate(n=Count("products"))
    )
    total = Product.objects.filter(author=request.user).count()
    return render(request, "core/mine_categories.html", {"categories": categories, "total": total})


@profile_required
def my_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = _products().filter(author=request.user, category=category)
    return render(request, "core/mine_products.html", {"category": category, "products": products})


@profile_required
def vip_view(request):
    products = _own_products(request.user).filter(is_vip=False)

    if request.method == "POST":
        ids = [i for i in request.POST.getlist("products") if i.isdigit()]
        if ids:
            count = Product.objects.filter(pk__in=products.filter(pk__in=ids).values("pk")).update(is_vip=True)
            messages.success(request, f"{count} ta mahsulot kategoriyasiga qo'shildi.")
        else:
            messages.error(request, "Avval mahsulotni belgilang.")
        return redirect("vip")

    return render(request, "core/vip.html", {"products": products})


@profile_required
def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.author = request.user
        product.save()
        if product.is_vip:
            messages.success(request, "Mahsulot qo'shildi va targ'ib qilinmoqda.")
            return redirect(f"{reverse('home')}?category={product.category.slug}")
        messages.success(request, "Mahsulot VIP bo'limiga saqlandi.")
        return redirect("vip")
    return render(request, "core/product_form.html", {"form": form})


@profile_required
def delete_categories(request):
    return render(request, "core/delete_categories.html", {"categories": Category.objects.all()})


@profile_required
def delete_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = _own_products(request.user).filter(category=category)
    return render(request, "core/delete_products.html", {"category": category, "products": products})


@profile_required
def product_delete(request, pk):
    product = get_object_or_404(_own_products(request.user), pk=pk)
    if request.method == "POST":
        category = product.category
        title = product.title
        product.delete()
        messages.success(request, f"«{title}» o'chirildi.")
        return redirect("delete_products", slug=category.slug)
    return render(request, "core/product_confirm_delete.html", {"product": product})
