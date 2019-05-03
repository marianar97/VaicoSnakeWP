from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import asyncio
import time
from charts.models import Result
from users.tasks import frames2
import cv2
import os
import sys


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
        for b in logged_in_user_posts:
            b.activities = b.activities.split(',')
            b.instances = b.instances.split(',')
        frames2.delay()
        frames(name)
        
        return render(request, 'charts/posts.html', {'posts': logged_in_user_posts})
    else:
        return render(request, 'users/feed.html')


def frames(name):
    print('in')
    #print('../media/', name)
    #print(sys.path.append(os.path.realpath('../media/'+name)))
    
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, '..','media', name)
    
    print(filename)
    cap = cv2.VideoCapture(filename)
    print(cap)
    amount_of_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)
    print(amount_of_frames,length)
    frame_step = 10
    
    for i in range(0,int(cap.get(cv2.CAP_PROP_FRAME_COUNT)  ),frame_step):
        print('entra')
        cap.set(1,i) # Where frame_no is the frame you want
        ret, frame = cap.read()
        cv2.imwrite(os.path.join(dir, 'frames', ('img%d.png'%i)) , frame)

def get_bounding_box(id_frame):
    raise NotImplementedError     

def tracking(first_frame, f):
        raise NotImplementedError     




@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
