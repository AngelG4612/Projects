#!/usr/bin/python
import subprocess as sp
import time
import os
import datetime
from pirdetect import *
import sys
import random
"""
This script will play any of the videos listed in a random order.
Usage: python ./scareRandom.py [VideoName] [Minutes]

[VideoName] is any of video prefixes in the video_prefix list.
[Minutes] is the time value in minutes of how often you want to rotate to a different video.

Example usage would be : python ./scareRandom.py Male 5.

After each trigger of the on_motion event the script will check and determine if the time elapsed is greater than the 
value you provided in argument 2 and if the elapsed time is longer than your time setting it will randomly pick a new
video prefix and will recursively attempt to choose one that is NOT the current video prefix so it doesn't play the same 
video more than one time in sequence.

To add more or different videos just add to or modify the video_prefix list below.
If adding more videos or changing the defaults you will have to create a start image for each additional video.
The naming structure for the start images and videos are as follows.

[Prefix]ScareV.m4v (MaleScareV.m4v) or [Prefix]ScareV.mp4 (MaleScareV.mp4)
[Prefix]Start.png (MaleStart.png) 
"""


#  initialize variables

video_prefix = ["Male", "Female", "Child"] # This is the list of videos prefixes, you can add additional video
# prefixes here.
video = ["omxplayer", "filename", "-o", "both", "--win", "0 0 1920x1080", "--aspect-mode", "fill", "--no-osd",
         "--orientation", "0", "--vol", "-600"]
record = ["raspivid", "-o", "filename", "-n", "-t", "5000", "-rot", "180"]
scare_file = ""
current_prefix = ""
new_prefix = ""
image_name = ""
start_time = time.time()


def change_video():
    global start_time
    global scare_file
    global current_prefix
    global new_prefix
    elapsed_time = time.time() - start_time
    print(str("\nTime since last rotation: {0}".format(datetime.timedelta(seconds=elapsed_time))))
    if elapsed_time > (int(sys.argv[2]) * 60):
        while new_prefix == current_prefix:  # make sure we don't choose the same video
            new_prefix = video_prefix[random.randrange(len(video_prefix))]
        current_prefix = new_prefix
        scare_file = "/home/pi/Projects/Halloween/ScareMedia/{0}ScareV.mp4".format(current_prefix)
        start_time = time.time()
        show_image(current_prefix)
        print("\nUpdating Video to: {0}\n".format(current_prefix))


def getfilename():
    return "/home/pi/Projects/Halloween/Recordings/" + datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")


def sub_proc_wait(params):
    sub = sp.Popen(params)
    while sub.poll() is None:
        time.sleep(.1)


def on_motion(curr_state):
    if curr_state:
        auto_file_name = getfilename()  # Get a time stamped file name
        record[2] = auto_file_name
        sub_record = sp.Popen(record)  # Start recording to capture their fright
        video[1] = scare_file
        sub_proc_wait(video)  # Play the video to scare them
        video[1] = auto_file_name
        sub_proc_wait(video)  # Play back the video we just recorded
        change_video()


def show_image(_image_name):
    os.system("sudo fbi -a -T 1 -d /dev/fb0 -noverbose -once /home/pi/Projects/Halloween/ScareMedia/{0}Start.png".format(
        _image_name))


def start_up():
    global scare_file
    global image_name
    image_name = arg1
    scare_file = "/home/pi/Projects/Halloween/ScareMedia/{0}ScareV.mp4".format(image_name)
    show_image(image_name)
    obj_detect = detector(7)
    obj_detect.subscribe(on_motion)
    obj_detect.start()
    os.system("sudo killall -9 fbi")


if __name__ == "__main__":

    try:

        arg1 = sys.argv[1]
        if arg1 not in video_prefix:
            raise ValueError('first argument must be Male,Female or Child')
        if sys.argv[2].isdigit():
            arg2 = int(sys.argv[2])
        else:
            raise ValueError('Second argument must be a number')
    except IndexError:
        print("Usage: python ./scareRandom.py [VideoName] [Minutes]")
        sys.exit(1)
    except ValueError as x:
        print(x.message + "\nUsage: python ./scareRandom.py [VideoName] [Minutes]")
        sys.exit(1)

start_up()
