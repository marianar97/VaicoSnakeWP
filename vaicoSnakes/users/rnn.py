import numpy as np

from keras import backend as K
from keras.optimizers import RMSprop
from keras.models import Model
from keras.layers import Dense, Input, Dropout, LSTM, Activation, CuDNNLSTM, CuDNNGRU, GRU, GlobalMaxPool1D, BatchNormalization, Flatten

from users.utilities import read , parse_Y

class RNNModel():
    
    def __init__(self):
        
        self.model = None
    
    def set_model(self,input_shape , model = None):
    
        _input = Input(input_shape)

        X = GRU(110 , return_sequences=True)(_input)
        X = GRU(110 , return_sequences=False)(X)
        X = Dense(13)(X)
        X = Activation('softmax')(X)
        
        if model == None:
            self.model = Model(inputs=_input, outputs=X)
        else:
            self.model = model
            
    def set_weights(self, path_to_weights):
        self.model.load_weights(path_to_weights)
    
    def get_activity(self, number, activities = None):
        
        _activities = activities
        
        if _activities == None:
            _activities = {
            0 : "handshaking", 1 : "hugging" , 2 :  "reading" , 3 : "drinking" ,  4 : "pushing/pulling",
            5 : "carrying", 6 : "calling" , 7 : "running",8 : "walking", 9 : "lying", 10 : "sitting",
            11 : "standing", 12 : "empty"
            }
            
        return _activities[number]

    
    def predict(self, X, activities = None):
        converted_predictions = []
        predictions = self.model.predict(X)
        predictions = np.argmax(predictions, axis=1)
        for prediction in predictions:
            text_with_pred = self.get_activity(prediction, activities)
            converted_predictions.append(text_with_pred)
        return converted_predictions
            
    def dataGenerator(self,pathes, batch_size, flag):

        while True: #generators for keras must be infinite
            for path in pathes:
                x_train, y_train = read(path)
                y_train = parse_Y(y_train)

                totalSamps = x_train.shape[0]
                batches = totalSamps // batch_size

                if totalSamps % batch_size > 0:
                    batches+=1

                for batch in range(batches):
                    section = slice(batch*batch_size,(batch+1)*batch_size)
                    yield (x_train[section], y_train[section])

    
    def train(self,  train_pathes, ev_pathes , train_steps, val_steps,  epochs = 20,
              batch_size = 16, optimizer = None, loss = 'categorical_crossentropy', metrics = ['accuracy']):
        
        if optimizer == None:
            optimizer = RMSprop(lr=0.001, rho=0.9, epsilon=None, decay=0.0)
        
        
        self.model.compile(loss=loss, optimizer=optimizer , metrics=metrics)
        gen_evaluation = self.dataGenerator(ev_pathes, batch_size, 'eval')
        gen_train = self.dataGenerator(train_pathes, batch_size, 'train')
        history = self.model.fit_generator(gen_train,
                    steps_per_epoch =  train_steps, 
                    validation_data = gen_evaluation,
                    validation_steps = val_steps,
                    epochs = epochs)
        
        return history
                   
        
    