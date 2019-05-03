from rnn import RNNModel
from cnn import CNNModel
import numpy as np

class Activities:

    #Define modelo RNN para actividad y CNN para caracteristicas (inicialmente propuesto)
    def __init__(self, input_shape, weight_path = 'model.h5'):

        self.rnn_model = RNNModel()
        self.rnn_model.set_model(input_shape)
        self.rnn_model.set_weights(weight_path)
        
        self.cnn_model = CNNModel()
    
    #Establecer una RNN, o modelo que reciba los mismos parametros que el metodo predict_rnn y que siga la misma signatura de metodos
    def set_rnn(self, model):
        
        self.rnn_model = model
    
    #Establecer una CNN, o modelo que reciba los mismos parametros que le modelo extract_features y que siga la misma signatura de metodos
    def set_cnn(self, model):
        
        self.cnn_model = model
    
    
    #Recibe una secuencia de frames y retorna sus caracteristicas, tamaño(m, time, height, width, channels)
    def extract_features(self, frame_seq, output_size = 1024, coordinates = None):
        m = frame_seq.shape[0]
        time = frame_seq.shape[1]
        feature_vector = np.zeros((m, time ,output_size))
        for idx in range(m):
            vector_to_predict = frame_seq[idx]
            feature_vector[idx] = self.cnn_model.predict(vector_to_predict)
            
        return feature_vector
        

    #Recibe un arreglo de tamaño (m, time, volume) retorna la predicción para cada ejemplo m
    def predict_rnn(self, features):
        predictions = self.rnn_model.predict(features)
        return predictions
    
    #Recibe una secuencia de frames y retorna sus predicciones, tamaño(m, time, height, width, channels)
    def predict(self, frames_seq, output_size = 1024 , coordinates = None):
        _feature = self.extract_features(frames_seq , output_size , coordinates)
        return self.predict_rnn(_feature)
