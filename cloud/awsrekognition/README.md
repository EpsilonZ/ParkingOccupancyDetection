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
