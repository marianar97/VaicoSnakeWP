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

from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import random
import string

from celery import task

global yolo_graph, cnn_graph
yolo_graph = tf.get_default_graph()
cnn_graph = tf.get_default_graph()

_act = Activities((20, 1024))

execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath(os.path.join(execution_path, "yolo.h5"))
detector.loadModel()


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
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
        #logged_in_user_posts = Result.objects.filter(user=request.user)
        #for b in logged_in_user_posts:
            #b.activities = b.activities.split(',')
            #b.instances = b.instances.split(',')
        #frames2.delay()
        #frames(name)
        
        frames.delay(request.user, name)

        # POST creando un registro que diga "Procesando..."
        return render(request, 'users/feed.html')
    else:
        return render(request, 'users/feed.html')

def get_links(users):
    #Get images for user
    NotImplementedError

@task(name="process_video")
def frames(user_id, name, n=20):
    print('in')
    #print('../media/', name)
    # print(sys.path.append(os.path.realpath('../media/'+name)))

    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, '..', 'media', name)

    print(filename)
    cap = cv.VideoCapture(filename)
    print(cap)
    amount_of_frames = cap.get(cv.CAP_PROP_FRAME_COUNT)
    print(amount_of_frames)
    frame_step = 1
    _frames = []
    predictions = []
    images = []
    img_name = randomStringDigits(10)
    for i in range(1,int(cap.get(cv.CAP_PROP_FRAME_COUNT)  ),frame_step):
        print('entra')
        cap.set(1, i)  # Where frame_no is the frame you want
        ret, frame = cap.read()
        cv.imwrite(os.path.join(dir, 'frames', (img_name + 'img%d.png'%i)) , frame)
        _frames.append(frame)
        if  i % n == 0:
            coordinates = yolo(os.path.join(dir, 'frames', (img_name + 'img%d.png'%(i - n + 1))), 
                               os.path.join(dir, 'yolo_output', (img_name + 'img%d.png'%(i - n + 1))))
            tracked_person = tracker(_frames , coordinates)
            print('tracked person: ', tracked_person, ' type: ', type(tracked_person))
            print('Shape', tracked_person.shape)
            with cnn_graph.as_default():
                predictions.append(_act.predict(tracked_person))
            save_inf(_frames[0], predictions[-1], coordinates, os.path.join(dir, 'inf_output', (img_name +'img%d.png'%(i - n + 1))))
            images.append(img_name +'img%d.png'%(i - n + 1))
            _frames = []

        if i == 61:
            break
    
    images.append(img_name + 'graph1.png')
    images.append(img_name + 'graph2.png')
    graficar_acciones(os.path.join(dir, 'inf_output', (img_name + 'graph1.png')) , predictions, n)
    graficar_acciones_barra( os.path.join(dir, 'inf_output', (img_name + 'graph2.png')) , predictions, n)
    print(predictions)
    Result.objects.create(images =images, user = user_id)
    return images

def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))



def save_inf(frame, preds, coords, path):

    for idx, pred in enumerate(preds):
        x, y, w, h = coords[idx]
        w = x + w
        h = y + h
        cv.rectangle(frame, (x, y), (w, h), (255, 0, 0), 2)
        cv.putText(frame, pred, (x, y-7), cv.FONT_HERSHEY_SIMPLEX,
                   0.4, (255, 255, 255), thickness=1, lineType=cv.LINE_AA)

    cv.imwrite(path, frame)


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def yolo(input_path, output_path):
    print('input path', input_path, '\noutput path ', output_path)
    with yolo_graph.as_default():
        detections = detector.detectObjectsFromImage(
            input_image=input_path, output_image_path=output_path, minimum_percentage_probability=30)
    coordinates = []
    for eachObject in detections:
        name = eachObject["name"]
        x1, y1, x2, y2 = eachObject["box_points"]
        if(name == "person"):
            coordinates.append((x1, y1, x2-x1, y2-y1))

    return coordinates


def graficar_acciones(path, acciones, intervalo, lista_acciones=['standing', 'laying', 'running', 'hugging', 'sitting']):
    n_tiempos = len(acciones)
    ocurrencias = np.zeros((n_tiempos, len(lista_acciones))).astype(np.int32)
    dt = timedelta(seconds=intervalo)
    tiempos = np.arange(0, n_tiempos)
    for t in range(n_tiempos):
        for i, accion in enumerate(lista_acciones):
            ocurrencia = acciones[t].count(accion)
            ocurrencias[t, i] = ocurrencia

    for i in range(len(lista_acciones)):
        plt.plot(tiempos, ocurrencias[:, i])
    plt.legend(lista_acciones, loc='upper right')
    plt.xticks(tiempos, tiempos*dt)
    plt.yticks(tiempos)
    plt.savefig(path)
    plt.clf()


def graficar_acciones_barra(path, acciones, intervalo, lista_acciones=['standing', 'laying', 'running', 'hugging', 'sitting']):
    n_tiempos = len(acciones)
    ocurrencias = np.zeros((n_tiempos, len(lista_acciones))).astype(np.int32)
    dt = timedelta(seconds=intervalo)
    tiempos = np.arange(0, n_tiempos)
    for t in range(n_tiempos):
        for i, accion in enumerate(lista_acciones):
            ocurrencia = acciones[t].count(accion)
            ocurrencias[t, i] = ocurrencia

    w = 1 / (len(acciones) + 1)
    for i in range(len(lista_acciones)):
        plt.bar(tiempos + i*w, ocurrencias[:, i], width=w)
    plt.legend(lista_acciones, loc='upper right')
    plt.xticks(tiempos + (len(lista_acciones) - 1)/2 * w, tiempos*dt)
    plt.yticks(tiempos)
    plt.savefig(path)
    plt.clf()
