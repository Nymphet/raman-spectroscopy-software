
# raman-spectroscopy-software

Software for Raman spectroscopy instruments.

Note: this is more of a prototype GUI software to controll the raman spectroscopy instrument, and only basic data processing functionalities are added because I only have very limited time on this project (~8 hours). There might still be a lot of bugs, sorry for any inconvenience.

# Dependencies

dependencies for the python backend:
pyserial, numpy, Bokeh, dicttoxml, pandas, scipy

dependencies for the electron app: see Raman-GUI/package.json

# Docs

The protocal of the CCD controller is in the docs folder.

## Raman

The Raman directory is the backend program for the server or embeded host computer connected to the CCD controller physically. The corresponding drivers and python dependencies must be installed on the device that runs the backend program.
To start the backend server, run the following command outside the Raman directory.

    python3 -m bokeh serve Raman --allow-websocket-origin={allowed_origin}

Once the backend is up and running, you can access the frontend via [http://{allowed_origin}:5006/Raman](http://{allowed_origin}:5006/Raman). If all origins are allowed, just run

    python3 -m bokeh serve Raman --allow-websocket-origin=*

## Raman-GUI

The Raman-GUI directory is another way to use the program without command line. Actually it is just the Raman backend wrapped with Electron. The corresponding drivers and python dependencies must be installed on the device running the GUI application, and the CCD controller is assumed to be connected to the same device. To test the program, inside the Raman-GUI directory, run

    npm install
    npm start

If everything works good, you can now build the Electron app with

    electron-packager . --overwrite

Note that for the application to work correctly, python must be added to the PATH variable. Or, you can also explicitly add the path to python executable to the main.js.

## Arduino_simulator

The Arduino_simulator is a simple CCD controller simulator that works on most arduino toy chips. The actual CCD controller is developed with stm32f40x chips and cyclone FPGA chips and is much faster than the simulator, so you should be careful when testing high speed sampling with the simulator.

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

# TODO

- The save-file functionality is currently implemented simply with a python function and is not very convenient to use. Consider switching to pure javascript call to save the file at frontend.
- There is no frontend design for now and the layout looks very strange. Consider integrating with Bootstrap.

# License

License for current version is the Apache License 2.0.

Copyright 2018 [Zhi Zi](mailto:x@zzi.io)
