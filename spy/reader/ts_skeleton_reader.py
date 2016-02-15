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
import time

from spy.reader.bottle_reader import BottleReader
from spy.models.ts_skeleton   import TSSkeleton


class TSSkeletonReader(BottleReader):
    """ The TSSkeletonReader class provides a BottleReader for the transformation from 
        OpenNI2DeviceServer skeleton to the TutorSpotter skeleton.
    """
    
    
    def __init__(self, bottle, create_time = None):
        self.mode        = None
        self.cur_user    = 0
        self.cur_joint   = 0
        self.create_time = create_time

        BottleReader.__init__(self, bottle)

    

    def readVocab(self, value):
        self.mode = value.asString()

        if 'POS' == self.mode:
            self.data[self.cur_user].append( { 'POS' : [], 'ORI' : [] } )


    def readDouble(self, value):
        self.data[self.cur_user][-1][self.mode].append(value.asDouble())


    def readInt(self, value):
        if 'USER' == self.mode:
            self.cur_user = value.asInt()
            self.data[self.cur_user] = []

        else:
            print 'wrong mode', self.mode  
            
            
    def getData(self):
        create_time = time.time()
        
        if self.create_time:
            create_time = self.create_time
        
        for key in self.data:
            self.data[key] = TSSkeleton(key, self.data[key], create_time)
            
        return BottleReader.getData(self)
