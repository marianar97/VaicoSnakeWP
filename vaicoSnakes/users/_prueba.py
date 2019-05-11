from activities import Activities
import numpy as np
from imageai.Detection import ObjectDetection
import os

execution_path = os.getcwd()
detector  = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath( os.path.join(execution_path , "yolo.h5"))
detector.loadModel()

def yolo(input_path , output_path):
    print('input path', input_path, '\noutput path ', output_path)

    detections = detector.detectObjectsFromImage(input_image= input_path, output_image_path=output_path, minimum_percentage_probability=30)
    coordinates = []
    for eachObject in detections:
        name = eachObject["name"]
        x1,y1,x2,y2 = eachObject["box_points"]
        if( name == "person"):
            coordinates.append((x1,y1,x2,y2))
        
    return coordinates

dir = os.path.dirname(__file__)

c = yolo(os.path.join(dir, 'frames', ('img%d.png'%(0))), 
                               os.path.join(dir, 'yolo_output', ('img%d.png'%(0))))
_act = Activities((10,1024))
t = np.random.rand(1,10,224,224,3)
_act.cnn_model.describe()

print(_act.predict(t))

del _act