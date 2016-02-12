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
import numpy as np
import yarp


EMSG_YARP_NOT_FOUND = "Could not connect to the yarp server. Try running 'yarp detect'."


class YarpFactory(object):


    def __createPort(self, name, target = None, mode = 'unbuffered'):
        """ This method returns a port object.
    
        @param name     - yarp name for the port
        @param obj      - object for which the port is created
        @param buffered - if buffered is True a buffered port will be used otherwise not; 
                          default is True.
        @result port
        """
        # create port
        if mode == 'buffered':
            port = yarp.BufferedPortBottle()
        elif mode == 'rpcclient':
            port = yarp.RpcClient()
    
        elif mode == 'rpcserver':
            port = yarp.RpcServer()
        
        else:
            port = yarp.Port()
    
        # open port
        if not port.open('/%s/%s' % (self.__class__.__name__, name)):
            raise RuntimeError, EMSG_YARP_NOT_FOUND
    
        # add output if given
        if target:
            port.addOutput(target)
    
        return port
    
    
    def createInputPort(self, name, mode = 'unbuffered'):
        """ This method returns an input port.
        
        @param obj      - the object that the port is created for
        @param name     - if a name is provided it gets appended to the modules name
        @param buffered - if buffered is True a buffered port will be used otherwise not; 
                          default is True.
        @result port
        """
        return self.__createPort(name + ':i', None, mode)
    
    
    def createOutputPort(self, name, target = None, mode = 'unbuffered'):
        """ This method returns an output port.
        
        @param obj      - the object that the port is created for
        @param name     - if a name is provided it gets appended to the modules name
        @param buffered - if buffered is True a buffered port will be used otherwise not; 
                          default is True.
        @result port
        """
        return self.__createPort(name + ':o', target, mode)
    
    
    def createRpcClientPort(self, name, target = None):
        """ This method returns an output port.
        
        @param obj      - the object that the port is created for
        @param name     - if a name is provided it gets appended to the modules name
        @param buffered - if buffered is True a buffered port will be used otherwise not; 
                          default is True.
        @result port
        """
        if name:
            name += ':rpc'
        else:
            name = 'rpc'
        return self.__createPort(name, target, 'rpcclient')
    
    
    def createRpcServerPort(self, name, obj = None, target = None):
        """ This method returns an output port.
        
        @param obj      - the object that the port is created for
        @param name     - if a name is provided it gets appended to the modules name
        @param buffered - if buffered is True a buffered port will be used otherwise not; 
                          default is True.
        @result port
        """
        if name:
            name += ':rpc'
        else:
            name = 'rpc'
        return self.__createPort(name, target, 'rpcserver')

    
    @staticmethod    
    def createImageBuffer(width = 320, height = 240, channels = 3):
    
        if channels == 1:
            buf_image = yarp.ImageFloat()
            buf_image.resize(width, height)
            
            buf_array = np.zeros((height, width), dtype = np.float32)
            
        else:
            buf_image = yarp.ImageRgb()
            buf_image.resize(width, height)
            
            buf_array = np.zeros((height, width, channels), dtype = np.uint8)
    
        buf_image.setExternal( buf_array, 
                               buf_array.shape[1], 
                               buf_array.shape[0] )
    
        return buf_image, buf_array
    
