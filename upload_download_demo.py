import os, uuid, sys, json, requests
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
sys.path.append("../")
from appJar import gui
from PIL import Image

try:
	print("Azure Blob storage v12 - Python quickstart sample")
	connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
except Exception as ex:
    print('Exception:')
    print(ex)

app=gui()
app.addLabel("title", "Welcome to Aegle")   # add a label
app.setLabelBg("title", "green")                  # set the label's background to be red


import sys
sys.path.append("../")
from appJar import gui
import os
import json
import requests
api_key = 'e9a78bd98b7445c69c7a7b71ba2c0b46'
endpoint = 'https://hackbridgetest1.cognitiveservices.azure.com/vision/v2.1/ocr'
dir = 'images'
######################### Actual code that does the OCR #######################
def handler(filename):
    results = get_text(filename)
    NHSnum = parse_text(results)
    # open(NHSnum +'.txt', 'w').write(text)
    # print(NHSnum)
    return NHSnum
def parse_text(results):
    text = ''
    flag = 0
    NHSnum = ''
    for region in results['regions']:
        for line in region['lines']:
            for word in line['words']:
                text += word['text'] + ' '
                if test(word['text']):
                    flag = 4
                elif flag > 0 :
                    NHSnum += word['text']
                    flag = flag - 1
            text += '\n'
    print('Parsing Text: ' + NHSnum)
    # print(results)
#    text += NHSnum
    return NHSnum
def test(text): # check if string starts with NHS
    nhsappears = False
    if len(text) >= 3:
        if (text[0] == 'N') & (text[1] == 'H') & (text[2] == 'S'):
            nhsappears = True
    return nhsappears
def get_text(pathtoimage):
    print('processing: ' + pathtoimage)
    headers  = {
        'ocp-apim-subscription-key': api_key,
        'content-type': 'application/octet-stream'
    }
    params   = {
        'language': 'en',
        'detectorientation ': 'true'
    }
    payload = open(pathtoimage, 'rb').read()
    response = requests.post(endpoint, headers=headers, params=params, data=payload)
    results = json.loads(response.content)
    return results


def uploadbtn(btnName):
    filename = app.getEntry("image")
    # nhs_number = get_nhs_number from image

    nhs_number = handler(filename)
    nhs_number = nhs_number[7:]
    print(nhs_number)
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = nhs_number
    
    try:
    	container_client = blob_service_client.create_container(container_name)
    except ResourceExistsError:
    	container_client = blob_service_client.get_container_client(container_name)
    	

    record_name = os.path.basename(filename)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=record_name)

    with open(filename, "rb") as data:
    	blob_client.upload_blob(data)

    app.popUp("INFO", "You uploaded the file successfully")


def retrievebtn(btnName):
    ################ insert button functionality here to DOWNLOAD FROM AZURE #################
    app.popUp("INFO", "You uploaded the file successfully ")
    nhs_number = str(app.getEntry("NHSno"))
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    try: 
    	container_client = blob_service_client.get_container_client(nhs_number)
    except ResourceExistsError:
    	print("This person does not exist on the system yet")
    	return

    record_list = container_client.list_blobs()

    print(record_list)
    for record in record_list:
    	try:
    		img = Image.open(record.name)
    	except IOError:
    		print("didnt work")
    		pass



    

    # uploaded

with app.labelFrame("Upload Patient Data", colspan=2, sticky="news", expand="both"):
    app.addFileEntry("image") # file entry field
    app.button("Upload", uploadbtn) # UPLOAD button

with app.labelFrame("Retrieve Patient Data", colspan=2, sticky="news", expand="both"):
    app.addEntry("NHSno") # text entry field
    app.setEntryDefault("NHSno", "-- NHS Number --")
    app.button("Retrieve", retrievebtn) # RETRIEVE button

app.go() # starts the app interface
