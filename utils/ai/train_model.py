import os
import sys
import numpy as np
import keras
import matplotlib.pyplot as plt
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.models import Sequential, load_model
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    block = int(round(barLength*progress))
    bar = "#"*block + "-"*(barLength-block)
    text = f"\rReading image data: [{bar}] {round(progress * 100, 2)}%"
    sys.stdout.write(text)

epochs = []
accuracies = []
val_accuracies = []
losses = []
val_losses = []

def epoch_callback(epoch, log):
    epochs.append(epoch)
    accuracies.append(log["accuracy"])
    val_accuracies.append(log["val_accuracy"])
    losses.append(log["loss"])
    val_losses.append(log["val_loss"])
    update_plots()
    plt.pause(0.01)

def update_plots():
    plt.close()

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(losses, "r", label="Training loss")
    plt.plot(val_losses, "b", label="Validation loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(accuracies, "r", label="Training accuracy")
    plt.plot(val_accuracies, "b", label="Validation accuracy")
    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.legend()

# Parameters
batch_size = 300 # 300
category_slice_length = 10000 # 8000
category_count = 50
validation_data_proportion = 0.1
epoch_count = 100 # 1
img_rows, img_cols = 28, 28
data_path = "data/"
model_path = "models/"
model_name = "t4_cat50"
load_model_from = "models/model_t3_cat50_lr05.keras"

train_data = []
val_data = []
train_labels = []
val_labels = []

# load training data
categories_file = open("categories.txt")
categories = categories_file.readlines()[:category_count]
data_files = os.listdir(data_path)[:category_count]

for i, filename in enumerate(data_files):
    shuffled = np.load(os.path.join(data_path, filename))
    np.random.shuffle(shuffled)
    images = shuffled[:category_slice_length]
    split_index = round(len(images) * validation_data_proportion)
    val_images, train_images = images[:split_index], images[split_index:]
    train_labels.extend([i] * len(train_images))
    val_labels.extend([i] * len(val_images))
    train_data.extend(train_images)
    val_data.extend(val_images)
    update_progress(i / (category_count - 1))

# preprocess training data and split into training and validation sets
data_length = len(train_data) + len(val_data)

print(f"\nPreprocessing {data_length} images, this might take a while...")

train_data, val_data = np.array(train_data).astype("float32") / 255., np.array(val_data).astype("float32") / 255.
input_shape = (img_rows, img_cols, 1)
train_data = train_data.reshape(train_data.shape[0], *input_shape)
val_data = val_data.reshape(val_data.shape[0], *input_shape)
train_labels = to_categorical(train_labels, category_count)
val_labels = to_categorical(val_labels, category_count)

print(f"Preprocessed {data_length} images")

# Build model
print("Building/Loading model...")

if load_model_from is not None:
    model = load_model(load_model_from)
else:
    model = Sequential([
            Conv2D(32, kernel_size=(3, 3), activation="relu", input_shape=input_shape),
            Conv2D(64, (3, 3), activation="relu"),
            MaxPooling2D(pool_size=(2, 2)),
            Dropout(0.25),
            Flatten(),
            Dense(128, activation="relu"),
            Dropout(0.5),
            Dense(category_count, activation="softmax")
        ])

# Compile model
print("Model built! Compiling model...")

model.compile(loss=keras.losses.categorical_crossentropy,
                optimizer=keras.optimizers.Adadelta(learning_rate=0.5),
                metrics=["accuracy"])

# Train model
print("Model compiled, starting training...")

history = model.fit(train_data, train_labels,
                    batch_size=batch_size,
                    epochs=epoch_count,
                    verbose=1,
                    validation_data=(val_data, val_labels))
                    # callbacks=[keras.callbacks.LambdaCallback(on_epoch_end=lambda epoch, logs: epoch_callback(epoch, logs))])


# model_json = model.to_json()

# with open("model_image.json", "w") as json_file:
#     json_file.write(model_json) 

# model.save("model_image.h5")
print('Saving model...')
model.save(f"{model_path}model_{model_name}.keras")

accuracies = history.history["accuracy"]
val_accuracies = history.history["val_accuracy"]
losses = history.history["loss"]
val_losses = history.history["val_loss"]

update_plots()
plt.show()

# Evaluate model
print('Evaluating model...')
score = model.evaluate(val_data, val_labels, verbose=0)
print("Test loss:", score[0])
print("Test accuracy:", score[1])
