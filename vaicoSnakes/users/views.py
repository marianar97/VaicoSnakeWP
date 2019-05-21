from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User

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
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib.patches as mpatches

import random
import string

from celery import task
from celery.signals import worker_init, worker_process_init

yolo_graph = None
cnn_graph = None
detector = None
_act = None

@worker_process_init.connect()
def on_worker_init(**_):

    global yolo_graph , cnn_graph, detector, _act

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
        fs = FileSystemStorage('/code/media/' + str(request.user.id))
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
        #logged_in_user_posts = Result.objects.filter(user=request.user)
        #for b in logged_in_user_posts:
            #b.activities = b.activities.split(',')
            #b.instances = b.instances.split(',')
        #frames2.delay()
        #frames(name)
        
        frames.delay(request.user.id, name)

        # POST creando un registro que diga "Procesando..."
        return render(request, 'charts/loading.html')
    else:
        return render(request, 'users/feed.html')

def get_links(users):
    #Get images for user
    NotImplementedError

@task(name="process_video")
def frames(user_id, name, n=20):
    #print('../media/', name)
    # print(sys.path.append(os.path.realpath('../media/'+name)))

    dir = '/code/media/' + str(user_id)
    inf_dir = os.path.join(dir,'inf_output')
    frames_dir = os.path.join(dir, 'frames')
    yolo_output_dir = os.path.join(dir, 'yolo_output')

    if not os.path.exists(inf_dir):
        os.makedirs(inf_dir)

    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)

    if not os.path.exists(yolo_output_dir):
        os.makedirs(yolo_output_dir)

    filename = os.path.join(dir, name)
    cap = cv.VideoCapture(filename)
    amount_of_frames = cap.get(cv.CAP_PROP_FRAME_COUNT)
    frame_step = 1
    _frames = []
    predictions = []
    images = []
    img_name = randomStringDigits(6)
    for i in range(1,int(cap.get(cv.CAP_PROP_FRAME_COUNT)  ),frame_step):
        cap.set(1, i)  # Where frame_no is the frame you want
        ret, frame = cap.read()
        cv.imwrite(os.path.join(frames_dir, (img_name + 'img%d.png'%i)) , frame)
        _frames.append(frame)
        if  i % n == 0:
            coordinates = yolo(os.path.join(frames_dir, (img_name + 'img%d.png'%(i - n + 1))), 
                               os.path.join(yolo_output_dir, (img_name + 'img%d.png'%(i - n + 1))))
            tracked_person = tracker(_frames , coordinates)
            with cnn_graph.as_default():
                predictions.append(_act.predict(tracked_person))
            save_inf(_frames[0], predictions[-1], coordinates, os.path.join(inf_dir, (img_name +'img%d.png'%(i - n + 1))))
            images.append(os.path.join('/media', str(user_id), 'inf_output', img_name +'img%d.png'%(i - n + 1)))
            _frames = []

        if i == 61:
            break
    
    images.append(os.path.join('/media', str(user_id), 'inf_output', img_name + 'graph1.png'))
    images.append(os.path.join('/media', str(user_id), 'inf_output', img_name + 'graph2.png'))
    os.remove(filename)
    graficar_acciones(os.path.join(inf_dir, (img_name + 'graph1.png')) , predictions, n)
    graficar_acciones_barra( os.path.join(inf_dir, (img_name + 'graph2.png')) , predictions, n)
    user = User.objects.get(id=user_id)
    Result.objects.create(images =images, user = user)

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
    total_acciones = len(lista_acciones)
    n_tiempos = len(acciones)
    ocurrencias = np.zeros((n_tiempos, len(lista_acciones))).astype(np.int32)
    dt = timedelta(seconds=intervalo)
    tiempos = np.arange(0, n_tiempos) 
    
    colores = .25 * np.ones((total_acciones, 4))
    n_lista_acciones = np.arange(0, total_acciones)
    norm = mpl.colors.Normalize(vmin=0, vmax=total_acciones)
    c = cm.ScalarMappable(cmap=cm.gist_rainbow, norm=norm)
    colores = c.to_rgba(n_lista_acciones)
    
    for t in range(n_tiempos):
        for i, accion in enumerate(lista_acciones):
            ocurrencia = acciones[t].count(accion)
            ocurrencias[t, i] = ocurrencia
    
    for i in range(len(lista_acciones)):
        plt.plot(tiempos, ocurrencias[:, i], color=colores[i])
    plt.legend(lista_acciones, loc='upper right')
    plt.xticks(tiempos, tiempos*dt)
    plt.yticks(tiempos)
    plt.savefig(path)
    plt.clf()


def graficar_acciones_barra(path, acciones, intervalo, lista_acciones=['standing', 'laying', 'running', 'hugging', 'sitting']):
    total_acciones = len(lista_acciones)
    n_tiempos = len(acciones) 
    ocurrencias = np.zeros((n_tiempos, len(lista_acciones))).astype(np.int32)
    dt = timedelta(seconds=intervalo)
    tiempos = np.arange(0, n_tiempos + 1) 
    
    for t in range(n_tiempos):
        for i, accion in enumerate(lista_acciones):
            ocurrencia = acciones[t].count(accion)
            ocurrencias[t, i] = ocurrencia
    
    epsilon = 2
    w = 1 / (len(acciones) + epsilon)
    posiciones = tiempos + (len(lista_acciones) + epsilon)/2 * w
    
    colores = .25 * np.ones((total_acciones, 4))
    n_lista_acciones = np.arange(0, total_acciones)
    norm = mpl.colors.Normalize(vmin=0, vmax=total_acciones)
    c = cm.ScalarMappable(cmap=cm.gist_rainbow, norm=norm)
    colores = c.to_rgba(n_lista_acciones)
    
    
    for i in range(n_tiempos):
        no_cero = np.array([[x, n] for x, n in enumerate(ocurrencias[i,:]) if n > 0])
        ocurrencias_acciones = no_cero[:,1]
        indices_acciones = no_cero[:,0]
        colores_grafica = colores[indices_acciones]
        pos = np.arange(0, len(ocurrencias_acciones)*w, w)[:len(ocurrencias_acciones)]
        desplazamiento = posiciones[i] - (pos[-1] - pos[0]) / 2
        pos = pos + desplazamiento
        plt.bar(pos, ocurrencias_acciones, width=w, color=colores_grafica)
        
    handles = []
    for n_accion in n_lista_acciones:
        handles.append(mpatches.Patch(color=colores[n_accion], label=lista_acciones[n_accion]))
    plt.legend(handles=handles, loc='best')
    plt.xticks(posiciones , tiempos*dt)
    plt.yticks(tiempos)
    plt.savefig(path)
    plt.clf()
