import numpy as np
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import keras.models
from keras.models import load_model
import imageio
import matplotlib.pyplot as plt
from skimage.transform import resize
import sys
sys.path.append('../..')
from external.definitions import EXTERNAL_DIR
import os

categories_file = open(os.path.join(EXTERNAL_DIR, 'categories_german.txt'), encoding='utf-8')
german_categories = [word.replace('\n', '') for word in categories_file.readlines()]

class AI:
    def __init__(self:any, model_path:str='models/model_t1_cat50.keras')->None: 
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.model_path = model_path
        loaded_model = load_model(os.path.join(__location__, self.model_path))
        print("Loaded Model from disk")

        loaded_model.compile(loss='categorical_crossentropy', optimizer=keras.optimizers.Adadelta(), metrics=['accuracy'])
        self.model = loaded_model
        self.categories = german_categories

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
