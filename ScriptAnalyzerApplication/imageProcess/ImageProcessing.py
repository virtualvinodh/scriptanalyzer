import Image, ImageOps, pymorph, numpy

def RevList(L):
    L.reverse()
    return L

def ThinImage(imgPath):
    img = Image.open(imgPath).convert('L')
    
    imgArray = numpy.asarray(img)
    imgBinary =  pymorph.neg(pymorph.binary(imgArray))
    img = pymorph.thin(imgBinary)
    iPrune = pymorph.thin(img,pymorph.endpoints('homotopic'),10)

    Image.fromarray(pymorph.gray(pymorph.neg(iPrune))).save('thinned.png','PNG')
    print "Saving"

def CropImage(img):
    
    width,height = img.size
    
    try:
        leftMargin = min([list(x).index(False)
                          for x in img if False in list(x)])
    except ValueError:
        leftMargin = 0
        
    try:
        rightMargin = min([RevList(list(x)).index(False)
                           for x in img if False in list(x)])
    except ValueError:
        rightMargin =0

    try:
        topMargin = min([list(x).index(False)
                          for x in numpy.transpose(img) if False in list(x)])
    except ValueError:
        topMargin = 0

    try:
        bottomMargin = min([RevList(list(x)).index(False)
                           for x in numpy.transpose(img) if False in list(x)])
    except ValueError:
        bottomMargin =0
        
    imgGray = pymorph.gray(img)
    
    return Image.fromarray(imgGray).crop((leftMargin,topMargin,width-rightMargin,height-bottomMargin))
