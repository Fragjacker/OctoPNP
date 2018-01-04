'''
Created on 05.12.2017

This is the testing ground to achieve a proper image binarization to apply computer vision on it lateron.

@author: Dennis Struhs
'''

import cv2
import numpy as np

class imageBinarizer:
    
    def __init__(self,image):
        self.img = image
        self.bin_img = None #The actual final Image
        self.kernel_size = 3
        self.iterations = 3
        self.contrastThresh = 140
        self.contrastAmount = 90.0
        self.delta = 5
    
    '''
    The main function that handles all the necessary 
    operations to process the image into a usable state
    '''
    def processImage(self):
        self.bin_img = self.adjustContrast(self.img)
        self.bin_img = self.binarize_Image(self.bin_img)
        self.bin_img = self.invertImage(self.bin_img)
#         self.bin_img = self.dilateImage(self.iterations, self.bin_img)
#         self.bin_img = self.erodeImage(self.iterations+self.delta, self.bin_img)

    '''
    This function raises the brightness of the picture
    :param image: Input Image
    '''
    def adjustContrast(self,image):
        bigmask = cv2.compare(image,np.uint8([self.contrastThresh]),cv2.CMP_GE)
        smallmask = cv2.bitwise_not(bigmask)
        
        x = np.array([self.contrastAmount])
        big = cv2.add(image,x,mask = bigmask)
        small = cv2.subtract(image,x,mask = smallmask)
        res = cv2.add(big,small)
        return res
        
    '''
    This function handles the binarization of the Image
    in order to highlight the circuit parts
    :param image: Input Image
    '''
    def binarize_Image(self,image):
        # Otsu's thresholding after Gaussian filtering
        dst = np.zeros(shape=(5,5))
        norm = cv2.normalize(image,dst, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        blur = cv2.GaussianBlur(norm,(5,5),0)
        __,res = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        return res
        
    '''
    Helper function to erode the image.
    :param iterations: The amount of iterations/times the erosion is applied to the image 
    :param image: Input Image
    '''
    def erodeImage(self, iterations, image):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(self.kernel_size,self.kernel_size))
        return cv2.erode(image,kernel,iterations = iterations)
            
    '''
    Helper function to dilate the image.
    :param iterations: The amount of iterations/times the dilation is applied to the image
    :param image: Input Image
    '''    
    def dilateImage(self, iterations, image):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(self.kernel_size,self.kernel_size))
        return cv2.dilate(image,kernel,iterations = iterations)
    
    '''
    Helper function to invert black<->white colors.
    '''
    def invertImage(self,image):
        return cv2.bitwise_not(image)
    
    #TODO: Remove the save function when embedding it into OctoPNP
    '''
    Helper function to save the image
    :param name: Specifies the name of the file as a String.
    :param suffix: Specifies the file extension of the newly saved file.
    '''
    def saveImage( self, name, suffix ):
        cv2.imwrite( name + suffix, self.bin_img )
    
    '''
    This function returns the final result image.
    '''
    def getResultImage(self):
        return self.bin_img;
        

Image = imageBinarizer(cv2.imread('Komplette_Drucke/result_battery_cube_2017-11-28/Layer_7.png',0))
Image.processImage()
Image.saveImage('binary_Layer7', '.png')