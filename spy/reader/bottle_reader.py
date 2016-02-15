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
from yarp import Bottle, Value


class BottleReader(object):
    """ The BottleReader class provides an abstract, simple tree walker base class for complex yarp
        bottles.
    """

    E_ABSTRACT_CALL = 'Call of an abstract method. Implement if you inherit from BottleReader!'

    
    def __init__(self, bottle):
        """ This method creates the bottle reader and starts the reading. 
        
        @param bottle - Yarp Bottle
        """

        self.data = {}
        
        # flags
        self.vocabAsString = True

        # do the work
        self._readBottle(bottle)
    

    def _readBottle(self, bottle):
        """ This protected method is called to start the tree walking. 

        @param bottle - Yarp Bottle
        """

        for idx in range(bottle.size()):
            item = bottle.get(idx)

            if isinstance(item, Value):
                self._readValue(item)

            elif isinstance(item, Bottle):
                self._readBottle(item)
            

    def _readValue(self, value):
        """ This protected method is used to call the hook methods for each value type. """
        
        if value.isVocab():
            self.readVocab(value)

        elif value.isDouble():
            self.readDouble(value)

        elif value.isInt():
            self.readInt(value)

        elif value.isList():
            self.onListStart()
            self._readBottle( value.asList() )
            self.onListEnd()

        else:
            raise NotImplementedError('Value type is not known to the parser: %s' % value)


    def getData(self):
        """ This method needs to return the parsed data. 
        
        @result dictionary containing the parsed data
        """
        return self.data
    
    ################################################################################################
    #
    # Tree Walker Abstract Methods
    #
    ################################################################################################
    def readVocab(self, value):
        """ This method is the hook method to read vocab values. """
        raise NotImplementedError(BottleReader.E_ABSTRACT_CALL)


    def readDouble(self, value):
        """ This method is the hook method to read double values. """
        raise NotImplementedError(BottleReader.E_ABSTRACT_CALL)


    def readInt(self, value):
        """ This method is the hook method to read integer values. """
        raise NotImplementedError(BottleReader.E_ABSTRACT_CALL)


    def onListStart(self):
        """ This method is the hook method that is called if a new list was found. """
        pass
    
    
    def onListEnd(self):
        """ This method is the hook method that is called if a list has finished. """
        pass
