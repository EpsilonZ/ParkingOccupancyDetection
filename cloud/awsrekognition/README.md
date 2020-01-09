# REQUIREMENTS

In this case you'll need to have an AWS account in order to proceed. As long as you have it set up correctly that's all you'll have to need except for python3:

```
sudo apt-get update
sudo apt-get install python3
pip3 install boto3
```

Once you've got installed python3, boto3 and created an AWS account you'll need to create a file called 'credentials.csv' within this directory which will have the needed keys for interacting with your AWS account. 'credentials.csv' will have the following contents:
```
[default]
aws_access_key_id = xxxxxxxxxxx
aws_secret_access_key = xxxxxxx
```

__NOTE__: You can config boto3 client if you don't want to have a raw and exposed keys like in this case.

And, lastly, give execution permissions to the script which will start the service:

```
chmod +x setup_parking_camera_detector.sh
```

And now, you'll be able to launch it and set it up following the cmd instructions!


__The procedure will be the same as edge detection so instead of doing 2 same explanations i'll explain the differences between each two so it's easier to you to set up both__

python3 awsrekognitionspotdetector.py --> Will take the image by theirselve and ask you the parking spots. No need of providing detections.txt or the source image. It'll do everything for you.
python3 awsrekognitionoccupancydetector.py --> Same as edge detection!
