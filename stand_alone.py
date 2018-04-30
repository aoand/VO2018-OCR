#!/usr/bin/python2

import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import sys
import argparse

# minimal average of selected checkbox
CHECKBOX_THRESHOLD = 216
CHECKBOX_BAD_THRESHOLD = 100

#Pages to parse
PAGES_FOR_CLASS = {"4":(3,5,7,9,10,11)}

def find_qr(im) : 
    decodedObjects = pyzbar.decode(im)
    if len(decodedObject) > 1:
        raise RuntimeError ("Too many QR codes\n")
    
    return decodedObjects


def parse_image (name, is_debug=False):
    im = cv2.imread(name)
    if im is None:
        raise RuntimeError ("No image %s\n"%(name))
    qrs = pyzbar.decode(cv2.threshold(im, 127, 255, cv2.THRESH_BINARY)[1])
    if len(qrs) == 0:
        raise RuntimeError ("No QR found on image %s\n"%(name))
    if len(qrs) > 1:
        raise RuntimeError ("Too many QRs on image %s\n"%(name))
    qr = qrs[0]
    if not('P' in qr.data):
        raise RuntimeError ("No page in QR code (image %s)\n"%(name))
    page = int(qr.data.split("P")[-1])
    work_id = qr.data.rsplit('P')[0].split("-")[1]
    cl = work_id[0]
    if page in PAGES_FOR_CLASS[cl]:
        try:
            result = decode_result(im, qr, is_debug)
            return "%s\t%s\t%d\t%d\n"%(work_id, page, result[0],result[1])
        except RuntimeError as e:
            raise RuntimeError ("Not parsed:%s, %s (image: %s): %s\n"%(work_id,page, name, e))


def decode_result(im, qr_code, is_debug):
    (l, t, w, h) = qr_code.rect
    w1 = h1 = 14
    result = []
    for j in range (2):
        result_j = -1
        detected = False
        for i in range (8):
            l1 = l - 252 - int(i*47.5) + 3
            t1 = t + 127 + j*53 + 3
            sub_image = im[t1:t1+h1,l1:l1+w1]
            average_color = np.average(sub_image, axis=0).min()
            if is_debug:
                print average_color
                cv2.imwrite("test/%d.%d.png"%(7-i,j+1),sub_image)
            if (average_color < CHECKBOX_THRESHOLD and
                average_color > CHECKBOX_BAD_THRESHOLD) :
                if detected and not(is_debug):
                    raise RuntimeError("too many squares detected on line: %d"%(j+1))
                detected = True
                result_j = 7-i
                if (is_debug):
                    print 7-i
        if not(detected) and not(is_debug):
            raise RuntimeError("no squares detected on line: %d"%(j+1))
        result.append(result_j)
    return result


def main():
    parser = argparse.ArgumentParser(description='Parse images. Without --debug key read file names from stdin. Debug mode write pictures to /test directory if it exists.')
    parser.add_argument('--debug', help='run on one particular image and create debug information', metavar="IMG")
    args = parser.parse_args()
    if args.debug:
        parse_image(args.debug, True)
        return
    for l in sys.stdin:
        name = l[:-1]
        try:
            sys.stdout.write(parse_image(name))
        except RuntimeError as e:
            sys.stderr.write("%s"%e)


if __name__ == '__main__':
    main()

#:vi:et
