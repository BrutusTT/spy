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


class TSSkeleton(object):
    """ The TSSkeleton class provides a skeleton for the tutor spotter module. """
    

    JOINT_LABELS = [ 'head',            'neck', 
                     'left shoulder',   'right shoulder', 
                     'left elbow',      'right elbow',
                     'left hand',       'right hand',
                     'torso',
                     'left hip',        'right hip',
                     'left knee',       'right knee',
                     'left foot',       'right foot' ]

    HEAD        = 0
    NECK        = 1
    
    L_SHOULDER  = 2
    R_SHOULDER  = 3
    L_ELBOW     = 4
    R_ELBOW     = 5
    L_HAND      = 6
    R_HAND      = 7

    TORSO       = 8

    L_HIP       = 9
    R_HIP       = 10
    L_KNEE      = 11
    R_KNEE      = 12
    L_FOOT      = 13
    R_FOOT      = 14
    
    # ORI_RM - Orientation Rotation Matrix

    def __init__(self, userid, data_dict = None, create_time = None):

        # overloaded constructor
        if isinstance(userid, dict):
            self.uid          = userid['uid'] 
            self.data         = userid['data']
            self.create_time  = userid['create_time']
        else:
            self.uid          = userid
            self.data         = data_dict
            self.create_time  = create_time

        for i in range(len(self.data)):
            self.data[i]['ORI_RM'] = self.quaternion_to_R(self.data[i]['ORI'])


    def getJoint(self, joint):
        """ This method returns the position and orientation information for the specified joint. 
        
        @param joint: the selected joint \see joint constants.
        @type  joint: integer
        """
        return self.data[joint]['POS'] + self.data[joint]['ORI']

        
    def quaternion_to_R(self, quat):
        """Convert a quaternion into rotation matrix form.
    
        @param quat:    The quaternion.
        @type  quat:    numpy 4D, rank-1 array
        @param matrix:  A 3D matrix to convert to a rotation matrix.
        @type  matrix:  numpy 3D, rank-2 array
        """
    
        # Repetitive calculations.
        q4_2 = quat[3]**2
        q12 = quat[0] * quat[1]
        q13 = quat[0] * quat[2]
        q14 = quat[0] * quat[3]
        q23 = quat[1] * quat[2]
        q24 = quat[1] * quat[3]
        q34 = quat[2] * quat[3]
    
        # The diagonal.
        matrix = np.zeros( (3, 3) )
        matrix[0, 0] = 2.0 * (quat[0]**2 + q4_2) - 1.0
        matrix[1, 1] = 2.0 * (quat[1]**2 + q4_2) - 1.0
        matrix[2, 2] = 2.0 * (quat[2]**2 + q4_2) - 1.0
    
        # Off-diagonal.
        matrix[0, 1] = 2.0 * (q12 - q34)
        matrix[0, 2] = 2.0 * (q13 + q24)
        matrix[1, 2] = 2.0 * (q23 - q14)
    
        matrix[1, 0] = 2.0 * (q12 + q34)
        matrix[2, 0] = 2.0 * (q13 - q24)
        matrix[2, 1] = 2.0 * (q23 + q14)
        return matrix


    def __str__(self):
        txt = ['User %s' % self.uid]
        for idx in range(len(self.data)):
            pos = ', '.join([ '%.2f' % pos for pos in self.data[idx]['POS'] ])
            ori = ', '.join([ '%s' % ori for ori in self.data[idx]['ORI'] ])
            txt.append( '%s: position[%s], orientation[%s]' % ( TSSkeleton.JOINT_LABELS[idx],
                                                                pos,
                                                                ori ) )
        return '\n'.join(txt)
    
    
    def __repr__(self):
        data = {}
        for idx in range(len(self.data)):
            data[idx] = {}
            data[idx]['POS'] = self.data[idx]['POS']
            data[idx]['ORI'] = self.data[idx]['ORI']
            
        return str( {'uid': self.uid, 'create_time' : self.create_time, 'data': data} )
