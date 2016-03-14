#!/usr/bin/env python

import signal
import subprocess
import sys
import os
import pickle

from os import mkfifo, path, remove
from time import sleep

video_width = '1280'
video_height = '720'
video_fps = '25'
video_time = '86400000'  # big enough to keep it going for a looong time
video_bit_rate = '1800000'

named_pipe_location = "/tmp/live.h264"
m3u8_location = "./stream.m3u8"

rasp_vid_args = ['/usr/bin/raspivid', '-vf', '-w', video_width, '-h', video_height, '-fps',
                 video_fps, '-t', video_time, '-b', video_bit_rate, '-o', named_pipe_location]

ffmpeg_segment_time = '1'
ffmpeg_segment_size = '10'

ffmpeg_vid_args = ['/usr/local/bin/ffmpeg', '-y', '-i', named_pipe_location, '-c:v', 'copy', '-map', ' 0:0', '-f', 'ssegment', '-segment_time', ffmpeg_segment_time, '-segment_format',
                   'mpegts', '-segment_list', m3u8_location, '-segment_list_size', ffmpeg_segment_size, '-segment_list_flags', 'live', '-segment_wrap', ffmpeg_segment_size, '%08d.ts']

main_loop_flag = True
ffmpeg_proc = None
rasp_vid_proc = None


def sigint_handler(signal, frame):
    if ffmpeg_proc:
        ffmpeg_proc.kill()
    if rasp_vid_proc:
        rasp_vid_proc.kill()
    clean_up()

signal.signal(signal.SIGINT, sigint_handler)


def main():

    os.system("killall ffmpeg")
    os.system("killall raspivid")

    clean_up()

    mkfifo(named_pipe_location)

    rasp_vid_proc = subprocess.Popen(rasp_vid_args)
    ffmpeg_proc = subprocess.Popen(ffmpeg_vid_args)

    rasp_vid_proc.wait()
    ffmpeg_proc.wait()

    return 0


def clean_up():
    [os.remove(os.path.join('.', f))
     for f in os.listdir(".") if f.endswith(".ts")]
    if (path.exists(named_pipe_location)):
        remove(named_pipe_location)
    if (path.exists(m3u8_location)):
        remove(m3u8_location)

if __name__ == '__main__':
    main()
