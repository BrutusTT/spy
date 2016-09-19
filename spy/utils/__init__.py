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
import os
import os.path as op
import subprocess

# short cut for imports
from spy.utils.factory import YarpFactory


def getFiles(_path):
    """ This method returns a list of all files within a given \a path. If the path is already a
        file it returns the file contained in a list.

    This method does not return hidden files (files starting with a '.').

    @return List of files
    """

    # test for single file
    if op.isfile(_path):
        return [_path]

    elif op.isdir(_path):
        _ls = os.listdir
        _if = op.isfile
        _jo  = op.join
        return [ _jo(_path, f) for f in _ls(_path) if _if(_jo(_path, f)) and not f.startswith('.') ]

    return []


def executeWithLogs(cmd, name = 'log', directory = '/tmp', append = False):
    """ This method runs a command as a subprocess and writes it's output to log files.

    If cmd contains a yarp module call with the --name parameter then this name will used as a
    prefix for the log files. If it contains a path separator the log files will be put into a
    hierarchy.

    Examples:

        >>> executeWithLogs('yarpdev --device opencv_grabber --name /my/grabber')

        This will create the files:
        - /tmp/my/grabber_log_stderr.txt
        - /tmp/my/grabber_log_stdout.txt

        >>> executeWithLogs('yarpdev --device opencv_grabber --name /my/grabber', 'my_prefix')

        This will create the files:
        - /tmp/my/grabber_my_prefix_stderr.txt
        - /tmp/my/grabber_my_prefix_stdout.txt

        >>> executeWithLogs('echo "Hello World!"')

        This will create the files:
        - /tmp/log_stderr.txt
        - /tmp/log_stdout.txt

    @param cmd       - string or list of strings containing the command to be runned
    @param name      - explicit name for the log files; default is 'log'.
    @param directory - directory to which the output is written; default is '/tmp'.
    @param append    - if set to True log-files with the same name will extended; default is False.
    @return Popen object - returns the subprocess handle object
    """

    # if the command is issued in a string it is decompose into a list to fit the input of Popen
    if isinstance(cmd, type('')):
        cmd = cmd.split(' ')

    print 'Execute: ', ' '.join(cmd)

    # find name in command
    # just for convenience while using yarp modules
    if '--name' in cmd:
        name = '%s_%s' % (cmd[cmd.index('--name') + 1], name)

    # create sub-directories if there is path separator in the name
    if os.sep in name:
        directory = op.join(directory, op.split(name)[0])
        name      = op.split(name)[1]

    # create the directory if it is not yet present
    if not op.exists(directory):
        os.makedirs(directory)

    # appending or not appending ?
    if append:
        mode = 'a'
    else:
        mode = 'w'

    # redirect standard out and standard err to file and return the subprocess handle
    return subprocess.Popen( cmd,
                             stdout = open(op.join(directory, '%s_stdout.txt' % name), mode),
                             stderr = open(op.join(directory, '%s_stderr.txt' % name), mode) )
