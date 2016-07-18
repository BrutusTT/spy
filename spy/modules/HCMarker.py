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
import argparse
import time
import yarp

try:
    import cv2
except:
    print '[HCMarkerModule] Can not import cv2. This module will raise a RuntimeException.'


try:
    from ar_markers.hamming.detect import detect_markers
except:
    print '[HCMarkerModule] Can not import ar_markers. This module will raise a RuntimeException.'

from spy.modules.BaseModule import BaseModule, main


class HCMarker(BaseModule):
    """ The HCMarkerModule class provides a yarp module for recognizing Hamming Markers. It is acts
        as a wrapper for the python-ar-markers package by DebVortex.
    """
    
    D_WIDTH  = 640
    D_HEIGHT = 480

    O_HORIZONTAL = 0
    O_VERTICAL   = 1
    
    
    def __init__(self, args):
        BaseModule.__init__(self, args)
        self.memory_length = args.memory


    def configure(self, rf):

        BaseModule.configure(self, rf)
    
        self.markersPort = self.createOutputPort('markers')
        self.orderPort   = self.createOutputPort('order')

        self.imgInPort   = self.createInputPort('img')
        self.imgOutPort  = self.createOutputPort('img')
        
        self.bufImageIn,  self.bufArrayIn  = self.createImageBuffer(640, 480, 3)
        self.bufImageOut, self.bufArrayOut = self.createImageBuffer(640, 480, 3)
    
        self.order           = HCMarker.O_HORIZONTAL
        self.orderIsReversed = False
        
        self.memory          = {}
        
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


    def sendOrder(self, markers):
        """ This method sends the order information to the order port.

        Message: <markerid_1> <markerid_2> ... <markerid_n>

        All values are integer values.

        @param markers - list of HammingMarker from ar_markers package.
        """

        markers.sort(key = lambda x: x.center[self.order], reverse = self.orderIsReversed)

        bottle = yarp.Bottle()
        bottle.clear()

        for marker in markers:
            bottle.addInt(marker.id)
            
        self.orderPort.write(bottle)
        

    def sendMarkers(self, markers):
        """ This method sends the marker information to the markers port.

        Message: <number of markers> ( ( <id> <center-x>  <center-y> <contour> )* )
                 <contour> = (<p1-x> <p1-y> <p2-x> <p2-y> <p3-x> <p3-y> <p4-x> <p4-y>)

        All values are integer values.

        @param markers - list of HammingMarker from ar_markers package.
        """

        bottle  = yarp.Bottle()
        bottle.clear()

        bottle.addInt(len(markers))
        markers_list = bottle.addList()
        
        for marker in markers:
        
            cx, cy        = marker.center
            marker_values = markers_list.addList()
            marker_values.addInt(marker.id)
            marker_values.addInt(cx)
            marker_values.addInt(cy)
            marker_contour = marker_values.addList()

            for value in marker.contours:
                marker_contour.addInt(int(value[0][0]))
                marker_contour.addInt(int(value[0][1]))
         
        self.markersPort.write(bottle)


    def onImage(self, cv2_image):
        """ This method gets called upon receiving an input image given by cv2_image. 
        
        The method detects the markers. Then it chooses one HammingMarker object for each recognized
        marker id and draws it on the output image. Afterwards the additional information is send to
        the corresponding ports.
        
        @param cv2_image - an OpenCV image object
        """

        # we only care for one contour
        markers = {}
        for marker in detect_markers(cv2_image):
            markers[marker.id] = marker

        marker_list = [ markers[mid] for mid in markers ]

        # handle memory
        if self.memory_length > 0:
            
            # set all current marker information
            cur_time = time.time()
            for marker in marker_list:
                self.memory[marker.id] = ( marker, cur_time )

            # create new marker list and only include marker which are within the time frame
            marker_list = [ self.memory[mid][0] for mid in self.memory if cur_time - self.memory[mid][1] < self.memory_length ]

        # highlight markers in output image        
        for marker in marker_list:
            marker.highlite_marker(cv2_image)

        self.sendMarkers(marker_list)
        self.sendOrder(marker_list)

        return cv2_image


    def respond(self, command, reply):

        success = False
        command = command.toString().split(' ')
        
        if command[0] == 'set':
            
            if command[1] == 'order':
                
                if command[2] == 'horizontal':
                    self.order = HCMarker.O_HORIZONTAL
                    success = True

                elif  command[2] == 'vertical':
                    self.order = HCMarker.O_VERTICAL
                    success = True

                elif command[2] == 'reverse':
                    self.orderIsReversed = not self.orderIsReversed
                    success = True

        elif command[0] == 'get':

            if command[1] == 'order':
                reply.add('horizontal' if self.order == HCMarker.O_HORIZONTAL else 'vertical')
                reply.add('normal' if not self.orderIsReversed else 'reversed')
                success = True

        elif command[0] == 'memory':

            self.memory_length = float(command[1])
            success = True


        reply.addString('ack' if success else 'nack')
        return True


def createArgParser():
    """ This method creates a base argument parser. 
    
    @return Argument Parser object
    """
    parser = argparse.ArgumentParser(description='Create a SensorModule for Yarp.')
    parser.add_argument( '-n', '--name', 
                         dest       = 'name', 
                         default    = '',
                         help       = 'Name prefix for Yarp port names')

    parser.add_argument( '-m', '--memory', 
                         dest       = 'memory', 
                         type       = type(0),
                         default    = 0,
                         help       = 'Defines how long the marker positions are kept in memory.')

    return parser.parse_args()


if __name__ == '__main__':
    main(HCMarker, createArgParser())