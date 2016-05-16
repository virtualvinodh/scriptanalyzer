import numpy as np
import cv2

imgPath = "C:\Users\Administrator\Documents\cross.png"

img = cv2.imread(imgPath)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # Greyscaling the Image
edges = cv2.Canny(gray,50,150,apertureSize = 3) # Detect Edges

minLineLength = 100
maxLineGap = 5
threshold = 20
rho = 1
theta = np.pi/180

lines = cv2.HoughLinesP(edges,rho,theta,threshold,minLineLength,maxLineGap)

for x1,y1,x2,y2 in lines[0]:
    cv2.line(img,(x1,y1),(x2,y2),(0,0,255),1)

cv2.imshow('Lines Detected',img)  ## Visualize corners detect from the above methods

if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()    



