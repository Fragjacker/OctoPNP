'''
Created on 18.07.2017

@author: Dennis Struhs
'''

import cv2
import numpy as np
from GCode_processor import Coordinate

#===============================================================================
# Global variables
#===============================================================================
#Stores the coordinates as tuples of x and y. Implementation in class Coordinate
workList = []

#Conversion from millimeters to pixel
MillimeterToPixel = 3.779527559

#Stores the List of found centers for the Camera Run
CameraCoords = []

#Stores the maximum Pixel size the camera provies. Its in Pixel x Pixel Format
CamPixelX = 0
CamPixelY = 0

#Below values store the extreme values found during the processing process
minX = None
minY = None
maxX = None
maxY = None
centerX = None
centerY = None

#===============================================================================
# Help Classes
#===============================================================================

class ImageOperations:

    def createBackgroundImage(self):
        self.img = np.zeros((512,512,3),np.uint8)

    def drawBlueLines(self, xStart , yStart, xEnd, yEnd):
        cv2.line(self.img,(xStart,yStart),(xEnd, yEnd),(255,0,0),1)

    def drawCameraLines(self, xStart , yStart, xEnd, yEnd):
        cv2.line(self.img,(xStart,yStart),(xEnd, yEnd),(0,160,255),1)

    def drawGridBox(self, xStart , yStart, xEnd, yEnd):
        cv2.rectangle(self.img,(xStart, yStart),(xEnd, yEnd),(0,255,0),0)

    def drawCenterCircle(self,x,y):
        cv2.circle(self.img,(x,y),1,(0,0,255),-1)

    def drawExtremaBounds(self):
        self.drawCenterCircle(int(minX), int(minY))
        self.drawCenterCircle(int(minX), int(maxY))
        self.drawCenterCircle(int(maxX), int(minY))
        self.drawCenterCircle(int(maxX), int(maxY))

    def drawBoxFromCenter(self, xStart , yStart):
        cv2.circle(self.img,(xStart,yStart),1,(0,255,255),-1)
        cv2.rectangle(self.img,(xStart - int(CamPixelX / 2), yStart - int(CamPixelY / 2)),(xStart + int(CamPixelX / 2), yStart + int(CamPixelY / 2)),(0,255,0),0)

    def resizeImage(self,fx,fy):
        self.img = cv2.resize(self.img,(fx, fy),interpolation = cv2.INTER_AREA)

    def showImage(self,windowName):
        cv2.imshow(windowName,self.img)
        if cv2.waitKey(0) & 0xff == 27:
            cv2.destroyAllWindows()

    def saveImage(self,name):
        cv2.imwrite(name + '.jpg',self.img)

