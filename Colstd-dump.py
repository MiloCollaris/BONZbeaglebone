"""
@author: MiloCollaris
Utrecht University Bachelor research
"""
#This document calculates the damping constand of the damped oscillation of a droplet inside an 
#acoustic levitator. The data it uses is the length of the horizontal or vertical radius. The 
#first fitting method is a fit to the standard deviation of the radius and the second fit is an
#fit to the data directly.

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

def fit1(t, A, tau, C):
	return A*np.exp(-t/tau)+C

def fit2(p, t):
	return p[0]+p[1]*np.cos(p[2]*t+p[3]/360*np.pi)*np.exp(-t/p[4])+p[5]*t

def errorfunc(p, t, r):
	return fit2(p,t)-r

# cutout(period number, radius, translation of data, extra data so the set contains 597 images)
def cutout(number, r, roll, off):
    r = np.roll(r,roll)    
    r = r[int(border[0 + number]):int(border[1 + number] + off)]
    return r

def fitting(number, p0, r):
    #First fitting method with std.
    b=100
    dump=np.zeros(r.size-b)
    
    for i in range(dump.size):
    	dump[i]=np.std(r[i:i+b])
    
    p1=[0.60,100,0.01]
    params, pvar = scipy.optimize.curve_fit(fit1, np.arange(dump.size), dump, p1, maxfev=100000)
    	    
    print('Fitting1')
    print(params[1]*0.001)
    print(0.001*np.sqrt(np.diag(pvar))[1])
    
    #Second fitting method to data directly
    pfit, pcov, infodict, errmsg, success = scipy.optimize.leastsq(errorfunc, p0, args=(t, r), Dfun=None, full_output=True, ftol=1e-9, xtol=1e-9, maxfev=10000000, epsfcn=1e-10, factor=0.1)
    
    print('Fitting2')
    print(0.001*pfit[4])
    print(pcov)
    print(0.001*np.sqrt(np.diag(pcov))[4]) 
    
    #plotting
    f = plt.figure(figsize = (19,4))

    ax1 = f.add_subplot(131)
    ax1.plot(r, '.', markersize=3)
    ax1.set_title("Damped oscillation of colloidal droplet",fontsize=19)
    ax1.set_xlabel("time (ms)",fontsize=19)
    ax1.set_ylabel("vertical radius (mm)",fontsize=19)
    
    ax2 = f.add_subplot(132)
    ax2.scatter(np.arange(dump.size),dump, s=1, label = 'Data')
    ax2.plot(fit1(np.arange(dump.size), params[0], params[1], params[2]),color = 'red', label = 'Fitted function')
    ax2.legend(loc='best') 
    ax2.set_title("Std fit to the radius",fontsize=19)
    ax2.set_xlabel("time (ms)",fontsize=19)
    ax2.set_ylabel("$\sigma / r_0$",fontsize=19)
    
    ax3 = f.add_subplot(133)
    ax3.plot(r, '.', markersize=3, label = 'Data')
    ax3.plot(fit2(pfit, t), color = 'red',label = 'Fitted function')
    ax3.legend(loc='best') 
    ax3.set_title('Direct fit to the radius',fontsize=19)
    ax3.set_ylabel('vertical radius (mm)',fontsize=19)
    ax3.set_xlabel('time (ms)',fontsize=19)
    plt.show()
    
    """
    name =  "/Users/MiloCollaris/Documents/UU/BONZ/Data/Colloid/Plots/Colvrfitting" + str(number) + ".png"
    f.savefig(name)
    """
    
    
#Code starts here    
h = np.loadtxt("/Users/MiloCollaris/Documents/UU/BONZ/Data/Colloid/hradii.txt")
v = np.loadtxt("/Users/MiloCollaris/Documents/UU/BONZ/Data/Colloid/vradii.txt")

hr = h[:4200]
vr = v[:4200]
t = np.linspace(0,596, num = 597)

"""
plt.plot(vr,'.', markersize=3)
plt.title("Colloidal droplet oscillation",fontsize=19)
plt.xlabel("time (ms)",fontsize=19)
plt.ylabel("vertical radius (mm)",fontsize=19)
plt.show()
"""
    
#Cutting the data in equal regions for each period
Tdamp = 7
period = np.zeros([Tdamp,int(len(hr)/Tdamp)])
border = np.zeros([Tdamp])

for i in range(Tdamp):
    period[i] = hr[(i*int(len(hr)/Tdamp)):(i+1)*int(len(hr)/Tdamp)]
    border[i] = i*int(len(hr)/Tdamp) + np.argmax(period[i])
  
    
   
#Cutting the data and alling the fittings
r0 = cutout(0, vr, 8, -2)
fitting(0, [1, 0.2, 0.01, 50, 60, -0.0008], r0)

r1 = cutout(1, vr, 8, -31)
#fitting(1, [1, 0.2, 0.01, 50, 50, -0.0008], r1)

r2 = cutout(2, vr, 37, 0)
#fitting(2, [1, 0.2, 0.01, 50, 60, -0.0008], r2)

r3 = cutout(3, vr, 37, 1)
#fitting(3, [0.9, 0.1, 0.01, 40, 50, -0.0008], r3)

r4 = cutout(4, vr, 33, 25)
#fitting(4, [1, 0.2, 0.01, 50, 60, -0.0008], r4)

r5 = cutout(5, vr, 6, 218)
#fitting(5, [0.8, 0.15, 0.01, 40, 1, -0.0008], r5)






