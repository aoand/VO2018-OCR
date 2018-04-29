#!/usr/bin/python2

import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import sys
import argparse

# minimal average of selected checkbox
CHECKBOX_THRESHOLD = 216
CHECKBOX_BAD_THRESHOLD = 120

#Pages to parse
PAGES_FOR_CLASS = {"4":(3,5,7,9,10,11)}

def find_qr(im) : 
    decodedObjects = pyzbar.decode(im)
    if len(decodedObject) > 1:
        raise RuntimeError ("Too many QR codes\n")
    
    return decodedObjects


def parse_image (name):
    im = cv2.imread(name)
    if im is None:
        sys.stderr.write("no image %s\n"%(name))
        return
    qrs = pyzbar.decode(cv2.threshold(im, 127, 255, cv2.THRESH_BINARY)[1])
    if len(qrs) == 0:
        sys.stderr.write("no QR found on image %s\n"%(name))
        return
    if len(qrs) > 1:
        sys.stderr.write("Too many QRs on image %s\n"%(name))
        return
    qr = qrs[0]
    if not('P' in qr.data):
        sys.stderr.write("No page within QR code (image %s)\n"%(name))
        return
    page = int(qr.data.split("P")[-1])
    work_id = qr.data.rsplit('P')[0].split("-")[1]
    if page in (3,5,7,9,10,11): #Pages to parse
        try:
            result = decode_result(im, qr)
            sys.stdout.write("%s\t%s\t%d\t%d\n"%(work_id, page, result[0],result[1]))
        except RuntimeError as e:
            sys.stderr.write("Not parsed:%s, %s (image: %s): %s\n"%(work_id,page, name, e))


def decode_result(im, qr_code):
    (l, t, w, h) = qr_code.rect
    w1 = h1 = 14
    result = []
    for j in range (2):
        detected = False
        for i in range (8):
            l1 = l - 252 - int(i*47.5) + 3
            t1 = t + 127 + j*53 + 3
            sub_image = im[t1:t1+h1,l1:l1+w1]
            average_color = np.average(sub_image, axis=0).min()
            if average_color < 210:
                if not(detected):
                    detected = True
                    result_j = 7-i
                else:
                    raise RuntimeError("too many detected squares: %d"%j)
        if not(detected):
            raise RuntimeError("no detected squares: %d"%j)
        result.append(result_j)
    return result

def debug_result(im, qr_code):
    (l, t, w, h) = qr_code.rect
    w1 = h1 = 14
    result = []
    for j in range (2):
        detected = False
        for i in range (8):
            l1 = l - 252 - int(i*47.5) + 3
            t1 = t + 127 + j*53 + 3
            sub_image = im[t1:t1+h1,l1:l1+w1]
            cv2.imwrite("test/%d%d.png)"%(i,j),sub_image)
            average_color = np.average(sub_image, axis=0).min()
            print average_color
            if average_color < 205:
                print 7-i
        if not(detected):
            print("no detected squares: %d"%j)


def main():
    parser = argparse.ArgumentParser(description='Parse images. Without --debug key read file names from stdin. Debug mode write pictures to /test directory if it exists.')
    parser.add_argument('--debug', help='run on one particular image and create debug information', metavar="IMG")
    args = parser.parse_args()
    if args.debug:
        name = args.debug
        im = cv2.imread(name)
        qr = pyzbar.decode(cv2.threshold(im, 127, 255, cv2.THRESH_BINARY)[1])[0]
        debug_result(im, qr)
        return()
    for l in sys.stdin:
        name = l[:-1]
        parse_image(name)


if __name__ == '__main__':
    main()