#===============================================================================
# Help Functions
#===============================================================================
class CameraGridMaker:

    #Stores the incoming List of coordinates
    CordList = []

    def __init__(self,incomingCoordList,layer,CamResX,CamResY):
        global CamPixelX
        global CamPixelY
        CamPixelX = CamResX
        CamPixelY = CamResY
        self.CordList = incomingCoordList[layer]

    #Creates the work list we're using for our computations
    #and sets up the Bounding Box values
    def getCoordinates(self):
        global workList
        for eachEntry in self.CordList:
            Coord = Coordinate(
                int(eachEntry.x*MillimeterToPixel),
                int(eachEntry.y*MillimeterToPixel))
            self.findXYExtremas(Coord.x, Coord.y)
            self.computeCenterOfExtremes()
            workList.append(Coord)

    #Draws the printed Object
    def drawGCodeLines(self,img):
        i = 0
        while i < len(workList) - 1:
            xStart = workList[i].x
            yStart = workList[i].y
            xEnd = workList[i + 1].x
            yEnd = workList[i + 1].y
            img.drawBlueLines(xStart, yStart, xEnd, yEnd)
            i += 1

    #Draws the path the Camera will take
    def drawCameraLines(self,img):
        i = 0
        while i < len(CameraCoords) - 1:
            xStart = int(CameraCoords[i].x)
            yStart = int(CameraCoords[i].y)
            xEnd = int(CameraCoords[i + 1].x)
            yEnd = int(CameraCoords[i + 1].y)
            img.drawCameraLines(xStart, yStart, xEnd, yEnd)
            i += 1

    #Draws the found Camerasectorboxes on the Screen
    def drawAllFoundCameraPositions(self,img):
        for eachItem in CameraCoords:
            print(eachItem.x,eachItem.y)
            img.drawBoxFromCenter(int(eachItem.x), int(eachItem.y))

    #Find the Extrema for the Bounding Box
    def findXYExtremas(self,NewX,NewY):
        global minX
        global minY
        global maxX
        global maxY
        #Initialize with some base values other than zero
        if (minX == None):
            minX = NewX
            maxX = NewX
            minY = NewY
            maxY = NewY
        else:
            if(NewX < minX):
                minX = NewX
            elif(NewX > maxX):
                maxX = NewX

            if(NewY < minY):
                minY = NewY
            elif(NewY > maxY):
                maxY = NewY

    def findYMinMaxInList(self,inputList,mode):
        result = None
        if(mode == 'min'):
            previous = None
            for each in inputList:
                #Initilize
                if(previous == None):
                    previous = each.y
                if(each < previous):
                    previous = each.y
            result = previous

        if(mode == 'max'):
            previous = None
            for each in inputList:
                #Initilize
                if(previous == None):
                    previous = each.y
                if(each > previous):
                    previous = each.y
            result = previous

        return result

    #Compute the Center of the printed Object
    def computeCenterOfExtremes(self):
        global centerX
        global centerY
        centerX = (maxX+minX) / 2
        centerY = (maxY+minY) / 2

    #Makes a points symmetrical copy of the upper Camerasectorgrid
    def makePointSymmetry(self,inputList):
        symmetryList = []
        for eachItem in inputList:
            distX = centerX - eachItem.x
            distY = centerY - eachItem.y

            if(distY != 0):
                symmetryX = centerX + distX
                symmetryY = centerY + distY
                newCoord = Coordinate(symmetryX,symmetryY)
                symmetryList.insert(0, newCoord)

        return symmetryList

    #===============================================================================
    # Main Camera Grid computation Algortihm
    #===============================================================================
    def createCameraLookUpGrid(self):
        global CameraCoords

        currentXPos = centerX
        seeRight = currentXPos
        walkRight = currentXPos
        #Walk all the way right first until maxX bound is reached
        while(True):
            seeRight = (currentXPos + CamPixelX)
            walkRight = (currentXPos + CamPixelX / 2)
            if(walkRight < maxX):
                if(seeRight < maxX):
                    currentXPos += CamPixelX
                elif(seeRight > maxX):
                    currentXPos += CamPixelX
                    break
            else:
                break

        #Once the most right is reached
        #fill the Camcoords list from right to left
        seeLeft = currentXPos
        walkLeft = currentXPos
        while(True):
            seeLeft = (currentXPos - CamPixelX)
            walkLeft = (currentXPos - CamPixelX / 2)
            if(walkLeft > minX):
                if(seeLeft > minX):
                    newCoord = Coordinate(currentXPos, centerY)
                    CameraCoords.append(newCoord)
                    currentXPos -= CamPixelX
                elif(seeLeft < minX):
                    newCoord = Coordinate(currentXPos, centerY)
                    CameraCoords.append(newCoord)
                    currentXPos -= CamPixelX
                    newCoord = Coordinate(currentXPos, centerY)
                    CameraCoords.append(newCoord)
                    break
            else:
                newCoord = Coordinate(currentXPos, centerY)
                CameraCoords.append(newCoord)
                break


        #Now create the x-Axis lines
        cacheList = []
        currentYPos = centerY
        while(True):
            switcher = 0
            #Rows that have the switcher module result
            #of 0 fill from left to right
            if(switcher % 2 == 0):
                reverserList = []
                seeUp = (currentYPos - CamPixelY)
                walkUp = (currentYPos - CamPixelY / 2)
                if(walkUp > minY):
                    if(seeUp > minY):
                        for eachItem in CameraCoords:
                            newCoord = Coordinate(eachItem.x, seeUp)
                            reverserList.append(newCoord)

                        reverserList.reverse()
                        reverserList.extend(cacheList)
                        cacheList = reverserList
                        currentYPos = seeUp
                        switcher += 1
                    elif(seeUp < minY):
                        for eachItem in CameraCoords:
                            newCoord = Coordinate(eachItem.x, seeUp)
                            reverserList.append(newCoord)

                        reverserList.reverse()
                        reverserList.extend(cacheList)
                        cacheList = reverserList
                        currentYPos = seeUp
                        switcher += 1
                        break
                else:
                    break
            #Rows that have the switcher module result
            # of 1 fill from right to left
            if(switcher % 2 == 1):
                localList = []
                seeUp = (currentYPos - CamPixelY)
                walkUp = (currentYPos - CamPixelY / 2)
                if(walkUp > minY):
                    if(seeUp > minY):
                        for eachItem in CameraCoords:
                            newCoord = Coordinate(eachItem.x, seeUp)
                            localList.append(newCoord)

                        localList.extend(cacheList)
                        cacheList = localList
                        currentYPos = seeUp
                        switcher += 1
                    elif(seeUp < minY):
                        for eachItem in CameraCoords:
                            newCoord = Coordinate(eachItem.x, seeUp)
                            localList.append(newCoord)

                        localList.extend(cacheList)
                        cacheList = localList
                        currentYPos = seeUp
                        switcher += 1
                        break
                else:
                    break

        #Insert the new list items into the Cameracoordinate List
        cacheList.extend(CameraCoords)
        CameraCoords = cacheList

        #Create the lower half of the Grid
        #by making a point symmetrical Copy
        CameraCoords.extend(self.makePointSymmetry(cacheList))
