'''
Created on 02.01.2018

@author: Dennis Struhs
'''
import cv2
import numpy as np


class ImageAnalyzer:
    
    """
    Initilizes the necessary variables.
    @param Image: Must be a greyscale Image
    @param infoDict: A dictionary that contains necessary constants from OctoCamDox 
    """
    def __init__(self, Image, infoDict):
        self.inputImage = Image
        # Get the dimension of the Image
        self.Imageheight,self.Imagewidth = self.inputImage.shape
        
        # Specifiy the radius of the Region of Interest
        self.ROI_radius = infoDict["radius"]
        self.originX = None
        self.originY = None
        
        self.pixelRatioX, self.pixelRatioY = self.computePixelToGCodeCoordRatio(infoDict)
        
    
    """
    Creates the region of interest that will be used
    as our detector to count pixels.
    @param posX: The X-Coordinate of the center for the ROI.
    @param posY: The Y-Coordinate of the center for the ROI.
    """
    def countPixelsAtPosition(self, posX, posY):
        circle_img = np.zeros((self.ROI_radius*2,self.ROI_radius*2), dtype=self.inputImage.dtype)
        cv2.circle(circle_img,(self.ROI_radius,self.ROI_radius),self.ROI_radius,255,thickness=-1)
        croppedRegion = self.inputImage[posY-self.ROI_radius:posY+self.ROI_radius, posX-self.ROI_radius:posX+self.ROI_radius]
        masked_data = cv2.bitwise_and(croppedRegion, croppedRegion, mask=circle_img)
        
        # Since the mask is a white Circle we can just count them for the total amount of pixels
        maxPixels = cv2.countNonZero(circle_img)
        whitePixel = cv2.countNonZero(masked_data)
        blackPixel = maxPixels - whitePixel
        
        return maxPixels, whitePixel, blackPixel
    
    """
    Returns the ratio of found white Pixels compared to the total amount of pixel
    @param totalPixel: The total amount of all pixels in the ROI
    @param whitePixel: The amount of found white pixels in the ROI
    """
    def circuitQualityChecker(self, totalPixel, whitePixel):
        qualityLevel = (float(whitePixel) / float(totalPixel)) * 100
        
        return qualityLevel
    
    """
    Computes the ratio between GCode and Pixels and returns
    a scalar that can be used to convert Pixel to GCode coordinates
    @param inputDict: A dictionary that Contains the necessary data for the computation
    """
    def computePixelToGCodeCoordRatio(self, inputDict):
        camCenterX = inputDict["tileCenterX"]
        camCenterY = inputDict["tileCenterY"]
        tileWidthX = inputDict["tileWidthX"]
        tileWidthY = inputDict["tileWidthY"]
        pixelWidthX = inputDict["campixelWidthX"]
        pixelWidthY = inputDict["campixelWidthY"]
        
        self.originX = camCenterX - (tileWidthX / 2)
        self.originY = camCenterY - (tileWidthY / 2) 
        
        resultX = tileWidthX / pixelWidthX
        resultY = tileWidthY / pixelWidthY
        
        return resultX,resultY
    
    """
    This function converts between Pixel and GCode coordinates.
    @param posX: The input position for the desired X-Axis
    @param posX: The input position for the desired Y-Axis
    @param mode: Specify the target coordinate System. Valid options are "ToGCode" and "ToPixel"
    """
    def convertPixelToGCodeCoordinates(self, posX, posY, mode):
        if mode is "ToGCode":
            resultX = self.originX + self.pixelRatioX * posX
            resultY = self.originY + self.pixelRatioY * posY
        elif mode is "ToPixel":
            resultX = (posX - self.originX) / self.pixelRatioX
            resultY = (posY - self.originY) / self.pixelRatioY
        
        return resultX,resultY
    
    def analyzeCircuits(self):
        img = np.zeros( ( self.Imageheight, self.Imagewidth, 3 ), dtype=self.inputImage.dtype )
        
        x = self.ROI_radius
        y = self.ROI_radius
        while y <= (self.Imageheight - self.ROI_radius):
            while x <= (self.Imagewidth - self.ROI_radius):
                currMaxPix, currWhitePix, __ = self.countPixelsAtPosition(x, y)
                currQuality = self.circuitQualityChecker(currMaxPix, currWhitePix)
                
                if(currQuality >= 50.0):
                    cv2.rectangle( img, (x-self.ROI_radius/2,y-self.ROI_radius/2), (x+self.ROI_radius/2,y+self.ROI_radius/2), ( 0, 255, 0 ), thickness=-1 )
                elif(currQuality < 50.0):
                    cv2.rectangle( img, (x-self.ROI_radius/2,y-self.ROI_radius/2), (x+self.ROI_radius/2,y+self.ROI_radius/2), ( 0, 0, 255 ), thickness=-1 )
                
                x += self.ROI_radius
            x = self.ROI_radius
            y += self.ROI_radius
            
        print("DONE!")
        cv2.imwrite( "AnalyzedImage" + '.png', img )
        

values = dict(radius = 10, tileCenterX = 50.0, tileCenterY = 50.0, tileWidthX = 10.0, tileWidthY = 10.0, campixelWidthX = 880,campixelWidthY = 880)
Image = ImageAnalyzer(cv2.imread('binary_Layer7.png',0), values)
# position = [values["radius"],values["radius"]]
# print(Image.countPixelsAtPosition(position[0],position[1]))
# maxPix, whitePix, __ = Image.countPixelsAtPosition(position[0],position[1])
# print("The circuit quality is %f" % Image.circuitQualityChecker(maxPix, whitePix) + "%")
# print(Image.convertPixelToGCodeCoordinates(4, 67, "ToPixel"))
# print(Image.convertPixelToGCodeCoordinates(1936, 1936, "ToGCode"))
Image.analyzeCircuits()
