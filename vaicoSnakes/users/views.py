from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import asyncio
import time
from charts.models import Result
from users.tasks import frames2
import cv2 as cv
import os
import sys
from imageai.Detection import ObjectDetection
from users.tracker_function import tracker
import tensorflow as tf
from users.activities import Activities

global graph
graph = tf.get_default_graph() 

_act = Activities((181,1024))

execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath( os.path.join(execution_path , "yolo.h5"))
detector.loadModel()

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
        #frames2.delay()
        frames(name)
        return render(request, 'charts/posts.html', {'posts': logged_in_user_posts})
    else:
        return render(request, 'users/feed.html')


def frames(name,n=180):
    print('in')
    #print('../media/', name)
    #print(sys.path.append(os.path.realpath('../media/'+name)))
    
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, '..','media', name)
    
    print(filename)
    cap = cv.VideoCapture(filename)
    print(cap)
    amount_of_frames = cap.get(cv.CAP_PROP_FRAME_COUNT)
    print(amount_of_frames)
    frame_step = 1
    _frames = []
    predictions = []
    for i in range(0,int(cap.get(cv.CAP_PROP_FRAME_COUNT)  ),frame_step):
        print('entra')
        cap.set(1,i) # Where frame_no is the frame you want
        ret, frame = cap.read()
        cv.imwrite(os.path.join(dir, 'frames', ('img%d.png'%i)) , frame)
        _frames.append(frame)
        if  i % n == 0 and i > 0:
            coordinates = yolo(os.path.join(dir, 'frames', ('img%d.png'%(i - n))), 
                               os.path.join(dir, 'yolo_output', ('img%d.png'%(i - n))))
            tracked_person = tracker(_frames , coordinates)
            print('tracked person: ', tracked_person, ' type: ', type(tracked_person))
            print('Shape', tracked_person.shape)
            predictions.append(_act.predict(tracked_person))
            _frames = []



def get_bounding_box(id_frame):
    raise NotImplementedError     

def tracking(first_frame, f):
        raise NotImplementedError     

def posts(request):
    return (request, 'charts/posts.html')



@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

"""
def getDetector():
    if instanced:
        return detector
    else:
        execution_path = os.getcwd()
        detector = ObjectDetection()
        detector.setModelTypeAsYOLOv3()
        detector.setModelPath( os.path.join(execution_path , "yolo.h5"))
        detector.loadModel()
"""

def yolo(input_path , output_path):
    print('input path', input_path, '\noutput path ', output_path)
    with graph.as_default():
        detections = detector.detectObjectsFromImage(input_image= input_path, output_image_path=output_path, minimum_percentage_probability=30)
    coordinates = []
    for eachObject in detections:
        name = eachObject["name"]
        x1,y1,x2,y2 = eachObject["box_points"]
        if( name == "person"):
            coordinates.append((x1,y1,x2,y2))
        
    return coordinates
