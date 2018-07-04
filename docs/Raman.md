# Raman

this is the documentation for the backend program Raman.

The Raman directory is the backend program for the server or embeded host computer connected to the CCD controller physically. The corresponding drivers and python dependencies must be installed on the device that runs the backend program.
To start the backend server, run the following command outside the Raman directory.

    python3 -m bokeh serve Raman --allow-websocket-origin={allowed_origin}

Once the backend is up and running, you can access the frontend via [http://{allowed_origin}:5006/Raman](http://{allowed_origin}:5006/Raman). If all origins are allowed, just run

    python3 -m bokeh serve Raman --allow-websocket-origin=*

## Settings

There are a lot of default settings in the `raman_configs.py` affecting logics of the backend program.

Note: if the IS_TESTING is set to True, the program will not get data from real port, instead it will use generated random fake data for testing.

## CCD Protocol Parser

Rewrite `CCD_protocol_parser.py` if the CCD controller protocol is modified.

## Custom JavasScript Calls

Custom javascript calls are stored in `static/js/` directory. If you need to add more frontend functionalities, add them inside this folder and create corresponding calls in the main python program, or include them directly inside the html template at `templates/index.html`.

## Styling and appearence

### Theme

To modify the style of plotting or appearence of other elements, add you own settings in `Raman/theme.yaml` to override default settings.

For example, you can add the following lines in `Raman/theme.yaml` to see the change in appearence.

    attrs:
        Plot:
            background_fill_color: "#282828"
            border_fill_color: "#282828"
            outline_line_color: "#49483E"
        Axis:
            axis_label_standoff: 10
            axis_label_text_font_size="15pt"
            axis_line_color: "#49483E"
        BasicTicker:
            num_minor_ticks: 2
        PrintfTickFormatter:
            format: "%4.1e"

### CSS

You can also completely change every element of the front-end page by adding you own CSS file to `static/css/`

### Static Images

If you plan to add images or logos, put them in `static/images/` and include them in `templates/index.html`

### Layout

To change the layout of elements, modify the Jinja templates inside `templates` folder and link the variables in `main.py`.