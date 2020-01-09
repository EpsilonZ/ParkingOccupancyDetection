# EDGE

# INSTALL

You'll need to install OpenCV library!

## SPECIFY REKOGNITION HARDWARE (NVIDIA GRAPHIC CARD)

__If you do not have an NVIDIA Graphic Card look for SPECIFY REKOGNITION HARDWARE (CPU BASED) header__

NVIDIA has done an amazing work at it's amazing libraries and that's why they are widly used. That's why we'll need to install them to perform rekognitions with darknet software:

1. Install latest CUDA library following NVIDIA instructions

## SPECIFY REKOGNITION HARDWARE (CPU BASED)

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


TODO
