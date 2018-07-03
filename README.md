
# raman-spectroscopy-software

Software for Raman spectroscopy instruments

# Dependencies

pyserial, numpy, Bokeh, dicttoxml, pandas, scipy

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
