# pure-Python Douglas-Peucker line simplification/generalization
#
# this code was written by Schuyler Erle <schuyler@nocat.net> and is
#   made available in the public domain.
#
# the code was ported from a freely-licensed example at
#   http://www.3dsoftware.com/Cartography/Programming/PolyLineReduction/
#
# the original page is no longer available, but is mirrored at
#   http://www.mappinghacks.com/code/PolyLineReduction/

"""

>>> line = [(0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2),(0,1),(0,0)]
>>> simplify_points(line, 1.0)
[(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]

>>> line = [(0,0),(0.5,0.5),(1,0),(1.25,-0.25),(1.5,.5)]
>>> simplify_points(line, 0.25)
[(0, 0), (0.5, 0.5), (1.25, -0.25), (1.5, 0.5)]

"""

import math
   
def simplify_points (pts, tolerance): 
    anchor  = 0
    floater = len(pts) - 1
    stack   = []
    keep    = set()

    stack.append((anchor, floater))  
    while stack:
        anchor, floater = stack.pop()
      
        # initialize line segment
        if pts[floater] != pts[anchor]:
            anchorX = float(pts[floater][0] - pts[anchor][0])
            anchorY = float(pts[floater][1] - pts[anchor][1])
            seg_len = math.sqrt(anchorX ** 2 + anchorY ** 2)
            # get the unit vector
            anchorX /= seg_len
            anchorY /= seg_len
        else:
            anchorX = anchorY = seg_len = 0.0
    
        # inner loop:
        max_dist = 0.0
        farthest = anchor + 1
        for i in range(anchor + 1, floater):
            dist_to_seg = 0.0
            # compare to anchor
            vecX = float(pts[i][0] - pts[anchor][0])
            vecY = float(pts[i][1] - pts[anchor][1])
            seg_len = math.sqrt( vecX ** 2 + vecY ** 2 )
            # dot product:
            proj = vecX * anchorX + vecY * anchorY
            if proj < 0.0:
                dist_to_seg = seg_len
            else: 
                # compare to floater
                vecX = float(pts[i][0] - pts[floater][0])
                vecY = float(pts[i][1] - pts[floater][1])
                seg_len = math.sqrt( vecX ** 2 + vecY ** 2 )
                # dot product:
                proj = vecX * (-anchorX) + vecY * (-anchorY)
                if proj < 0.0:
                    dist_to_seg = seg_len
                else:  # calculate perpendicular distance to line (pythagorean theorem):
                    dist_to_seg = math.sqrt(abs(seg_len ** 2 - proj ** 2))
                if max_dist < dist_to_seg:
                    max_dist = dist_to_seg
                    farthest = i

        if max_dist <= tolerance: # use line segment
            keep.add(anchor)
            keep.add(floater)
        else:
            stack.append((anchor, farthest))
            stack.append((farthest, floater))

    keep = list(keep)
    keep.sort()
    return [pts[i] for i in keep]

from scipy.interpolate import splev,splprep

def makeSpline(pointList,smPnts):   
    x = [p[0] for p in pointList]
    y = [p[1] for p in pointList] 
        
    xRed = [p[0] for p in smPnts]
    yRed = [p[1] for p in smPnts]

#    print xRed
#    print yRed                                     
    tck,uout = splprep([xRed,yRed],s=0.,k=2,per=False)
    tckOri, uout = splprep([x,y],s=0.,k=2,per=False)
                                
    N=300
                
    uout = list((float(i) / N for i in xrange(N + 1)))
                            
    xOri, yOri = splev(uout,tckOri)                        
    xSp,ySp = splev(uout,tck)         
                
    import dtw
    diff = dtw.dynamicTimeWarp(zip(xOri,yOri), zip(xSp,ySp))
                
    err =  diff/len(xSp)
        
    return tck,err

def reduceP(pointList,errT=11):    
    x = [p[0] for p in pointList]
    y = [p[1] for p in pointList]
        
    pointList = zip(x,y)     
    smPnts  = zip(x,y)   
    err = 0
    sTxt = 0
    
    count = 0
    i=1
    
    #print pointList
    
    oldLength = len(pointList)
    
    while err < errT and len(smPnts) > 3:
        smPnts = simplify_points(pointList, sTxt)
        
        if len(smPnts) < 3:
            return smPnts,None
        
        tck,err = makeSpline(pointList, smPnts)
        
        if count == 5:
            count = 0
            i += 2
            #print "Incrementing"
             
        sTxt += i
        
        if len(smPnts) == oldLength:
            count += 1
            
        oldLength = len(smPnts)
            
        #print err, sTxt, len(smPnts)
            
    if err > errT+2:
        #print "Error beyond recognition: reverting to previous"
        #print err, sTxt, len(smPnts)            
        sTxt -= i+i
        smPnts = simplify_points(pointList, sTxt)
        tck,err = makeSpline(pointList, smPnts)
        #print err, sTxt, len(smPnts)
     
    return smPnts,tck