import csv
import boto3
import cv2
import json
import sys

cam = cv2.VideoCapture(-1)

#INITIAL SETUP FOR ENABLING AWS COMMUNICATION THROUGH PYTHON SDK
#IF ENDPOINT ERROR OCCURS JUST DO "AWS CONFIGURE" ON CMD AND RECONFIGURE REGION
#----------------------------------------------------------------

with open('credentials.csv','r') as credentialsFile:
	#skips first row	
	next(credentialsFile)
	reader = csv.reader(credentialsFile)
	for line in reader:
		access_key_id = line[2]
		secret_access_key = line[3]

client = boto3.client('rekognition',
		      aws_access_key_id = access_key_id,
		      aws_secret_access_key = secret_access_key)

#----------------------------------------------------------------


def take_photo():
	global cam
	ret, frame = cam.read()
	img_name = "parkingPhotoDetetion.png"
	img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	cv2.imwrite(img_name, img_gray)
	print("Image taken")
	return frame



def show_bounding_boxes_of_response(img, response):
	#print("Labels: " + response['Labels']['V)
	i = 0
	vehicleLabelFound = False
	while (not vehicleLabelFound and i < len(response['Labels']) ):
		elem = response['Labels'][i]['Name']
		if(elem=='Car'):
			vehicleLabelFound = True
		else:
			i = i + 1
		print('------------')
		print(elem)
		print('------------')

	if(vehicleLabelFound):

		vehicleBoundingBoxes = response['Labels'][i]['Instances']
		deleteKeys = []
		boundingBoxParkingsDictionary = {}
		itemNum = 0

		for jsonElement in vehicleBoundingBoxes:
			vehicleBoundingBox = jsonElement['BoundingBox']
			print(vehicleBoundingBox)
			x = int(vehicleBoundingBox['Left'] * image_width)
			y = int(vehicleBoundingBox['Top'] * image_height)
			w = int(vehicleBoundingBox['Width'] * image_width + x)
			h = int(vehicleBoundingBox['Height'] * image_height + y)

			print(x,y,w,h)

			img = cv2.imread(photo)
			customimg = img
			cv2.rectangle(customimg, (x,y), (w,h), (255,0,0), 2)
			cv2.imshow('Parking', customimg)

			crop = img[y:h, x:w]
			cv2.imshow('Parking' + str(itemNum) , crop)
			cv2.waitKey(0)

			userCheck = str(input('Is this parking correctly detected? Y/N: '))

			if(userCheck == "Y" or userCheck == "y"):
				vehicleBoundingBox['Left'] = x
				vehicleBoundingBox['Top'] = y
				vehicleBoundingBox['Width'] = w
				vehicleBoundingBox['Height'] = h
				boundingBoxParkingsDictionary[str(itemNum)] = vehicleBoundingBox
				print("Parking added")
				itemNum = itemNum + 1
			else:
				print("Parking not added")

			cv2.destroyAllWindows()


		userCheck = str(input('Is everything correct? Y/N: '))

		if (userCheck=='Y' or userCheck=='y'):
			print("Exiting program...")

		elif (userCheck=='N' or userCheck=='n'):
			print("Please enter coordinates of the bounding boxes you want to add to this configuration")
			print("Before diving into the entering of the bounding boxes coordinates please take note from them from the original image. Once you are done press any key")
			cv2.imshow('Original', img)
			cv2.waitKey(0)
			userParkingAdding = 1
			print(itemNum)
			while(userParkingAdding==1):
				y = int(input("Enter the top pixels of the bounding box parking: "))
				x = int(input("Enter the left pixels of the bounding box parking: "))
				h = int(input("Enter the bottom pixels of the bounding box parking: "))
				w = int(input("Enter the right pixels of the bounding box parking: "))
				parkingId = itemNum
				boundingBoxParkingsDictionary[str(parkingId)] = {}
				boundingBoxParkingsDictionary[str(parkingId)]['Left'] = x
				boundingBoxParkingsDictionary[str(parkingId)]['Top'] = y
				boundingBoxParkingsDictionary[str(parkingId)]['Width'] = w
				boundingBoxParkingsDictionary[str(parkingId)]['Height'] = h

				crop = img[y:h, x:w]
				cv2.imshow('Parking you want to add', crop)
				cv2.waitKey(0)
				userParkingAdding = str(input("Do you want to keep adding parking bounding boxes? Y/N: "))
				itemNum = itemNum + 1
				if(userParkingAdding=="n" or userParkingAdding=="N"):
					userParkingAdding = 0


		print("Writing JSON result configuration into parkingInfo.json...")

		parkingListJSON = json.dumps(boundingBoxParkingsDictionary)
		print(parkingListJSON)

		with open('parkingBoundingBoxesGenerated.json', 'w') as f:
		    json.dump(parkingListJSON, f)


	else:
		print("No vehicles found on the image")		


take_photo()

photo='parkingPhotoDetetion.png'


with open(photo,'rb') as source_image:
	source_bytes = source_image.read()


#with 2 detects car + license plate
#with 3 detects vehicle + car + licenseplate
response = client.detect_labels(Image={'Bytes':source_bytes},
					MaxLabels=3)

print(response)


#we load image onto opencv2 to show boundingboxesresults
img = cv2.imread(photo)
image_height = img.shape[0]
image_width = img.shape[1]

show_bounding_boxes_of_response(img, response)



