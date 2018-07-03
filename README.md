
# raman-spectroscopy-software

Software for Raman spectroscopy instruments

# Dependencies

pyserial, numpy, Bokeh, dicttoxml, pandas, scipy

# Docs

The protocal of the CCD controller is in the docs folder.

Currently the bokeh app is in Raman directory, I'm working on integrate the app with electron.

The Arduino_simulator is a simple CCD controller simulator that works on most arduino toy chips, it's very simple because I only have very limited time (~8 hours) on this project. Sorry for any bugs. The actual CCD controller is developed with STM32f40x chips and cyclone FPGA chips and is much faster than the simulator, so you should be careful when testing high speed sampling with the simulator.

# Design

        Frontend---------------------GUI: electron / web <-------------- theme configs
        |Javascript Callback                |
        |                                   |
    ----+-----------------------------------+--------------------------- Instrument
        Backend                             |
        |                                   |
        |                                   |
        |                                   |
        |       |Renderer ------------>   Bokeh  <---------------------- Configs
        |       |     |
        ------> |     +-----------------------<------------------------+
        |       |                                                      |
        |       |Data ----------------> VCP -------------> Binary Stream Parser ----> Other Data Manipulation Tools
        |                                |
        |                                | USB
        |                                |
        |       |Sensor  -------------> CCD                         |
        +-----> |                                                   |   Hardwares
                |Mechanical Parts , Optical Parts & Electronics     |

# License

License for current version is the Apache License 2.0.
