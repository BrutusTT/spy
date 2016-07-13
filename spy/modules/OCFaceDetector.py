####################################################################################################
#    Copyright (C) 2016 by Ingo Keller                                                             #
#    <brutusthetschiepel@gmail.com>                                                                #
#                                                                                                  #
#    This file is part of SPY (A Sensor Module Package for Yarp).                                  #
#                                                                                                  #
#    SPY is free software: you can redistribute it and/or modify it under the terms of the         #
#    GNU Affero General Public License as published by the Free Software Foundation, either        #
#    version 3 of the License, or (at your option) any later version.                              #
#                                                                                                  #
#    SPY is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;              #
#    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.     #
#    See the GNU Affero General Public License for more details.                                   #
#                                                                                                  #
#    You should have received a copy of the GNU Affero General Public License                      #
#    along with SPY.  If not, see <http://www.gnu.org/licenses/>.                                  #
####################################################################################################
import os.path as op
try:
    import cv2
except:
    print '[OCFaceDetector] Can not import cv2. This module will raise a RuntimeException.'
import yarp


from spy.modules.BaseModule import BaseModule, main
from spy.utils              import getFiles


class OCFaceDetector(BaseModule):
    """ The OCFaceDetector class provides a yarp module for recognizing faces based on the OpenCV
        Haarcasade Classifier implementation.
    """
    D_WIDTH      = 640
    D_HEIGHT     = 480

    O_HORIZONTAL = 0
    O_VERTICAL   = 1

    HC           = {}


    #
    # Global initialization of the haarcascades
    #
    files = getFiles('/usr/local/share/opencv/haarcascades')
    for _file in files:
        _, filename = op.split(_file)

        if filename.startswith('haarcascade'):
            cname = filename.replace('haarcascade_', '').replace('.xml', '')
            HC[cname] = cv2.CascadeClassifier(_file)
    
    
    def configure(self, rf):

        BaseModule.configure(self, rf)
    
        self.facesPort  = self.createOutputPort('faces')

        self.imgInPort   = self.createInputPort('img')
        self.imgOutPort  = self.createOutputPort('img')
        
        self.bufImageIn,  self.bufArrayIn  = self.createImageBuffer(640, 480, 3)
        self.bufImageOut, self.bufArrayOut = self.createImageBuffer(640, 480, 3)
    
        return True

                

    
    def updateModule(self):
        
        if self.imgInPort.read(self.bufImageIn):
            
            # Make sure the image has not been re-allocated
            assert self.bufArrayIn.__array_interface__['data'][0] == self.bufImageIn.getRawImage().__long__()

            # convert image to be usable in OpenCV
            image  = cv2.cvtColor(self.bufArrayIn, cv2.COLOR_BGR2RGB)

            # and convert image back to something the yarpview can understand
            self.bufArrayOut[:,:] = cv2.cvtColor(self.onImage(image), cv2.COLOR_RGB2BGR)

            # Send the result to the output port
            self.imgOutPort.write(self.bufImageOut)
            
        return True


    def sendFaces(self, faces):
        """ This method sends the marker information to the markers port.

        Message: <number of markers> ( ( <id> <center-x>  <center-y> <contour> )* )
                 <contour> = (<p1-x> <p1-y> <p2-x> <p2-y> <p3-x> <p3-y> <p4-x> <p4-y>)

        All values are integer values.

        @param markers - list of HammingMarker from ar_markers package.
        """

        bottle  = yarp.Bottle()
        bottle.clear()

        bottle.addInt(len(faces))
        faces_list = bottle.addList()

        face_id = 0        
        for (x, y, w, h) in faces:
            
            _values      = faces_list.addList()
            _values.addInt(face_id)
            _values.addInt(int((x + w) / 2.0))
            _values.addInt(int((y + h) / 2.0))
            _contour     = _values.addList()
            face_contour = [(x, y), (x + w, y), (x + w, y + h), ( x, y + h )]

            for (x, y) in face_contour:
                _contour.addInt(int(x))
                _contour.addInt(int(y))
         
            face_id += 1
         
        self.facesPort.write(bottle)


    def onImage(self, cv2_image):
        """ This method gets called upon receiving an input image given by cv2_image. 
        
        The method detects faces and draws a bounding box around them on the output image. 
        Afterwards the additional information is send to the corresponding ports.
        
        @param cv2_image - an OpenCV image object
        """

        # we only care for one contour
        gray  = cv2.cvtColor(cv2_image, cv2.COLOR_RGB2GRAY)
        faces = OCFaceDetector.HC['frontalface_default'].detectMultiScale(gray, 1.3, 5)
        
        for (x,y,w,h) in faces:
            cv2.rectangle(cv2_image,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray  = gray[y:y+h, x:x+w]
            roi_color = cv2_image[y:y+h, x:x+w]
            eyes = OCFaceDetector.HC['eye'].detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                
        self.sendFaces(faces)

        return cv2_image


if __name__ == '__main__':
    main(OCFaceDetector)