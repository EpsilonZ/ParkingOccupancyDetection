#image cropping
import cv2
import numpy as pd
import json
import collections
import sys


if(len(sys.argv) != 3):
	print("Usage: python3 parkingspotdetector.py detectionsFile.txt imageWhereDetectionsWhereMade.jpg")
else:
	print("-------------------------------------------------------------")

	print("EpsilonZ")

	print("-------------------------------------------------------------")

	print("This is the main program to configure parking spots in order to afterwards detect presence or not on them so we can get the availability")
	print("Please, follow the steps carefully and watch out for the prompt messages...")

	print("-------------------------------------------------------------")

	print("Now I'll read the detections file in order to detect which are the parking spots")

	detectionsFile = open(sys.argv[1], "r")
	lines = detectionsFile.readlines()
	parkingDictionary = collections.defaultdict(dict)
	lineNumDebug = 0
	for line in lines:
		try:
			features = line.split(" ")
			parkingKey = str(features[1])
			parkingDictionary[parkingKey]["id"] = int(features[1])
			parkingDictionary[parkingKey]["left"] = int(features[3])
			parkingDictionary[parkingKey]["top"] = int(features[5])
			parkingDictionary[parkingKey]["right"] = int(features[7])
			#on the last element we :-1 so we delete the \n of the end of the line
			parkingDictionary[parkingKey]["bottom"] = int(features[9][:-1])
			lineNumDebug  = lineNumDebug + 1
		except:
			print("Corrupt " + str(lineNumDebug) + " line , please check it after the execution as something went wrong...")
			pass

	print("Parking list detected correctly, proceding to establish bounding boxes around parking spots...")

	boundingBoxParkingsDictionary = collections.defaultdict(dict)

	for key in parkingDictionary.keys():
		parking = parkingDictionary[key]
		boundingBoxParkingsDictionary[key]["id"] = parking["id"]
		boundingBoxParkingsDictionary[key]["left"] = parking["left"]
		boundingBoxParkingsDictionary[key]["top"] = parking["top"]
		boundingBoxParkingsDictionary[key]["right"] = parking["right"]
		boundingBoxParkingsDictionary[key]["bottom"] = parking["bottom"]

	print(boundingBoxParkingsDictionary)


	print("Parking bounding boxes are set succesfully")

	print("Now, I'll show you what I've done. Please check if everything is correct, otherwise your intervention will be necessary as I couldn't detect more.")
	
	deleteKeys = []

	img = cv2.imread(sys.argv[2])
	for key in boundingBoxParkingsDictionary.keys():
		parking = boundingBoxParkingsDictionary[key]
		y = parking["top"]
		x = parking["left"]
		h = parking["bottom"]
		w = parking["right"]

		img = cv2.imread(sys.argv[2])
		customimg = img
		cv2.rectangle(customimg, (x, y), (w, h), (255,0,0), 2)
		cv2.imshow('Original', customimg)
		
		crop = img[y:h, x:w]
		cv2.imshow('Parking' + str(parking["id"]) , crop)
		cv2.waitKey(0)
		userCheck = str(input("Is this parking correctly detected? Y/N: "))
		if(userCheck == "N" or userCheck == "n"):
			deleteKeys.append(key)
			print("Parking wrongly detected deleted")
		cv2.destroyAllWindows()

	for deleteKey in deleteKeys:
		boundingBoxParkingsDictionary.pop(deleteKey,None)

	userCheck = str(input('Is everything correct? Y/N: '))

	print("Reordering parking ids in case some of them were deleted...")
	boundingBoxParkingsReorderedKeys = collections.defaultdict(dict)
	iterNum = 0
	for key in boundingBoxParkingsDictionary.keys():
		boundingBoxParkingsReorderedKeys[str(iterNum)] = boundingBoxParkingsDictionary[key] 
		iterNum  = iterNum + 1


	if (userCheck=='Y' or userCheck=='y'):
		print("Exiting program...")

	elif (userCheck=='N' or userCheck=='n'):
		print("Please enter coordinates of the bounding boxes you want to add to this configuration")
		print("Before diving into the entering of the bounding boxes coordinates please take note from them from the original image. Once you are done press any key")
		cv2.imshow('Original', img)
		cv2.waitKey(0)
		userParkingAdding = 1
		while(userParkingAdding==1):
			y = int(input("Enter the top pixels of the bounding box parking: "))
			x = int(input("Enter the left pixels of the bounding box parking: "))
			h = int(input("Enter the bottom pixels of the bounding box parking: "))
			w = int(input("Enter the right pixels of the bounding box parking: "))
			parkingId = max(boundingBoxParkingsDictionary.keys()) + 1

			boundingBoxParkingsReorderedKeys[str(parkingId)]["top"] = y
			boundingBoxParkingsReorderedKeys[str(parkingId)]["left"] = x
			boundingBoxParkingsReorderedKeys[str(parkingId)]["bottom"] = h
			boundingBoxParkingsReorderedKeys[str(parkingId)]["right"] = w

			crop = img[y:h, x:w]
			cv2.imshow('Parking you want to add', crop)
			cv2.waitKey(0)
			userParkingAdding = str(input("Do you want to keep adding parking bounding boxes? Y/N: "))
			if(userParkingAdding=="n" or userParkingAdding=="N"):
				userParkingAdding = 0


	print("Writing JSON result configuration into parkingInfo.json...")

	parkingListJSON = json.dumps(boundingBoxParkingsReorderedKeys)
	print(parkingListJSON)

	with open('parkingInfo.json', 'w') as f:
	    json.dump(parkingListJSON, f)


