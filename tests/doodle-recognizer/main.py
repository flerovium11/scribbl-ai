import numpy as np
import keras.models
from keras.models import model_from_json
import imageio
from skimage.transform import resize
import sys
import os

def init(): 
    json_file = open('model_image.json','r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    
    #load weights into new model
    loaded_model.load_weights("model_image.h5")
    print("Loaded Model from disk")

    loaded_model.compile(loss='categorical_crossentropy', optimizer=keras.optimizers.Adadelta(), metrics=['accuracy'])

    return loaded_model

def convertImage(img_path):
    x = imageio.imread(img_path, mode='F')
    x = np.invert(x.astype(np.uint8))
    x = resize(x, (28, 28), anti_aliasing=True)
    x = x.reshape(1, 28, 28, 1).astype('float32')
    return x

def predictImage(img_path, model):
    x = convertImage(img_path)
    out = model.predict(x)
    print(out)
    prediction = np.argmax(out, axis=1)
    return prediction

if __name__ == "__main__":
    # Load model
    model_image = init()
    image_path = 'output_image.png'
    mypath = "data/"
    txt_name_list = [filename for filename in os.listdir(mypath) if filename.endswith('.npy')]
    categories = [val.replace('full_numpy_bitmap_', '').replace('.npy', '') for val in txt_name_list]

    # Make prediction
    prediction = predictImage(image_path, model_image)
    print("Prediction:", categories[prediction[0]])
