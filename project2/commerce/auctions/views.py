from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime

from .models import User, Category, Product, Comment, Watchlist
from .forms import CreateForm, CommentForm, WatchlistForm, BidForm, CloseForm

def index(request):
    products = Product.objects.all().filter(is_open=True).order_by("id").reverse()
    categories = Category.objects.all().order_by("category_name")
    try:
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        user = None
    return render(request, "auctions/index.html", {
        "products": products,
        "user": user,
        "categories": categories
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = CreateForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.seller = User.objects.get(username=request.user)
                form.save()
                return HttpResponseRedirect(reverse("index"))
        form = CreateForm

        print(form)
        return render(request, "auctions/create.html", {
            "form": form,
            "categories": Category.objects.all().order_by("category_name")
        })
    else:
        return HttpResponseRedirect(reverse("login"))


def product(request, product_title):
    product = Product.objects.get(title=product_title)
    comments = Comment.objects.filter(product_id=product.id)
    seller_bid = product.current_bid
    bid_count = product.bid_count
    buyer = product.buyer
    comment_form = CommentForm
    watchlist_form = WatchlistForm
    bid_form = BidForm
    message = ""
    error = ""
    amount = 0
    try:
        user = User.objects.get(username=request.user)
        watchlist_item = Watchlist.objects.filter(product_id=product.id, user_id=user.id)
    except User.DoesNotExist:
        user = None
        watchlist_item = None

    if request.method == "POST":
        if "add-comment" in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                form = form.save(commit=False)
                form.product_id = product
                form.user_id = User.objects.get(username=request.user)
                form.time = datetime.datetime.now()
                form.save()

        if "watchlist-add" in request.POST:
            form = WatchlistForm(request.POST)
            if form.is_valid() and not watchlist_item:
                form = form.save(commit=False)
                form.product_id = product
                form.user_id = User.objects.get(username=request.user)
                form.save()
                watchlist_item = True

        if "watchlist-remove" in request.POST:
            form = WatchlistForm(request.POST)
            if form.is_valid() and watchlist_item:
                Watchlist.objects.filter(product_id=product.id, user_id=user.id).delete()
                watchlist_item = False

        if "make-bid" in request.POST:
            form = BidForm(request.POST, instance=product)
            if form.is_valid():
                form = form.save(commit=False)
                # If user's bid more than the seller's bid, update bid
                if form.current_bid > seller_bid:
                    amount = form.current_bid - seller_bid
                    print(amount)
                    form.current_bid_user = user
                    form.bid_count = bid_count + 1
                    form.save()
                    # message = f"Last bid maded by {user}. Increased price by {amount}."
                # Else, do not change the bid
                else:
                    form.current_bid = seller_bid
                    form.save()
                    error = "Every bid must be more than previous bid."

        if "close-listing" in request.POST:
            form = CloseForm(request.POST, instance=product)
            if form.is_valid():
                form = form.save(commit=False)
                form.buyer = product.current_bid_user
                form.is_open = False
                form.save()

    return render(request, "auctions/product.html", {
        "product": product,
        "comments": comments,
        "user": user,
        "buyer": buyer,
        "watchlist_item": watchlist_item,
        "watchlist_form": watchlist_form,
        "comment_form": comment_form,
        "bid_form": bid_form,
        "bid_count": bid_count,
        "message": message,
        "error": error,
        "current_bid_user": product.current_bid_user,
        "amount": amount,
        "categories": Category.objects.all().order_by("category_name")
    })

def user(request, username):
    user = User.objects.get(username=username)
    avatar = user.avatar_url
    active_listings = Product.objects.all().filter(seller=user.id, is_open=True).order_by("id").reverse()
    closed_listings = Product.objects.all().filter(seller=user.id, is_open=False).order_by("id").reverse()
    purchases = Product.objects.all().filter(buyer=user.id).order_by("id").reverse()
    watchlist = Watchlist.objects.all().filter(user_id=user.id).order_by("id").reverse()
    return render(request, "auctions/user.html", {
        "username": username,
        "avatar": avatar,
        "active_listings": active_listings,
        "closed_listings": closed_listings,
        "purchases": purchases,
        "watchlist": watchlist,
        "categories": Category.objects.all().order_by("category_name")
    })

def category(request, category_id):
    category = Category.objects.get(category_name=category_id.capitalize())
    products = Product.objects.all().filter(is_open=True, category_id=category.id).order_by("id").reverse()

    return render(request, "auctions/category.html", {
        "category": category_id.upper(),
        "products": products,
        "categories": Category.objects.all().order_by("category_name")
    })