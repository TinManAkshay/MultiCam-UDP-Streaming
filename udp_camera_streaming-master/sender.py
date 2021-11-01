#!/usr/bin/env python

from __future__ import division
import cv2,imutils
import numpy as np
import socket
import struct
import math
import time

BUFF_SIZE = 65536

fps,st,frames_to_count,cnt = (0,0,20,0)

class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown

    def __init__(self, sock, port, addr="192.168.1.17"):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        global fps,st,frames_to_count,cnt
        WIDTH = 400
        img = imutils.resize(img,width=WIDTH)
        compress_img = cv2.imencode('.jpg', img,[cv2.IMWRITE_JPEG_QUALITY,80])[1]
        img = cv2.putText(img,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        cv2.imshow('TRANSMITTING VIDEO',img)
        
        dat = compress_img.tostring()
        size = len(dat)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1
            if cnt == frames_to_count:
                try:
                    fps = round(frames_to_count/(time.time()-st))
                    st=time.time()
                    cnt=0
                except:
                    pass
            cnt+=1


def main():
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket created")
    port = 12345
    
    fs = FrameSegment(s, port)
    socket_address = (fs.addr,fs.port)
    print("Listening at: ", socket_address)
    #msg,receiver_addr = s.recvfrom(BUFF_SIZE)
    #print(msg)
    
    print("Detecting the USB Camera")
    cap = cv2.VideoCapture(0)
    
    while (cap.isOpened()):
        _, frame = cap.read()
        fs.udp_frame(frame)
    cap.release()
    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    main()