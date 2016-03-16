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
import yarp

from spy.modules.BaseModule        import BaseModule, main
from spy.models.ts_skeleton        import TSSkeleton
from spy.reader.ts_skeleton_reader import TSSkeletonReader


class TSUserSkeleton(BaseModule):
    """ The TSUserSkeleton class provides a yarp module for the transformation between OpenNI2 
        userSkeleton and the TutorSpotter skeleton.
    """
    
    USED_JOINTS = { TSSkeleton.HEAD:   'Head', 
                    TSSkeleton.L_HAND: 'Left_Hand',
                    TSSkeleton.R_HAND: 'Right_Hand',
                    TSSkeleton.TORSO:  'Chest'  }

    def configure(self, rf):

        BaseModule.configure(self, rf)
    
        self.skeletonInPort  = self.createInputPort('skeleton',  'buffered')
        self.skeletonOutPort = self.createOutputPort('skeleton', 'buffered')
        return True

    
    def updateModule(self):
        
        # read the bottle              
        input_bottle    = self.skeletonInPort.read()

        # get the envelope as bottle            
        envelope_bottle = self.skeletonInPort.prepare()
        envelope_bottle.clear()
        self.skeletonInPort.getEnvelope(envelope_bottle)

        # if bottle exists run the convert method
        if input_bottle:
            self.onBottle(input_bottle, envelope_bottle)
        
        return True

    
    def onBottle(self, input_bottle, envelope_bottle):

        # ignore broken parsing such as "Calibration User" messages
        try:
            data = TSSkeletonReader(input_bottle).getData()
        except:
            return

        for key in data:

            # get data and fresh bottle
            skeleton = data[key]
            bottle   = yarp.Bottle()
            bottle.clear()
    
            for joint, label in TSUserSkeleton.USED_JOINTS.items():

                jData = skeleton.data[joint]
        
                bottle.addString(label)
                [bottle.addDouble(value) for value in ([jData['POS'][-1]] + jData['POS'][:3])]
                    
                bottle.addString("Orientation")
                bottle.addDouble(jData['ORI'][-1])
                [bottle.addDouble(value) for value in jData['ORI_RM'].flatten()]

            # pass the time value as first element in the envelop
            ebottle   = yarp.Bottle()
            ebottle.clear()
            ebottle.addDouble(envelope_bottle.get(1).asDouble())
                        
            self.skeletonOutPort.setEnvelope(ebottle)
            self.skeletonOutPort.write(bottle)


    def respond(self, command, reply):
        return True


if __name__ == '__main__':
    main(TSUserSkeleton)