import os
import sys
import numpy as np
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # nopep8
import keras
import matplotlib.pyplot as plt
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.models import Sequential
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical


def update_progress(progress):
    barLength = 20  # Modify this to change the length of the progress bar
    block = int(round(barLength*progress))
    bar = "#"*block + "-"*(barLength-block)
    text = f"\rLoading image data: [{bar}] {round(progress * 100, 2)}%"
    sys.stdout.write(text)


def load_data(directory):
    """
    Load image data
    """
    filenames = os.listdir(directory)
    labels = []
    data = []
    samples_max_length = 10_000

    for i, filename in enumerate(filenames):
        images = np.load(os.path.join(directory, filename))[
            :samples_max_length]
        labels.extend([i] * len(images))
        data.extend(images)
        update_progress(i / (len(filenames) - 1))

    print(f'\nSuccessfully read {len(filenames)} files')

    return np.array(data), np.array(labels)


def preprocess_data(data, labels, slice_train_base=120000, test_size=0.1):
    """
    Preprocess the data: scale images, shuffle, and split into training and testing sets.
    """
    data_length = len(data)
    print(
        f'Preprocessing {data_length} chunks of image data, this might take a while...')
    data = data.astype('float32') / 255.
    indices = np.random.permutation(len(data))
    data, labels = data[indices], labels[indices]
    slice_train = slice_train_base // len(np.unique(labels))
    data, labels = data[:slice_train], labels[:slice_train]
    x_train, x_test, y_train, y_test = train_test_split(
        data, labels, test_size=test_size, random_state=42)
    print(f'Preprocessed {data_length} chunks of image data')
    return x_train, x_test, y_train, y_test


def build_model(input_shape, num_classes):
    """
    Build the CNN model.
    """
    model = Sequential([
        Conv2D(32, kernel_size=(3, 3), activation='relu',
               input_shape=input_shape),
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


epochs = []
accuracies = []
val_accuracies = []
losses = []
val_losses = []


def update_plots(epoch, log):
    epochs.append(epoch)
    accuracies.append(log['accuracy'])
    val_accuracies.append(log['val_accuracy'])
    losses.append(log['loss'])
    val_losses.append(log['val_loss'])

    """
    Update training and validation loss and accuracy plots dynamically during training.
    """
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(losses, 'r', label='Training loss')
    plt.plot(val_losses, 'b', label='Validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(accuracies, 'r', label='Training accuracy')
    plt.plot(val_accuracies, 'b', label='Validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.pause(0.01)  # Pause to update the plots


def main():
    # Parameters
    batch_size = 512
    slice_train_base = 120000
    epochs = 20
    img_rows, img_cols = 28, 28
    mypath = "data50/"

    # Load data
    data, labels = load_data(mypath)

    # Preprocess data
    x_train, x_test, y_train, y_test = preprocess_data(
        data, labels, slice_train_base=slice_train_base)

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
    # callbacks=[keras.callbacks.LambdaCallback(on_epoch_end=lambda epoch, logs: update_plots(epoch, logs))])

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
