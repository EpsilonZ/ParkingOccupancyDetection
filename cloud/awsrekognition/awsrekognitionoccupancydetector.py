import subprocess
import json
import cv2
import os.path
import time
import os
import collections
import boto3
import csv


cam = cv2.VideoCapture(0)
img_counter = 0

detection_occured = 0

img0 = 0
img1 = 0

img0_gray = 0
img1_gray = 0

image_width = 0
image_height = 0

parkingStatus = {}

print("Configuring boto3 client")
with open('credentials.csv', 'r') as credentialsFile:
	next(credentialsFile)
	reader = csv.reader(credentialsFile)
	for line in reader:
		access_key_id = line[2]
		secret_access_key = line[3]

client = boto3.client('rekognition', 
		      aws_access_key_id = access_key_id,
		      aws_secret_access_key = secret_access_key)


def send_image_to_aws_rekognition(imageName):
	with open(imageName,'rb') as source_image:
		source_bytes = source_image.read()


	#with 2 detects car + license plate
	#with 3 detects vehicle + car + licenseplate
	response = client.detect_labels(Image={'Bytes':source_bytes},
						MaxLabels=3)

	return response

def output_helper():

	print("-------------------------------------------------------------")

	print("EpsilonZ")

	print("-------------------------------------------------------------")

	print("This is the program to detect occupancy of the parking")
	print("Please, follow the steps carefully and watch out for the prompt messages...")

	print("-------------------------------------------------------------")

	print("Now I'll read the JSON configuration with the parking spots previously detected by the parkingspotdetector.py")


def take_photo():
	global cam
	global img_counter
	global img0
	global img1
	global detection_occured
	iterNumToGetLastImage = 40
	ret, frame = cam.read()
	if(detection_occured):
		for i in range(iterNumToGetLastImage):
			ret, frame = cam.read()
	else:
		for i in range(10):
			ret, frame = cam.read()

	img_name = "opencv_frame_{}.png".format(img_counter)
	img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	cv2.imwrite(img_name, img_gray)
	print("{} written!".format(img_name))
	if(img_counter==0):
		img0_gray = img_gray
		img0 = frame
	else:
		img1 = frame
		img1_gray = img_gray
	img_counter = (img_counter + 1) % 2


def lookForImageDiffFromBoundingBoxes(parkingBoundingBoxesDictionary):

	isThereAnyDiffOnImage = False

	for boundingBoxKey in parkingBoundingBoxesDictionary.keys():

		#We compare if the two images have changed and therefore a state change has potentially occured

		#METHOD 1: Comparing image sizes
		#size_bytes_image0 = os.path.getsize("opencv_frame_0.png")
		#size_bytes_image1 = os.path.getsize("opencv_frame_1.png")
		#size_bytes_diff = abs(size_bytes_image1-size_bytes_image0)
		#print("The size in bytes difference between the two images is " + str(size_bytes_diff))

		print(boundingBoxKey)

		crop0 = img0[parkingBoundingBoxesDictionary[boundingBoxKey]['Top']:parkingBoundingBoxesDictionary[boundingBoxKey]['Height'], \
			     parkingBoundingBoxesDictionary[boundingBoxKey]['Left']:parkingBoundingBoxesDictionary[boundingBoxKey]['Width']]

		crop1 = img1[parkingBoundingBoxesDictionary[boundingBoxKey]['Top']:parkingBoundingBoxesDictionary[boundingBoxKey]['Height'], \
			     parkingBoundingBoxesDictionary[boundingBoxKey]['Left']:parkingBoundingBoxesDictionary[boundingBoxKey]['Width']]

		
		distL1 = cv2.norm(crop0, crop1, cv2.NORM_L1)
		distL2 = cv2.norm(crop0, crop1, cv2.NORM_L2)
		print("Diff con norm L1: " + str(distL1))
		print("Diff con norm L2: " + str(distL2))

		#cv2.imshow('Crop0', crop0)
		#cv2.imshow('Crop1', crop1)
		#cv2.waitKey(0)
		#METHOD 3: Check bookmarks for skit image diff
		#TODO

		#The comparison values will depend on tests made on the parking. It will vary depending on the distance we are from the parking and the zoom that is applied (also 
		#daylight/light)

		#if(size_bytes_diff > 1000):
		if(distL2>4000):
			isThereAnyDiffOnImage = True
			break

	return isThereAnyDiffOnImage


def configure_parking_bounding_boxes_according_to_granularity(granularityBox, parkingBoundingBoxesDictionary):
	for key in parkingBoundingBoxesDictionary.keys():
		parkingBoundingBoxesDictionary[key]['Left'] += granularityBox
		parkingBoundingBoxesDictionary[key]['Top'] += granularityBox
		parkingBoundingBoxesDictionary[key]['Width'] -= granularityBox
		parkingBoundingBoxesDictionary[key]['Height'] -= granularityBox
	

