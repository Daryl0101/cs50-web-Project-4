from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.urls import reverse
import json
from django.core.paginator import Paginator
from django.utils import timezone

from .models import User, Post

# Number of contents per page
CONTENT_PER_PAGE = 10

def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    posts = Paginator(posts, CONTENT_PER_PAGE)
    page_num = request.GET.get('page')
    page_obj = posts.get_page(page_num)
    return render(request, "network/index.html", {'page_obj': page_obj})

# User profile page
@login_required(login_url='login')
def profile(request, profile_user):
    
    profile_user = get_object_or_404(User, username = profile_user)
    posts = Post.objects.filter(user = profile_user).order_by("-timestamp")
    posts = Paginator(posts, CONTENT_PER_PAGE)
    page_num = request.GET.get('page')
    page_obj = posts.get_page(page_num)
    return render(request, "network/profile.html", {
        'page_obj': page_obj,
        'profile_user': profile_user
    })

# User following page
@login_required(login_url='login')
def follow(request):
    posts = []
    for user in request.user.following.all():
        for obj in Post.objects.filter(user = user):
            posts.append(obj)
    posts.sort(key=get_timestamp, reverse=True)
    posts = Paginator(posts, CONTENT_PER_PAGE)
    page_num = request.GET.get('page')
    page_obj = posts.get_page(page_num)
    return render(request, "network/following.html", {
        'page_obj': page_obj,
    })

# Get post timestamp
def get_timestamp(post):
    return post.timestamp


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

# Creates new post
@login_required(login_url='login')
def post(request):

    # Posting must be via POST
    if request.method != 'POST':
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check post
    data = json.loads(request.body)
    if not data.get("content").strip():
        return JsonResponse({"error": "No content!"}, status=400)

    Post.objects.create(content=data.get("content"), user=request.user)
    return JsonResponse({"message": "Post successful."}, status=201)

# Update user's following status and like status
@login_required(login_url='login')
def update(request):
    if request.method == 'PUT':
        data = json.loads(request.body)

        # Update follow or unfollow
        if data.get('profile_user') is not None:
            profile_user = User.objects.get(pk = data.get('profile_user'))
            if request.user is not profile_user:
                if profile_user in request.user.following.all():
                    request.user.following.remove(data.get('profile_user'))
                    btn_content = 'Follow'
                    btn_class = 'btn btn-outline-success follow-button'
                else:
                    request.user.following.add(data.get('profile_user'))
                    btn_content = 'Unfollow'
                    btn_class = 'btn btn-outline-danger follow-button'
                return JsonResponse({"message": "Update following successful.", "btn_content": btn_content, "btn_class": btn_class, "profile_followers": profile_user.followers.count()}, status=201)
            else:
                return JsonResponse({"message": "Update failed, a user cannot follow himself/herself"}, status=400)
        
        # Update like or unlike
        else:
            if request.user.like.filter(id = data.get('current_post')).exists():
                request.user.like.remove(data.get('current_post'))
                icon_html = 'favorite_border'
            else:
                request.user.like.add(data.get('current_post'))
                icon_html = 'favorite'
            return JsonResponse({"message": "Update likes successful.", "like_num": Post.objects.get(id = data.get('current_post')).likes.count(), 'icon_html': icon_html}, status=201)

    else:
        return JsonResponse({"error": f"{request.method} method is invalid"}, status=400)

# Edit post
@login_required(login_url='login')
def edit(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        post_id = data.get('post_id')
        if Post.objects.filter(id = post_id).exists():
            edit_post = Post.objects.get(id = post_id)
            if len(data.get('content')):
                if request.user.id == edit_post.user.id:
                    Post.objects.filter(id = post_id).update(content=data.get('content'), timestamp=timezone.now())
                    return JsonResponse({"message": "Update successful", "content": Post.objects.get(id = post_id).content, "post_id": post_id}, status=201)
                else:
                    return JsonResponse({"message": "Update Failed, cannot edit other user's post"}, status=400)
            else:
                return JsonResponse({"message": "Update Failed, post cannot be empty"}, status=400)
        else:
            return JsonResponse({"message": "No such post"}, status=400)
            
    else:
        return JsonResponse({"message": f"PUT method only, you are using method: {request.method}"}, status=400)

# Get post info before editing
@login_required(login_url='login')
def getEditTextarea(request, post_id):
    if request.method == 'GET':
        if Post.objects.filter(id = post_id).exists():
            edit_post = Post.objects.get(id = post_id)
            if request.user.id == edit_post.user.id:
                return JsonResponse({"message": "Get successful", "content": edit_post.content, "post_id": post_id}, status=201)
            else:
                return JsonResponse({"message": "Get Failed, cannot edit other user's post"}, status=400)
        else:
            return JsonResponse({"message": "No such post"}, status=400)
    else:
        return JsonResponse({"message": f"GET method only, you are using method: {request.method}"}, status=400)