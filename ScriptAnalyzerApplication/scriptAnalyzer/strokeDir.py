import numpy as np
import matplotlib.pyplot as plt

### http://youarealegend.blogspot.de/2008/09/windrose.html

##N = 20
##theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
##radii = 10 * np.random.rand(N)
##width = np.pi / 4 * np.random.rand(N)
#
#ax = plt.subplot(111, polar=True)
#
#ax.set_xticklabels(['3', '2', '1', '8', '7', '6', '5', '4'])
#
#
##bars = ax.bar(theta, radii, width=width, bottom=0.0)
#
### Use custom colors and opacity
##for r, bar in zip(radii, bars):
##    bar.set_facecolor(plt.cm.jet(r / 10.))
##    bar.set_alpha(0.5)
#
#plt.show()

from pandas import *
from pandas.tools.plotting import parallel_coordinates

def parallelStrokeDir(strokes):

    #strokes.append(['1','3','4'])
    #strokes.append(['5','4','3','2'])
    #strokes.append(['1','2','3'])
    
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