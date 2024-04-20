import numpy as np
import keras.models
from keras.models import model_from_json
import imageio
import matplotlib.pyplot as plt
from skimage.transform import resize
import sys
import os

class AI:
    def __init__(self:any)->None: 
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        json_file = open(os.path.join(__location__, 'model_image.json'), 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        
        #load weights into new model
        loaded_model.load_weights(os.path.join(__location__, 'model_image.h5'))
        print("Loaded Model from disk")

        loaded_model.compile(loss='categorical_crossentropy', optimizer=keras.optimizers.Adadelta(), metrics=['accuracy'])
        self.model = loaded_model

        mypath = __location__ + "/data/"
        txt_name_list = [filename for filename in os.listdir(mypath) if filename.endswith('.npy')]
        self.categories = [val.replace('full_numpy_bitmap_', '').replace('.npy', '') for val in txt_name_list]

    def convertImagePath(self:any, img_path:str)->np.array:
        img = imageio.imread(img_path, mode='F') # read the image in grayscale
        img = np.invert(img.astype(np.uint8)) # to change white to black and vice versa
        return self.shapeImage(img)

    def predictImage(self:any, img:np.array)->dict[str, any]:
        img = self.shapeImage(img)
        out = self.model.predict(img)
        return self.prediction(out[0])

    def shapeImage(self:any, img:np.array)->np.array:
        img = resize(img, (28, 28), anti_aliasing=True) # squash the image down to 28x28 pixels
        # imgplot = plt.imshow(img, cmap='gray')
        # plt.show()
        img = img.reshape(1, 28, 28, 1).astype('float32') # shape array for inputting into model
        return img

    def predictImageByPath(self:any, img_path:str)->dict[str, any]:
        x = self.convertImagePath(img_path)
        out = self.model.predict(x)
        return self.prediction(out[0])

    def prediction(self:any, out:np.array)->dict[str, any]:
        prediction = [{'certainty': number, 'category': self.categories[index]} for index, number in enumerate(out)]
        prediction = sorted(prediction, key=lambda x: x['certainty'], reverse=True)
        return prediction

if __name__ == "__main__":
    # Load model
    ai = AI()
    image_path = 'output_image.png'

    # Make prediction
    prediction = ai.predictImageByPath(image_path)
    print(prediction)
