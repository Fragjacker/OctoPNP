'''
Created on 10.08.2017

@author: Dennis Struhs
'''

import GCode_processor as GCpros
import CameraCoordinateGetter as CamCoordGet

#===============================================================================
# Execute GCode extraction
#===============================================================================

# Remove when isnerting into OctoPNP
fileName = 'flat_solid_cube.gcode' #Load the corresponding file in

newCamExtractor = GCpros.CameraGCodeExtraction(0.25,'T0')          
Data = newCamExtractor.openFiles(fileName)
newCamExtractor.extractCameraGCode(Data)

#===============================================================================
# Main Execution Lines
#===============================================================================

Image = CamCoordGet.ImageOperations()
Image.createBackgroundImage()

#Creates a new CameraGridMaker Object with int Numbers for the Cam resolution
newGridMaker = CamCoordGet.CameraGridMaker(newCamExtractor.getCoordList(),0,50,50)

#Execute all necessary operations to create the actual CameraGrid
newGridMaker.getCoordinates()
newGridMaker.drawGCodeLines(Image)
newGridMaker.createCameraLookUpGrid()
newGridMaker.drawAllFoundCameraPositions(Image)
newGridMaker.drawCameraLines(Image)

#Image.drawGridBox(0, 0, 50, 50)
#Draw Maximums and Minimums
Image.drawExtremaBounds()
#Draw Center of of the Extremes
#Image.drawCenterCircle(int(centerX), int(centerY))
#Image.drawBoxFromCenter(int(centerX), int(centerY))
# Resize the Image
Image.resizeImage(1024, 1024)
Image.saveImage('Camera Grid')
Image.showImage()
