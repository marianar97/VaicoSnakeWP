import numpy as np
import h5py

def _sorted(element):
    return int(element[:-4])
    
def which_image(image_name):    
    return image_name[:-4]

    
def parse_Y(Y):
    m, t, v = Y.shape
    new_Y = np.zeros((m,v))
    for i in range(m):
        new_Y[i] = Y[i, 0, :]
    return new_Y

def join(path, list_of_dir, label_path):
    full_path = []
    for dir in list_of_dir:
        full_path.append( (path + dir ,  label_path + dir + '.txt'))
    
    return full_path

def get_dict(labels_path):
    frames_dict = {}
    person_dict = {}    
    _instances = 0
        
    with open(labels_path, "r") as f:
        file_l = f.readlines()
        for line in file_l: 
            _instances += 1
            current_line = line.split()
            if(len(current_line) == 11):
                person_id , x, y, w, h, frame_number, _, _, _, class_object, action = current_line
            elif(len(current_line) == 12):
                person_id , x, y, w, h, frame_number, _, _, _, class_object, action1, action2 = current_line
                action = action1 + action2
            else:
                person_id , x, y, w, h, frame_number, _, _, _, class_object = current_line
                action = '"Empty"'
                
            if(person_id in person_dict):
                person_dict[person_id].append((frame_number,x,y,w,h,action))
            else:
                person_dict[person_id] = [(frame_number,x,y,w,h,action)]
                
            if(frame_number in frames_dict):
                frames_dict[frame_number].append((person_id ,x,y,w,h,action))
            else:
                frames_dict[frame_number] = [(person_id, x,y,w,h,action)]
    #print(_instances)
    return  person_dict

def get_Y_many_to_one(Y):
    m, t, volume = Y.shape
    new_Y = np.zeros((m,volume))
    for i in range(m):
        new_Y[i] = Y[i, 0, :]
    return new_Y

def save(X, Y, path):
    hf = h5py.File(path, 'w')
    hf.create_dataset('x', data=X)
    hf.create_dataset('y', data=Y)
    hf.close()

def read(path):
    hf = h5py.File(path, 'r')
    X = hf.get('x')
    Y = hf.get('y')
    return np.array(X),np.array(Y)

def convert_coordinates(x,y,w,h):
    x = int((int(x) * 1280) / 3840) 
    y = int((int(y) * 720) / 2160)
    w = int((int(w) * 1280) / 3840) 
    h = int((int(h) * 720) / 2160)
    return x,y,w,h
