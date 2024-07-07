import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # nopep8
import keras.models
from keras.models import model_from_json

__location__ = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__))) + '\\models'
json_file = open(os.path.join(__location__, 'model_image.json'), 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

# load weights into new model
loaded_model.load_weights(os.path.join(__location__, 'model_image.h5'))
print("Loaded Model from disk")
model_path, model_name = "models/", "t1_cat50"
loaded_model.compile(loss='categorical_crossentropy',
                     optimizer=keras.optimizers.Adadelta(), metrics=['accuracy'])
loaded_model.save(f"{model_path}model_{model_name}.keras")
