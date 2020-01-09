# EDGE

## INSTALL

You'll need to install OpenCV library!

### SPECIFY REKOGNITION HARDWARE (NVIDIA GRAPHIC CARD)

__If you do not have an NVIDIA Graphic Card look for SPECIFY REKOGNITION HARDWARE (CPU BASED) header__

NVIDIA has done an amazing work at it's amazing libraries and that's why they are widly used. That's why we'll need to install them to perform rekognitions with darknet software:

1. Install latest CUDA library following NVIDIA instructions

### SPECIFY REKOGNITION HARDWARE (CPU BASED)

Head to darknet-modified/darknet/Makefile file with your favorite editor and change this line:

```
GPU=1
```

To:

```
GPU=0
```

Now head to darknet-modified/darknet/ and recompile everything:

```
make
```
__Note: ignore warnings that may appear, everything is good:)__

### Test

## 1. Detecting parking spots (this will only be done once per a set of parking spots!)

Go to darknet-modified/darknet/ directory and execute the following command:

```
./darknet detect cfg/yolov3.cfg yolov3.weights realParking.png
```

And now you'll see the following result:

 ![Allt text](edge_readme_media/edgerekognition.png)

With the following results printed on cmd:

 ![Allt text](edge_readme_media/edgeboundingboxes.png)

Once we have done this we'll copy the bounding boxes result to a file called __detections.txt__ with the bounding box output:

```


```

## 2. Detect parking occupancy (this will be running 24/7 based on parking spot bounding boxes detection!)


