from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.urls import reverse
import json
from django.core.paginator import Paginator


from .models import User, Post

# Number of contents per page
CONTENT_PER_PAGE = 10

def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    posts = Paginator(posts, CONTENT_PER_PAGE)
    page_num = request.GET.get('page')
    page_obj = posts.get_page(page_num)
    return render(request, "network/index.html", {'page_obj': page_obj})

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

@login_required(login_url='login')
def updatefollow(request):
    if request.method == 'PUT':
        data = json.loads(request.body)
        profile_user = User.objects.get(username = data.get('profile_user'))
        profile_user = profile_user.id
        if data.get('toFollow')==False:
            request.user.following.remove(profile_user)
        else:
            request.user.following.add(profile_user)
        return JsonResponse({"message": "Update successful."}, status=201)
""" def page(request, post_type, page_num):
    
    # User request all posts
    posts = []
    if post_type == 'all':
        all_post = Post.objects.all().order_by('-timestamp')
        for obj in all_post:
            posts.append(obj.serialize())
    # User request personal posts
    elif post_type == 'profile':
        all_post = Post.objects.filter(user=request.user).order_by('-timestamp')
        for obj in all_post:
            posts.append(obj.serialize())
    # User request posts by user's currently following users
    elif post_type == 'following':
        followings = request.user.following.all()
        for follow in followings:
            for post in follow.posts.all():
                posts.append(post.serialize())
                # May need to order by timestamp
    
    # Arrange the posts list into 10 posts per page
    p = Paginator(posts, 10)
    page_items = []
    for obj in p.page(page_num).object_list:
        page_items.append(obj)
    context = {
        'post_type' :post_type,
        'total_items':p.count,
        'all_posts': posts,
        'num_pages':p.num_pages,
        'page':page_num,
        'page_items' :page_items,
        'has_previous': p.page(page_num).has_previous(),
        'has_next': p.page(page_num).has_next()
    }

    if p.page(page_num).has_previous()==False:
        context['previous_page_number'] = ''
    else:
        context['previous_page_number'] = p.page(page_num).previous_page_number()

    if p.page(page_num).has_next()==False:
        context['next_page_number'] = ''
    else:
        context['next_page_number'] = p.page(page_num).next_page_number()

    return JsonResponse(context, status=201) """