def check_if_vehicle_fits_parking(parkingBoundingBox, vehicleBoundingBox):
	
	print(vehicleBoundingBox)

	vehicleBoundingBox = vehicleBoundingBox['BoundingBox']

	isParkingOccupied = False

	leftParking = parkingBoundingBox['Left']
	topParking = parkingBoundingBox['Top']
	rightParking = parkingBoundingBox['Width']
	bottomParking = parkingBoundingBox['Height']

	leftVehicleDetected = int(vehicleBoundingBox['Left'] * image_width)
	topVehicleDetected = int(vehicleBoundingBox['Top'] * image_height)
	rightVehicleDetected = int(vehicleBoundingBox['Width'] * image_width + leftVehicleDetected)
	bottomVehicleDetected = int(vehicleBoundingBox['Height'] * image_height + topVehicleDetected)

	if(leftVehicleDetected < leftParking and topVehicleDetected < topParking and rightVehicleDetected > rightParking and bottomVehicleDetected > bottomParking):
		isParkingOccupied = True

	return isParkingOccupied


def check_if_state_has_really_changed(carsBoundingBoxesArray):
	for keyParking in parkingBoundingBoxesDictionary.keys():
		parkingBoundingBox =  parkingBoundingBoxesDictionary[keyParking]
		for vehicleBoundingBox in carsBoundingBoxesArray:
			occupied = check_if_vehicle_fits_parking(parkingBoundingBox, vehicleBoundingBox)
			parkingStatus[keyParking] = occupied
			if(occupied):
				print("Parking occupied by")
				print("VEHICLE BOUNDING BOX")
				print(vehicleBoundingBox)
				print("PARKING BOUNDING BOX")
				print(parkingBoundingBox)
				break

	print(parkingStatus)

			
def show_results():
	
	imgName = str((img_counter+1%2)) + ".png"

	img = cv2.imread("opencv_frame_{}.png".format((	img_counter+1)%2))

	for key in parkingBoundingBoxesDictionary.keys():
		isOccupied = parkingStatus[key]

		x = parkingBoundingBoxesDictionary[key]['Left']
		y = parkingBoundingBoxesDictionary[key]['Top']
		w = parkingBoundingBoxesDictionary[key]['Width']
		h = parkingBoundingBoxesDictionary[key]['Height']

		color = (0,255,0)

		if(isOccupied):
			color = (0,0,255)

		cv2.rectangle(img, (x, y), (w, h), color, 2)

	cv2.imshow('Parking occupancy', img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
		

def find_cars_json_element(jsonResponseDetections):
	#print("Labels: " + response['Labels']['V)
	i = 0
	vehicleLabelFound = False
	print(jsonResponseDetections)
	while (not vehicleLabelFound and i < len(jsonResponseDetections['Labels']) ):
		elem = jsonResponseDetections['Labels'][i]['Name']
		if(elem=='Car'):
			vehicleLabelFound = True
		else:
			i = i + 1
		print('------------')
		print(elem)
		print('------------')

	carsBoundingBoxesJSONArray = []

	if(vehicleLabelFound):
		carsBoundingBoxesJSONArray = jsonResponseDetections['Labels'][i]['Instances']

	return carsBoundingBoxesJSONArray


def process_anomaly_detection(jsonResponseDetections):

	carsBoundingBoxesJSONArray = find_cars_json_element(jsonResponseDetections)
	print(carsBoundingBoxesJSONArray)
	if(len(carsBoundingBoxesJSONArray)>0):
		
		check_if_state_has_really_changed(carsBoundingBoxesJSONArray)
		show_results()

	else:
		print("Bounding boxes array vehicle detections, please check...")


if __name__ == "__main__":

	output_helper()

	granularityBox = 20
	print("Granularity box is set to 40. This is the default value, please check if it works for your case, in case it doesn't, just modify it until it does")


	with open('parkingBoundingBoxesGenerated.json') as f:
		parkingBoundingBoxesDictionary = json.load(f)
		parkingBoundingBoxesDictionary = json.loads(parkingBoundingBoxesDictionary)
	  

	print(parkingBoundingBoxesDictionary)
	print("-----------------------")
	configure_parking_bounding_boxes_according_to_granularity(granularityBox, parkingBoundingBoxesDictionary)
	print(parkingBoundingBoxesDictionary)

	#We take first image so we don't have to check on the while if we took a first photo
	take_photo()

	take_photo()

	#to redirect output from recognitions of darknet yolo
	FNULL = open(os.devnull, 'w')

	#this variable will help us when an anomaly is detected
	detectedAnomaly = 0

	iterTurn = 0

	while True:

		take_photo()

		if(detection_occured==0):

			highDiffDetected = lookForImageDiffFromBoundingBoxes(parkingBoundingBoxesDictionary)
			if(highDiffDetected):
				print("High difference between images detected, proceding to detect parking availability")
				imageName = "opencv_frame_" + str((img_counter+1)%2) + ".png"
				imgFoo = cv2.imread(imageName)
				image_height, image_width, channels = imgFoo.shape
				#jsonDetectionsResponse = send_image_to_aws_rekognition(imageName)
				#process_anomaly_detection(jsonDetectionsResponse)
				detection_occured = 1
				print("done")

			time.sleep(1)

		else:
			detection_occured = 0


