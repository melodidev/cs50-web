import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.paginator import Paginator
import datetime

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import *    

posts_per_page = 5

def index(request):
    return render(request, 'network/index.html')

@csrf_exempt
def posts(request):
    
    if request.method == "POST":
        return new_post(request)

    elif request.method == "GET":
        return all_posts(request)

    
@login_required
def new_post(request):
    # Check if content exists
    data = json.loads(request.body)
    if data == [""]:
        return JsonResponse({
            "error": "Content cannot be blank."
        }, status=400)

    try:
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"User does not exist."
        }, status=400)

    # Get content
    content = data.get("content", "")
    if (content == ""):
        return JsonResponse({"Content cannot be blank."}, status=400)

    post = Post(
        user_id=user,
        content=content,
        time=datetime.datetime.now()
    )
    post.save()

    return JsonResponse({"message": "Post sent successfully."}, status=201)

def all_posts(request):
    if 'username' in request.GET:
        username = request.GET['username']
        user_id = User.objects.get(username=username)
        posts = Post.objects.filter(user_id=user_id)
    elif 'following' in request.GET:
        follows = Follow.objects.filter(follower=request.user)
        user_ids = [follow.followed_user.id for follow in follows]
        posts = Post.objects.filter(user_id__in=user_ids)
    else:
        posts = Post.objects.all()

    posts = posts.order_by("-time").all()

    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page', 1)
    current_page = paginator.page(page_number)

    page_obj = None
    if paginator.num_pages > 1:
        page_obj = paginator.get_page(page_number)

    data = []
    for post in current_page.object_list:
        item = post.serialize()
        item["is_current"] = item["user"]["id"] == request.user.id
        # like count per post
        like_count = Like.objects.filter(post_id=post.id).count()
        item["like_count"] = like_count
        # current user was liked the post or not
        liked_post = Like.objects.filter(post_id=post.id, user_id=request.user.id)
        if liked_post:
            item["was_liked"] = True
            item["like_id"] = liked_post[0].id
        else:
            item["was_liked"] = False
        
        data.append(item)

    data = {
        'posts': data,
        'pagination': render_to_string('network/partials/pagination.html', {'page_obj': page_obj})
    }

    return JsonResponse(data, safe=False)

def following(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    follows = Follow.objects.filter(follower=request.user)
    user_ids = [follow.followed_user.id for follow in follows]
    return render(request, 'network/following.html')

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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
def like_post(request):
    if not request.user.is_authenticated:
        return render(request, "network/login.html")

    # Check if content exists
    data = json.loads(request.body)
    if data == [""]:
        return JsonResponse({
            "error": "Content cannot be blank."
        }, status=400)

    try:
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"User does not exist."
        }, status=400)

    user = User.objects.get(username=request.user)
    post_id = data.get("post_id", "")
    post = Post.objects.get(id=post_id)

    like = Like(
        user_id=user,
        post_id=post
    )
    like.save()

    return JsonResponse({"message": "Post liked successfully."}, status=201)

@csrf_exempt
def delete_like(request, like_id):
    like = Like.objects.get(id=like_id)
    like.delete()

    return JsonResponse({"message": "Like deleted successfully."}, status=201)

@csrf_exempt
def edit(request, post_id):
    # Check if content exists
    data = json.loads(request.body)
    if data == [""]:
        return JsonResponse({
            "error": "Content cannot be blank."
        }, status=400)

    user = User.objects.get(username=request.user)
    edited_content = data.get("content", "")

    if (edited_content == ""):
        return JsonResponse({"Content cannot be blank."}, status=400)

    post = Post.objects.get(id=post_id)
    post.content = edited_content
    post.save()

    return JsonResponse({"message": "Post edited successfully."}, status=201)

@csrf_exempt
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()

    return JsonResponse({"message": "Post deleted successfully."}, status=201)

def user(request, username):
    if request.method == "GET":
        user = User.objects.get(username=username)
        avatar = user.avatar_url
        bio = user.bio
        following = Follow.objects.filter(follower=user.id).count()
        followers = Follow.objects.filter(followed_user=user.id).count()
        if Follow.objects.filter(follower=request.user.id, followed_user=user.id):
            was_followed = True
        else:
            was_followed = False

        return render(request, "network/user.html", {
            "username": username,
            "avatar": avatar,
            "bio": bio,
            "following": following,
            "followers": followers,
            "was_followed": was_followed,
            "user_id": user.id,
        })

@csrf_exempt
def follow(request, user_id):
    if request.user.id == user_id:
        return JsonResponse({
            "error": "No."
        }, status=400)

    follower = User.objects.get(id=request.user.id)
    followed_user = User.objects.get(id=user_id)
    try:
        follow = Follow.objects.get(follower=follower, followed_user=followed_user)
    except:
        follow = None

    if request.method == "POST":
        if follow:
            return JsonResponse({
                "error": "Already followed."
            }, status=400)

        follow = Follow(
            follower=follower,
            followed_user=followed_user
        )
        follow.save()

        return JsonResponse({"message": "User followed successfully."}, status=201)

    if request.method == "DELETE":
        if follow:
            follow.delete()

        return JsonResponse({"message": "User unfollowed successfully."}, status=201)

# def pagination(request, post_list, post_number):
#     if len(post_list) > post_number:
#         paginator = Paginator(post_list, post_number)
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#         return page_obj
#     return None