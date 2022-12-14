
import numpy as np
import cv2
import time

import utils

# create a VideoCapture object
cap = cv2.VideoCapture('../output.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
mspf = round(1000/fps)

num_frames = 0
t = time.time()
while True:
    
    # Capture frame-by-frame
    ret, I = cap.read()
    
    if ret == False: # end of video (perhaps)
        break
    num_frames += 1

    # project the video to the field coordinate.
    proj_img = cv2.warpPerspective(I, utils.H, utils.output_size)
    
    # some closing, openning, dilating, ...
    preproc_img = utils.preprocess(proj_img)

    # apply connected components Alg and find foot position:
    n, stats = utils.CP_analysis(preproc_img)

    # save each player (patch) + label
    if (num_frames) % 10 == 0:
        for i in range(1, n):
            alpha = stats[i][1] / utils.output_size[1]
            if stats[i][4] > 500 - 300*(alpha**2): # area of CP
                ppatch = proj_img[stats[i][1]:stats[i][1]+stats[i][3] ,stats[i][0]:stats[i][0]+stats[i][2]]
                
                color = "idk"
                hsv = cv2.cvtColor(ppatch, cv2.COLOR_BGR2HSV)
                lr = np.array([0,5,10])
                ur = np.array([25,255,255])
                lb = np.array([88,5,5])
                ub = np.array([110,255,225])
                mask1 = cv2.inRange(hsv, lr, ur)
                mask2 = cv2.inRange(hsv, lb, ub)
                ms1 = np.sum(mask1 == 255)
                ms2 = np.sum(mask2 == 255)
                if abs(ms1-ms2) > 15:
                    if ms1 > ms2:
                        color = "r"
                        cv2.imwrite(f'./data/1/{num_frames}_{i}_{color}.jpg', ppatch)
                    else:
                        color = 'b'
                        cv2.imwrite(f'./data/2/{num_frames}_{i}_{color}.jpg', ppatch)

    # Display some images
    # cv2.imshow('win1', I)
    # cv2.imshow('win2', proj_img)
    # cv2.imshow('dilate(E)', preproc_img)
    # cv2.imshow('2D_field', F_circle[::2, ::2])

    key = cv2.waitKey(1) 

    if key & 0xFF == ord('q'): 
        break


print("#frames: " + str(num_frames) + " elapsed time: " + str(time.time() - t))
cap.release()
cv2.destroyAllWindows()
