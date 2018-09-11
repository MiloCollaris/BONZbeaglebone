import os
import sys
import numpy as np
import pypylon
import matplotlib.pyplot as plt
import time  #in case for use of sleep command
from datetime import datetime
import scipy.misc
import ellipses as el
from matplotlib.patches import Ellipse
from skimage.feature import peak_local_max

measnr = 9
period = 0.6  #Arduino period in seconds
os.makedirs("C:\\Users\\user\\milobonz\\data\\test"+str(measnr), exist_ok=True)
os.makedirs("C:\\Users\\user\\milobonz\\data\\test"+str(measnr)+ "\\image", exist_ok=True)
os.makedirs("C:\\Users\\user\\milobonz\\data\\test"+str(measnr)+ "\\analysis", exist_ok=True)

#Camera initialization
camera = pypylon.factory.find_devices()
cam = pypylon.factory.create_device(camera[0])
cam.open()

#Camera properties
cam.properties['Gain']=0
cam.properties['GainAuto']='Off'
cam.properties['ExposureAuto']='Off'
cam.properties['PixelFormat']='Mono12'
cam.properties['ExposureTime']=10
cam.properties['Width']=350
cam.properties['Height']=350

#Setting the external trigger
cam.properties['AcquisitionMode'] = 'Continuous'        #Important for external triggering
cam.properties['TriggerMode'] = 'On'
cam.properties['BslImmediateTriggerMode'] = 'Off'
cam.properties['TriggerSource'] = 'Line1'
cam.properties['TriggerActivation'] = 'FallingEdge'

#Saving parameters in filename
filename = "data/test"+str(measnr)+"/CamProp.txt"
cam_parameters = open(filename, 'w')
for key in cam.properties.keys():
    try:
        value = cam.properties[key]
    except IOError:
        value = '<NOT READABLE>'
    cam_parameters.write('{0} ({1}):\t{2}\n'.format(key, cam.properties.get_description(key), value))
cam_parameters.close()

#Numbers of pictures taken
datalength = 1800

img2=np.empty([datalength,cam.properties['Height'],cam.properties['Width']])
datatime = np.empty(datalength)

#Taking the images and correstonding time
starttime = datetime.now()
for num, image in enumerate(cam.grab_images(nr_images = datalength, grab_strategy=0, timeout=500000)):
    endtime = datetime.now()- starttime
    datatime[num] = "%s" %(endtime.seconds - num*period + endtime.microseconds / 1000000) #0.5 for the wait between triggering
    img2[num] = image
np.savetxt("data/"+"test"+ str(measnr) +"/datatime.txt", datatime, fmt='%1.6f')


#Save picture
for i in range(datalength):
    plt.imshow(img2[i], cmap = 'gray')
    plt.ylabel('Pixels')
    plt.xlabel('Pixels')
    name =  "data/"+"test"+ str(measnr) +"//image//graph-number-" + str(i) + ".png"
    plt.savefig(name, facecolor = None)

    plt.close()

cam.close()

#Data analysis
threshold = 1
radii = np.empty(datalength)


#The Fit Ellipse code
for i in range(datalength):
    data = img2[i]
    for n in range(350):
        for m in range(350):
            data [n][m] = 4095 - data[n][m]  # 4095 is max pixel value and is faster than np.amax(data)

    #Taking the edge of the droplet
    av = 1
    off = 2
    dataedge = np.zeros([350,350])
    for y in range(350):
        for x in range(350):
            if data[y][x] > av:
                if data[y+off][x] > av:
                    if data[y-off][x] < av:
                        dataedge[y][x] = 4095
    for y in range(350):
        for x in range(350):
            if data[y][x] > av:
                if data[y-off][x] > av:
                    if data[y+off][x] < av:
                        dataedge[y][x] = 4095
    for y in range(350):
        for x in range(350):
            if data[y][x] > av:
                if data[y][x+off] > av:
                    if data[y][x-off] < av:
                        dataedge[y][x] = 4095
    for y in range(350):
        for x in range(350):
            if data[y][x] > av:
                if data[y][x-off] > av:
                    if data[y][x+off] < av:
                        dataedge[y][x] = 4095

    data = dataedge

    ## Obtain x- and y-coords for each pixel above 'threshold'
    xy = peak_local_max(data, threshold_abs = threshold).T

    ## Fit an ellipse to the x- and y-coords of the pixels above 'threshold'
    lsqe = el.LSqEllipse()
    lsqe.fit(xy)
    center, width, height, phi = lsqe.parameters()


    ## Plot results
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    ax1.imshow(data, cmap = "gray")

    ax1.set_xlim(0, data.shape[0])
    ax1.set_ylim(data.shape[0], 0)
    ax1.set_title("Original image")


    ax2.imshow(data, cmap = "gray")
    ax2.plot(xy[1, :], xy[0, :], "yo", markersize = 2)

    ax2.set_xlim(0, data.shape[0])
    ax2.set_ylim(data.shape[0], 0)
    ax2.set_title("Convert ")

    ax3.plot(xy[1, :], xy[0, :], "yo", markersize = 2)

    ax3.set_aspect("equal")
    ax3.set_xlim(0, data.shape[0])
    ax3.set_ylim(data.shape[0], 0)


    ax4.plot(xy[1, :], xy[0, :], "yo", markersize = 1, alpha = 0.05)

    ellipse = Ellipse(xy = center, width = 2. * width, height = 2. * height,
                      angle = np.rad2deg(phi), edgecolor = "k", fc = "None",
                      lw = 4, zorder = 2)

    ax4.add_patch(ellipse)

    ax4.set_aspect("equal")
    ax4.set_xlim(0, data.shape[0])
    ax4.set_ylim(data.shape[0], 0)

    name2 =  "data/"+"test"+ str(measnr) +"//analysis//graph-number-" + str(i) + "-analysis.png"
    plt.savefig(name2, facecolor = None)

    plt.close()

    #Save the Images so that we have one map w/ raw data, fitted data and r,t coordinates
    #print("Center:", center)
    #print("Width:", width)
    #print("Height:", height)
    #print("Phi:", phi)

    radii[i] = width

fig = plt.figure()
plt.plot(datatime, radii, '.')
plt.ylabel('Amplitude (#Pixels)')
plt.xlabel('Time (s)')
name3 = "data/"+"test"+ str(measnr) +"/damping.png"
plt.savefig(name3)

#Save radii
np.savetxt("data/"+"test"+ str(measnr) +"/radii.txt", radii, fmt='%1.6f')






