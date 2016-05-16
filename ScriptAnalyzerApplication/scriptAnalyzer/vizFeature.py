import numpy as np
import math
import matplotlib.pyplot as plt

from pandas import *
from pandas.tools.plotting import parallel_coordinates

def plotAngle(angle): ## angle in radians
    N = len(angle)
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    
    theta = angle
    radii = [0.2] * N # 10 * np.random.rand(N)
    width = [0.01] * N
    #width = np.pi / 4 * np.random.rand(N)
    
    ax = plt.subplot(111, polar=True)
    ax.set_xticklabels(['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'])
    #ax.set_theta_direction(-1)
    #ax.set_theta_offset(math.pi/2)
    bars = ax.bar(theta, radii, width=width, bottom=0.0)
    
    c = ['b','g','r','c','m','y','k','w']*20
    
    i = 0
    
    # Use custom colors and opacity
    for r, bar in zip(radii, bars):
        bar.set_facecolor(c[i])
        i += 1
        bar.set_alpha(0.5)
    
    plt.show()
    
def parallelStrokeDir(strokes):

    strokes = sorted(strokes,key=len,reverse=True)
    
    maxStrokeLength = max([len(stroke) for stroke in strokes])
    
    strokesSep = {i+1:[] for i in range(maxStrokeLength)}
    
    si = [-0.05 for s in range(9)]
    
    for stroke in strokes:
        for i,s in enumerate(stroke):
            strokesSep[i+1].append(s+si[s])
            si[s] += 0.01
            
                    
    strokesSep = {label:Series(np.asarray(data,dtype=np.float64)) for label,data in strokesSep.iteritems()}     
    
    strokesSep['Name'] = np.asarray(range(1,len(strokes)+1),dtype=np.float64)
    
    df2 = DataFrame(strokesSep)
    
    parallel_coordinates(df2,'Name')
    plt.show()    
    
