#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utileties for starting video encoding and streaming."""

import os
import subprocess
import sys
import time
import uuid
import logging
import struct

def get_image(lima_tango_device):
    global LAST_FRAME

    img_data = lima_tango_device.video_last_image
    
    hfmt = ">IHHqiiHHHH"
    hsize = struct.calcsize(hfmt)
    _, _, img_mode, frame_number, width, height, _, _, _, _ = struct.unpack(
        hfmt, img_data[1][:hsize]
    )

    raw_data = img_data[1][hsize:]

    return raw_data, width, height, frame_number

def poll_image(encoder_input, device_uri):   
    from PyTango import DeviceProxy

    connected = False
    while not connected:
        try:
            logging.getLogger("HWR").info("Connecting to %s", device_uri)
            lima_tango_device = DeviceProxy(device_uri)
            lima_tango_device.ping()

        except Exception as ex:
            logging.getLogger("HWR").exception("")
            logging.getLogger("HWR").info(
                "Could not connect to %s, retrying ...", device_uri
            )
            connected = False
            time.sleep(0.2)
        else:
            connected = True

    sleep_time = lima_tango_device.video_exposure
    last_frame_number = -1
    
    while True:
        try:
            data, width, height, frame_number = get_image(lima_tango_device)

            if last_frame_number != frame_number:
                encoder_input.write(data)
                last_frame_number = frame_number

        except Exception as ex:
            print(ex)
        finally:
            time.sleep(sleep_time)

def start_video_stream(size, scale, _hash, video_mode):
    """
    Start encoding with ffmpeg and stream the video with the node
    websocket relay.

    :param str scale: Video width and height
    :param str _hash: Hash to use for relay
    :returns: Tupple with the two processes performing streaming and encoding
    :rtype: tuple
    """
    websocket_relay_js = os.path.join(os.path.dirname(__file__), "websocket-relay.js")

    FNULL = open(os.devnull, "w")

    relay = subprocess.Popen(
        ["node", websocket_relay_js, _hash, "4041", "4042"],
        close_fds=True
    )

    # Make sure that the relay is running (socket is open)
    time.sleep(2)

    size = "%sx%s" % size
    w, h = scale
    
    ffmpeg = subprocess.Popen(
        [
            "ffmpeg",
            "-f", "rawvideo",
            "-pixel_format", "rgb24",
            "-s", size,
            "-i", "-",
            "-vf", "scale=w=%s:h=%s" % (w, h),        
            "-f", "mpegts",
            "-b:v", "750000k",
            "-q:v", "4",
            "-an",
            "-vcodec", "mpeg1video",
            "http://localhost:4041/" + _hash,
        ],
        stderr=FNULL,
        stdin=subprocess.PIPE,
        shell=False,
        close_fds=True
    )

    with open("/tmp/mxcube.pid", "a") as f:
        f.write("%s %s" % (relay.pid, ffmpeg.pid))

    return relay, ffmpeg


if __name__ == "__main__":  
    try:
        video_device_uri = sys.argv[1].strip()
    except IndexError:
        video_device_uri = ""

    try:
        size = sys.argv[2].strip()
    except IndexError:
        size = "-1,-1"
    finally:
        size = tuple(size.split(","))
        
    try:
        scale = sys.argv[3].strip()
    except IndexError:
        scale = "-1,-1"
    finally:
        scale = tuple(scale.split(","))

    try:
        _hash = sys.argv[4].strip()
    except IndexError:
        _hash = "-1,-1"

    try:
        video_mode = sys.argv[5].strip()
    except IndexError:
        video_mode = "rgb24"  

    relay, ffmpeg = start_video_stream(size, scale, _hash, video_mode)
    poll_image(ffmpeg.stdin, video_device_uri)
