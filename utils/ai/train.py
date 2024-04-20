import os
import numpy as np
import keras
import matplotlib.pyplot as plt
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.models import Sequential
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

def load_data(directory):
    """
    Load image data from a directory.
    """
    filenames = os.listdir(directory)
    data = []
    labels = []
    for i, filename in enumerate(filenames):
        images = np.load(os.path.join(directory, filename))
        # for img in images:
        #     imgplot = plt.imshow(img.reshape(28, 28), cmap='gray')
        #     plt.show()
        labels.extend([i] * len(images))
        data.extend(images)
    return np.array(data), np.array(labels)

def preprocess_data(data, labels, slice_train_base=120000, test_size=0.1):
    """
    Preprocess the data: scale images, shuffle, and split into training and testing sets.
    """
    data = data.astype('float32') / 255.
    indices = np.random.permutation(len(data))
    data, labels = data[indices], labels[indices]
    slice_train = slice_train_base // len(np.unique(labels))
    data, labels = data[:slice_train], labels[:slice_train]
    x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=test_size, random_state=42)
    return x_train, x_test, y_train, y_test

def build_model(input_shape, num_classes):
    """
    Build the CNN model.
    """
    model = Sequential([
        Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape),
        Conv2D(64, (3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    return model

def plot_curves(history):
    """
    Plot training and validation loss and accuracy curves.
    """
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], 'r', label='Training loss')
    plt.plot(history.history['val_loss'], 'b', label='Validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], 'r', label='Training accuracy')
    plt.plot(history.history['val_accuracy'], 'b', label='Validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.show()

def main():
    # Parameters
    batch_size = 512
    slice_train_base = 120000
    epochs = 200
    img_rows, img_cols = 28, 28
    mypath = "data/"

    # Load data
    data, labels = load_data(mypath)

    # Preprocess data
    x_train, x_test, y_train, y_test = preprocess_data(data, labels, slice_train_base=slice_train_base)

    # Reshape input data
    input_shape = (img_rows, img_cols, 1)
    x_train = x_train.reshape(x_train.shape[0], *input_shape)
    x_test = x_test.reshape(x_test.shape[0], *input_shape)

    # Convert class vectors to binary class matrices
    num_classes = len(np.unique(labels))
    y_train = to_categorical(y_train, num_classes)
    y_test = to_categorical(y_test, num_classes)

    # Build model
    model = build_model(input_shape, num_classes)

    # Compile model
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])

    # Train model
    history = model.fit(x_train, y_train,
                        batch_size=batch_size,
                        epochs=epochs,
                        verbose=1,
                        validation_data=(x_test, y_test))

    # Plot training curves
    plot_curves(history)

    # Save model
    model.save('model_image.h5')

    # Evaluate model
    score = model.evaluate(x_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

if __name__ == "__main__":
    main()
