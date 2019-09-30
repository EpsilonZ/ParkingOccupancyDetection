import subprocess
import json
import cv2
import os.path
import time
import os
import collections


cam = cv2.VideoCapture(-1)
img_counter = 0

detection_occured = 0

img0 = 0
img1 = 0

img0_gray = 0
img1_gray = 0

parkingStatus = {}

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


def configure_parking_bounding_boxes_according_to_granularity(granularityBox, parkingBoundingBoxesDictionary):
	for key in parkingBoundingBoxesDictionary.keys():
		parkingBoundingBoxesDictionary[key]["left"] += granularityBox
		parkingBoundingBoxesDictionary[key]["top"] += granularityBox
		parkingBoundingBoxesDictionary[key]["right"] -= granularityBox
		parkingBoundingBoxesDictionary[key]["bottom"] -= granularityBox
	

def convert_detections_generated_file_to_dict():
	detectionsFile = open("detections.txt", "r")
	lines = detectionsFile.readlines()
	vehicleDetectionsDictionary = collections.defaultdict(dict)
	lineNumDebug = 0
	for line in lines:
		try:
			features = line.split(" ")
			vehicleKey = str(features[1])
			vehicleDetectionsDictionary[vehicleKey]["id"] = int(features[1])
			vehicleDetectionsDictionary[vehicleKey]["left"] = int(features[3])
			vehicleDetectionsDictionary[vehicleKey]["top"] = int(features[5])
			vehicleDetectionsDictionary[vehicleKey]["right"] = int(features[7])
			#on the last element we :-1 so we delete the \n of the end of the line
			vehicleDetectionsDictionary[vehicleKey]["bottom"] = int(features[9][:-1])
			lineNumDebug  = lineNumDebug + 1
		except:
			print("Corrupt " + str(lineNumDebug) + " line , please check it after the execution as something went wrong...")
			pass

	return vehicleDetectionsDictionary

def check_if_vehicle_fits_parking(parkingBoundingBox, vehicleBoundingBox):
	
	isParkingOccupied = False

	leftParking = parkingBoundingBox["left"]
	topParking = parkingBoundingBox["top"]
	rightParking = parkingBoundingBox["right"]
	bottomParking = parkingBoundingBox["bottom"]

	leftVehicleDetected = vehicleBoundingBox["left"]
	topVehicleDetected = vehicleBoundingBox["top"]
	rightVehicleDetected = vehicleBoundingBox["right"]
	bottomVehicleDetected = vehicleBoundingBox["bottom"]

	if(leftVehicleDetected < leftParking and topVehicleDetected < topParking and rightVehicleDetected > rightParking and bottomVehicleDetected > bottomParking):
		isParkingOccupied = True

	return isParkingOccupied

def check_if_state_has_really_changed(vehicleDetectionsDictionary):
	for keyParking in parkingBoundingBoxesDictionary.keys():
		parkingBoundingBox =  parkingBoundingBoxesDictionary[keyParking]
		for keyVehicle in vehicleDetectionsDictionary.keys():
			occupied = check_if_vehicle_fits_parking(parkingBoundingBox, vehicleDetectionsDictionary[keyVehicle])
			parkingStatus[keyParking] = occupied
			if(occupied):
				print("Parking occupied by")
				print("VEHICLE BOUNDING BOX")
				print(vehicleDetectionsDictionary[keyVehicle])
				print("PARKING BOUNDING BOX")
				print(parkingBoundingBox)
				break

	print(parkingStatus)

			
def show_results():
	
	imgName = str((img_counter+1%2)) + ".png"

	img = cv2.imread("opencv_frame_{}.png".format((	img_counter+1)%2))

	for key in parkingBoundingBoxesDictionary.keys():
		isOccupied = parkingStatus[key]

		x = parkingBoundingBoxesDictionary[key]["left"]
		y = parkingBoundingBoxesDictionary[key]["top"]
		w = parkingBoundingBoxesDictionary[key]["right"]
		h = parkingBoundingBoxesDictionary[key]["bottom"]

		color = (0,255,0)

		if(isOccupied):
			color = (0,0,255)

		cv2.rectangle(img, (x, y), (w, h), color, 2)

	cv2.imshow('Parking occupancy', img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
		

def process_anomaly_detection():
	vehicleDetectionsDictionary = convert_detections_generated_file_to_dict()
	check_if_state_has_really_changed(vehicleDetectionsDictionary)
	print(vehicleDetectionsDictionary)
	show_results()


if __name__ == "__main__":

	output_helper()

	granularityBox = 20
	print("Granularity box is set to 40. This is the default value, please check if it works for your case, in case it doesn't, just modify it until it does")


	with open('parkingInfo.json') as f:
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
			
			#We compare if the two images have changed and therefore a state change has potentially occured

			#METHOD 1: Comparing image sizes
			#size_bytes_image0 = os.path.getsize("opencv_frame_0.png")
			#size_bytes_image1 = os.path.getsize("opencv_frame_1.png")
			#size_bytes_diff = abs(size_bytes_image1-size_bytes_image0)
			#print("The size in bytes difference between the two images is " + str(size_bytes_diff))
			
			#METHOD 2: Norm diff between images offered by cv2
			distL1 = cv2.norm(img0, img1, cv2.NORM_L1)
			distL2 = cv2.norm(img0, img1, cv2.NORM_L2)
			print("Diff con norm L1: " + str(distL1))
			print("Diff con norm L2: " + str(distL2))

			#METHOD 3: Check bookmarks for skit image diff
			#TODO

			#The comparison values will depend on tests made on the parking. It will vary depending on the distance we are from the parking and the zoom that is applied (also 
			#daylight/light)

			#if(size_bytes_diff > 1000):
			if(distL2>4000):
				print("High difference between images detected, proceding to detect parking availability")
				subprocess.call(["../darknet/darknet", "detector", "test", "../darknet/cfg/coco.data", "../darknet/cfg/yolov3.cfg", "../darknet/yolov3.weights", "opencv_frame_" + 
				str((img_counter+1)%2) + ".png"], stdout=FNULL, stderr=subprocess.STDOUT)
		
				#subprocess.call(["cp", "../darknet/detections.txt", "detectionsOnTest.txt"])
				process_anomaly_detection()
				detection_occured = 1
				print("done")
			time.sleep(1)

		else:
			detection_occured = 0


