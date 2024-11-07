# -*- coding: utf-8 -*-
"""Copy of resnet50-epoch30-pneumonia.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13-nglggEVu7R5qvm1vJ9zfYdxyx1xDo4
    
    In order to use the code in google colab following commands should be uncommented and executed
    else the data should be downloaded from kaggle manually and put it inside chest_xray directory and run program
"""

# Installing kaggle inorder to download the data
#pip install kaggle

#!mkdir ~/.kaggle

#from google.colab import drive
#drive.mount('/content/drive')

#!cp /content/drive/MyDrive/kaggle.json ~/.kaggle/kaggle.json

#!chmod 600 ~/.kaggle/kaggle.json

#!kaggle datasets download -d paultimothymooney/chest-xray-pneumonia

#!unzip chest-xray-pneumonia.zip

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 21:31:21 2023

@author: bipin
"""

import numpy as np
import pandas as pd

import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import warnings
import tensorflow as tf
import glob
import random
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image

#For ignoring warnings inside console
warnings.filterwarnings("ignore")

# Directory structure
data_dir = "chest_xray"
train_dir = data_dir + "/train"
val_dir = data_dir + "/val"
test_dir = data_dir + "/test"

data_dir = train_dir
items = os.listdir(train_dir)

# Filter out class names from the items, excluding hidden directories
class_names = [item for item in items if os.path.isdir(os.path.join(train_dir, item)) and not item.startswith('.')]

#Printing file names
print(class_names)

# Method to display random images
def view_random_image(target_directory, target_class):
    target_folder = target_directory +"/"+ target_class
    random_image = random.sample(os.listdir(target_folder), 1)
    img = mpimg.imread(target_folder + "/" + random_image[0])
    plt.imshow(img)
    plt.title(target_class)
    plt.axis("off");
    return img

plt.figure(figsize=(10,10))
for i in range(12):
    plt.subplot(3,4,i+1)
    r=random.randint(0,1)
    img = view_random_image(data_dir, class_names[r])


input_path="chest_xray/"
fig, ax = plt.subplots(2, 3, figsize=(15, 7))
ax = ax.ravel()
plt.tight_layout()


#Showing sample from train, test and val directory
for i, _set in enumerate(['train', 'val', 'test']):
    set_path = input_path+_set
    ax[i].imshow(plt.imread(set_path+'/NORMAL/'+os.listdir(set_path+'/NORMAL')[0]), cmap='gray')
    ax[i].set_title('Set: {}, Condition: Normal'.format(_set))
    ax[i+3].imshow(plt.imread(set_path+'/PNEUMONIA/'+os.listdir(set_path+'/PNEUMONIA')[0]), cmap='gray')
    ax[i+3].set_title('Set: {}, Condition: Pneumonia'.format(_set))

for _set in ['train', 'val', 'test']:
    n_normal = len(os.listdir(input_path + _set + '/NORMAL'))
    n_infect = len(os.listdir(input_path + _set + '/PNEUMONIA'))
    print('Set: {}, Normal images: {}, pneumonia images: {}'.format(_set, n_normal, n_infect))

# Define image size and batch size
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32

# Create an ImageDataGenerator for data augmentation
Image_gen = ImageDataGenerator(
        rescale=1/255,
        shear_range=10,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.5, 2.0],
        width_shift_range=0.2,
        rotation_range=20,
        fill_mode='nearest'
)

val_Datagen = ImageDataGenerator(rescale = 1/255)

# Generate batches of augmented image data from the training directory
train = Image_gen.flow_from_directory(train_dir,
                                       batch_size=2,
                                       class_mode='binary',
                                       target_size=(224, 224))

# Generate batches of augmented image data from the validation directory
validation = Image_gen.flow_from_directory(val_dir,
                                       batch_size=2,
                                       class_mode='binary',
                                       target_size=(224, 224))

# Generate batches of image data from the test directory (no augmentation)
test = val_Datagen.flow_from_directory(test_dir,
                                       batch_size=2,
                                       class_mode='binary',
                                       target_size=(224, 224))

img, label = next(train)

# Define early stopping callback to stop training when validation loss does not improve
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                  patience=10)

# Define learning rate reduction callback to reduce learning rate when validation loss plateaus
lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
                                          patience=8)
  


def create_model():
    resnet_model = tf.keras.applications.ResNet50V2(
        weights='imagenet',
        include_top = False,
        input_shape = (224,224,3)
    )

    for layer in resnet_model.layers:
        layer.trainable=False

    x = resnet_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(128,activation='relu')(x)
    # output layer
    predictions = tf.keras.layers.Dense(1,activation='sigmoid')(x)

    res_model = tf.keras.Model(inputs=resnet_model.input, outputs=predictions)

    # Compiling the model
    res_model.compile(loss='binary_crossentropy', optimizer='adam',metrics=['accuracy'])
    return res_model


res_model = create_model()
res_model.summary()


# Train the model
history = res_model.fit(train,epochs=30,
                    validation_data=validation,
                     steps_per_epoch=100,
                    callbacks=[early_stopping,lr],
                    batch_size=32)

#Plot the training artifacts
train_acc = history.history['accuracy']
train_loss = history.history['loss']
val_acc = history.history['val_accuracy']
val_loss = history.history['val_loss']

epochs = range(1, len(train_acc) + 1)

# Plotting the training and validation accuracy
plt.figure(figsize=(12, 5))

# Accuracy plot
plt.subplot(1, 2, 1)
plt.plot(epochs, train_acc, 'r', label='Training Accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

# Loss plot
plt.subplot(1, 2, 2)
plt.plot(epochs, train_loss, 'r', label='Training Loss')
plt.plot(epochs, val_loss, 'b', label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()

# Evaluating the model on train and test
score = res_model.evaluate(train)

print("Train Loss: ", score[0])
print("Train Accuracy: ", score[1])

score = res_model.evaluate(test)
print("\nTest loss: ", score[0])
print("Test Accuracy: ", score[1])

# Save the trained model
res_model.save("my_resnet_model.h5")

# Randomly select 10 images and labels from the test dataset
test_images, test_labels = next(test)

# Make predictions using the trained model
predictions = res_model.predict(test_images)

# Convert predictions to binary labels: 0 (Normal) and 1 (Pneumonia)
predicted_labels = np.where(predictions > 0.5, 1, 0)

# Display the images, real labels, and predicted labels
plt.figure(figsize=(20, 14))

for i in range(2):
    plt.subplot(2, 5, i+1)
    plt.imshow(test_images[i])
    plt.title(f"True: {'Pneumonia' if test_labels[i] == 1 else 'Normal'}\nPredicted: {'Pneumonia' if predicted_labels[i] == 1 else 'Normal'}")
    plt.axis("off")

plt.tight_layout()
plt.show()

