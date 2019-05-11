from keras.applications import MobileNet
from keras.models import Model
from keras import backend as K

class CNNModel:
    
    def __init__(self, include_top = True, weights = 'imagenet', 
                 model = None, transfer_layer = 'global_average_pooling2d_1'):
        
        self.model = model
        
        if self.model == None:
            self.model = MobileNet(include_top=include_top, weights=weights)            
        
        self._transfer_layer = self.model.get_layer(transfer_layer)
        self.transfer_model = Model(inputs=self.model.input,
                                    outputs=self._transfer_layer.output)
     

    def predict(self, array_of_examples):
        
        prediction = self.transfer_model.predict(array_of_examples)
        
        return prediction
    
    def describe(self):
        _input = K.int_shape(self.model.input)
        _output = K.int_shape(self._transfer_layer.output)

        description = {"input" :  _input , "output_transfer_layer" : _output , "summary" : self.model.summary()}
        return description
        