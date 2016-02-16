# SPY - A Sensor Module Package for Yarp

SPY is intended to ease development for yarp-based setups. It contains Yarp modules for (virtual) 
sensors and other types of input.


## Installation

1- Install the dependencies:

You need Yarp installed with the python bindings. For more details see 
[full instructions](http://wiki.icub.org/yarpdoc/install.html).

Example: OSX using [Homebrew](http://brew.sh)

    brew tap homebrew/x11
    brew install --with-python yarp


Additional dependencies:

    NumPy           [http://www.numpy.org/]
    OpenCV          [http://opencv.org/]
    PythonArMarkers [https://github.com/DebVortex/python-ar-markers.git]


2- Download the source code: 

    git clone https://github.com/BrutusTT/spy

3- build and install:

    cd spy
    python setup.py install


## Running SPY Modules

Each module can be started standalone using the following command line.


    python -m spy.modules.<ModuleName> [--name <Name Prefix>]

Parameters:

    []            - denotes optional parameter
    <ModuleName>  - can be one of the following: - HCMarker
                                                 - OCFaceDetector
                                                 - TSUserSkeleton
    <Name Prefix> - if a name is given it will be used as a prefix for the port names
                    e.g.:  --name test results in /test/JDModule/rpc

Example:

    python -m spy.modules.HCMarker --name MySpy


## General

The package contains Yarp modules that can be used to make (virtual) sensors or other types of input 
accessible to yarp-based setups. Once the modules are started, they provide RPC Ports for 
controlling the internal settings and additional ports for providing information.

The **HCMarker** module is used to recognize Hamming Marker and provides information about them.

    ...


Happy hacking!

## License

See COPYING for licensing info.
