#!/usr/bin/env python

from __future__ import division
import cv2, imutils
import numpy as np
import socket
import struct
import time

MAX_DGRAM = 2**16
fps,st,frames_to_count,cnt = (0,0,20,0)

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break

def main():
    """ Getting image udp frame &
    concate before decode and output image """
    message = b'Hello'
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('192.168.1.17', 12345))
    #s.sendto(message, ('192.168.1.17', 12345))
    dat = b''
    dump_buffer(s)
    global fps,st,frames_to_count,cnt
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            img = cv2.putText(img,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
            cv2.imshow('Live Video Streaming via UDP', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''
        if cnt == frames_to_count:
            try:
                fps = round(frames_to_count/(time.time()-st))
                st=time.time()
                cnt=0
            except:
                pass
        cnt+=1

            

    # cap.release()
    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    main()
