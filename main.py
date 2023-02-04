# https://deeplizard.com/learn/video/FNqp4ZY0wDY
# https://deeplizard.com/learn/video/Zrt76AIbeh4

# Importing the libraries
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.layers import Dense
from keras.models import Model
from keras.optimizers import Adam
from sklearn.metrics import confusion_matrix

import os
import random
import shutil
import json
from function import plot_confusion_matrix

# Organize data into train, valid, test dirs
os.chdir('dataset/steering-wheel')
if os.path.isdir('train/drzi/') is False:
    os.mkdir('train')
    os.mkdir('valid')
    os.mkdir('test')

    # for i in range(0, 2):
    for i in ['drzi', 'nedrzi']:
        shutil.move(f'{i}', 'train')
        os.mkdir(f'valid/{i}')
        os.mkdir(f'test/{i}')

        valid_samples = random.sample(os.listdir(f'train/{i}'), 200)
        for j in valid_samples:
            shutil.move(f'train/{i}/{j}', f'valid/{i}')

        test_samples = random.sample(os.listdir(f'train/{i}'), 100)
        for k in test_samples:
            shutil.move(f'train/{i}/{k}', f'test/{i}')
os.chdir('../..')

# Process the Data
train_path = 'dataset/steering-wheel/train'
valid_path = 'dataset/steering-wheel/valid'
test_path = 'dataset/steering-wheel/test'

# todo zmenit na verziu v3?
train_batches = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input).flow_from_directory(
    directory=train_path, target_size=(224, 224), batch_size=10)
valid_batches = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input).flow_from_directory(
    directory=valid_path, target_size=(224, 224), batch_size=10)
test_batches = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.mobilenet_v2.preprocess_input).flow_from_directory(
    directory=test_path, target_size=(224, 224), batch_size=10, shuffle=False)

print(test_batches.class_indices)

# Build The fine-tuned model
mobile = tf.keras.applications.mobilenet_v2.MobileNetV2()
mobile.summary()

x = mobile.layers[-6].output
x = tf.keras.layers.Flatten()(x)
output = Dense(units=2, activation='softmax')(x)

model = Model(inputs=mobile.input, outputs=output)

for layer in model.layers[:-23]:
    layer.trainable = False  # not trainable

model.summary()

# Train model
model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(x=train_batches,
          validation_data=valid_batches,
          epochs=30,
          verbose=2
          )

# predict sign language digits
test_labels = test_batches.classes
predictions = model.predict(x=test_batches, steps=len(test_batches), verbose=0)
cm = confusion_matrix(y_true=test_labels, y_pred=predictions.argmax(axis=1))  # confusion matrix

print(test_batches.class_indices)
class_indices = test_batches.class_indices

cm_plot_labels = ['drzi', 'nedrzi']
plot_confusion_matrix(cm=cm, classes=cm_plot_labels, title='Confusion Matrix')

# Ulozenie modelu
model_json = model.to_json()
with open('mobileNet_steering_wheel_1.json', 'w') as json_file:
    json_file.write(model_json)

from keras.models import save_model

network_saved = save_model(model, 'mobileNet_steering_wheel_1.hdf5')

# todo custom class.json
class_indices_dictionary = {}
i = 0

for class_item in class_indices:
    class_indices_dictionary[i] = [str(class_item)]
    i += 1


with open('class_index_steering_wheel_1.json', 'w') as file:
    file.write(json.dumps(class_indices_dictionary))
