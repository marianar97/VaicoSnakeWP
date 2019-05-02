from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import asyncio
import time
from users.tasks import frames
from charts.models import Result


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request,user)
            return redirect('feed')
        else: 
            return render(request, 'users/login.html', {'error': 'Invalid username or password'})
    return render(request, 'users/login.html')

@login_required
def feed(request):
    context = {}
    if request.method == "POST":
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
        logged_in_user_posts = Result.objects.filter(user=request.user)
        return render(request, 'charts/posts.html', {'posts': logged_in_user_posts})
    else:
        return render(request, 'users/feed.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
