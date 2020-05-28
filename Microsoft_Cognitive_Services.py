
import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import json
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, \
    OperationStatusType

import cognitive_face as CF

FACE_SUBSCRIPTION_KEY = "e9fa3a8292fc470c85db68cadc806961"
FACE_SUBSCRIPTION_KEY = "b0c394ce0c8d43219876638135bc8cbb"
FACE_ENDPOINT = "https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect"
FACE_ENDPOINT_LIB = "https://westcentralus.api.cognitive.microsoft.com/face/v1.0/"
COMPUTER_VISION_ENDPOINT = "https://westcentralus.api.cognitive.microsoft.com/"

# Set the FACE_SUBSCRIPTION_KEY environment variable with your key as the value.
# This key will serve all examples in this document.
os.environ['FACE_SUBSCRIPTION_KEY'] = FACE_SUBSCRIPTION_KEY
KEY = os.environ['FACE_SUBSCRIPTION_KEY']

# Set the FACE_ENDPOINT environment variable with the endpoint from your Face service in Azure.
# This endpoint will be used in all examples in this quickstart.
os.environ['COMPUTER_VISION_ENDPOINT'] = COMPUTER_VISION_ENDPOINT
os.environ['FACE_ENDPOINT'] = FACE_ENDPOINT
ENDPOINT = os.environ['COMPUTER_VISION_ENDPOINT']

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

### Определение лиц на изображении ###
# Detect a face in an image that contains a single face
single_face_image_url = 'https://www.biography.com/.image/t_share/MTQ1MzAyNzYzOTgxNTE0NTEz/john-f-kennedy---mini-biography.jpg'
single_image_name = os.path.basename(single_face_image_url)
detected_faces = face_client.face.detect_with_url(url=single_face_image_url)
if not detected_faces:
    raise Exception('No face detected from image {}'.format(single_image_name))

# Display the detected face ID in the first single-face image.
# Face IDs are used for comparison to faces (their IDs) detected in other images.
print('Detected face ID from', single_image_name, ':')
for face in detected_faces: print(face.face_id)
print()

# Save this ID for use in Find Similar
first_image_face_ID = detected_faces[0].face_id

### Отображение лиц и их выделение рамкой ###
# Detect a face in an image that contains a single face
single_face_image_url = 'https://i.ibb.co/RTnn06h/image.jpg'
single_image_name = os.path.basename(single_face_image_url)
params = {
                'returnFaceId': 'true',
                'returnFaceLandmarks': 'false',
                'returnRectangle': 'true',
                'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,'
                                        'accessories,blur,exposure,noise',
            }
headers = {'Ocp-Apim-Subscription-Key': FACE_SUBSCRIPTION_KEY}
response = requests.post(FACE_ENDPOINT, params=params,
                         headers=headers, json={"url": single_face_image_url})
detected_faces = response.json()

if not detected_faces:
    raise Exception('No face detected from image {}'.format(single_image_name))


# Convert width height to a point in a rectangle
def getRectangle(faceDictionary):
    rect = faceDictionary['faceRectangle']
    left = rect['left']
    top = rect['top']
    right = left + rect['width']
    bottom = top + rect['height']
    return ((left, top), (right, bottom))


# Download the image from the url
response = requests.get(single_face_image_url)
img = Image.open(BytesIO(response.content))

# For each face returned use the face rectangle and draw a red box.
print('Drawing rectangle around face... see popup for results.')
draw = ImageDraw.Draw(img)
for n, face in enumerate(detected_faces):
    draw.rectangle(getRectangle(face), outline='red')
    text = 'age: '+str(face['faceAttributes']['age'])
    font = ImageFont.truetype("arial.ttf", 22, encoding='UTF-8')
    w, h = font.getsize(text)
    x, y = getRectangle(face)[0][0], getRectangle(face)[1][1]
    draw.rectangle((x, y, x + w, y + h), fill='black')
    draw.text((x, y), text,fill="red", font=font, stroke_fill='green')

    print('человек номер - ', n)
    face_attributes = face['faceAttributes']
    print("пол: ", face_attributes['gender'])
    print("возраст: ", face_attributes['age'])
    print("есть ли очки?: ", face_attributes['glasses'])
    print('Эмоция: ')
    for key, value in face_attributes['emotion'].items():
        print('{}: {}'.format(key, value))

# Display the image in the users default image browser.
img.show()