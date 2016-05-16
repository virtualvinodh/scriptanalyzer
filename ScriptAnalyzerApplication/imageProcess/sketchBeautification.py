import numpy as np
from utilities import util
def checkShape(points):
    x,y = util.coOrd(points,0),util.coOrd(points,1)
    
    if util.checkLine(x, y, 15000):
        return "line"
    
    return points

