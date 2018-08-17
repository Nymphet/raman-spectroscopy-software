# -*- coding: utf-8 -*-

import base64
import io
import json
import logging
import os
import select
import sys
import time

# Math
import numpy as np
from scipy import signal
# System
import serial
# Bokeh
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import (Button, DataTable, Div, NumberEditor,
                                  NumberFormatter, RadioButtonGroup,
                                  RangeSlider, Select, Slider, TableColumn,
                                  TextInput)
from bokeh.plotting import curdoc, figure, output_file, show
# Tornado
from tornado import gen

# Local packages
import CCD_protocol_parser
import CCD_utils
import fake_serial
import raman_configs
import raman_languages

### -------------- get things ready --------------- ###

# system
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# --- Bokeh related
# Save current Bokeh document for later use
doc = curdoc()

# define tools used
spectrum_tools = "box_select,box_zoom,lasso_select,pan,poly_select,tap,wheel_zoom,undo,redo,reset,save,crosshair,hover"

# prepare empty figures
rawdata_figure = figure(title=raman_languages.TEXT__REAL_TIME_DAQ, x_axis_label=raman_languages.TEXT__PIXEL,
                        y_axis_label=raman_languages.TEXT__INTENSITY, plot_width=900, plot_height=500, tools=spectrum_tools)
raman_spec_figure = figure(title=raman_languages.TEXT__RAMAN,
                           x_axis_label=raman_languages.WAVELENGTH_UNIT,
                           y_axis_label=raman_languages.TEXT__INTENSITY, plot_width=900, plot_height=500, tools=spectrum_tools)

# prepare empty data
intensities = np.array([0] * raman_configs.PIXELS_WIDTH)
rawdata_x = np.array(range(raman_configs.PIXELS_WIDTH))
raman_spec_x = np.array(range(raman_configs.PIXELS_WIDTH))

# Link datasource for raman spec and raw data (shared intensities)
waveform_data_source = ColumnDataSource(
    data=dict(rawdata_x=rawdata_x, raman_spec_x=raman_spec_x, intensities=intensities))

# draw the lines
rawdata_waveform = rawdata_figure.line('rawdata_x', 'intensities',
                                       line_width=1, source=waveform_data_source)
raman_spec_waveform = raman_spec_figure.line(
    'raman_spec_x', 'intensities', line_width=1, source=waveform_data_source)

# --- a lot of default settings
user_serial_port = raman_configs.DEFAULT_SERIAL_PORT
user_baud_rate = raman_configs.DEFAULT_BAUD_RATE

user_CCD_integration_interval = raman_configs.DEFAULT_CCD_INTEGRATION_INTERVAL
user_CCD_integration_unit = raman_configs.DEFAULT_CCD_INTEGRATION_UNIT

user_save_path = raman_configs.DEFAULT_SAVE_PATH
user_selected_data_file_format = raman_configs.DEFAULT_FILE_FORMAT
auto_append_current_time = raman_configs.AUTO_APPEND_CURRENT_TIME

user_calibration_params = raman_configs.DEFAULT_CALIBRATION_PARAMS
user_selected_calibration_regression_model = raman_configs.DEFAULT_CALIBRATION_REGRESSION_MODEL
calibrate_model = CCD_utils.create_1d_regression(
    user_calibration_params, user_selected_calibration_regression_model)

user_AUTO_PEAK_DETECT_MIN_SNR = raman_configs.AUTO_PEAK_DETECT_MIN_SNR
user_AUTO_PEAK_DETECT_WIDTHS_MIN = raman_configs.AUTO_PEAK_DETECT_WIDTHS_MIN
user_AUTO_PEAK_DETECT_WIDTHS_MAX = raman_configs.AUTO_PEAK_DETECT_WIDTHS_MAX
peaks = []
peaks_data_source = ColumnDataSource(data=dict(peaks=peaks, wavenumber_peaks=calibrate_model(
    peaks), intensities=np.array([waveform_data_source.data['intensities'][i] for i in peaks])))
peaks_marks = raman_spec_figure.inverted_triangle(
    'wavenumber_peaks', 'intensities', source=peaks_data_source, color='pink')

user_NOISE_SAMPLE_SIZE = 100
user_SIGNAL_SAMPLE_SIZE = 100
user_SAMPLE_INTERVAL_IN_SECONDS = 5


# --- before serial port is opened, it should be none.
ser = None

### -------------- get things ready --------------- ###


### -------------- define callbacks --------------- ###
def callback_select_serial_port_text_input(att, old, new):
    global user_serial_port
    try:
        user_serial_port = select_serial_port_text_input.value
    except Exception as inst:
        print(type(inst), inst.args)


def callback_select_baud_rate_text_input(attr, old, new):
    global user_baud_rate
    try:
        user_baud_rate = int(
            select_baud_rate_text_input.value)
    except Exception as inst:
        print(type(inst), inst.args)


def callback_open_serial_port():
    global ser
    global user_serial_port
    global user_baud_rate
    # --- Serial port related
    # open serial port
    if raman_configs.IS_TESTING:
        ser = fake_serial.FakeSerial()
    else:
        ser = serial.Serial(user_serial_port,
                            user_baud_rate, timeout=1)

    # --- configure CCD to it's default settings
    # default integration time
    ser.write(CCD_protocol_parser.to_set_integration_time_command(
        raman_configs.DEFAULT_CCD_INTEGRATION_INTERVAL, raman_configs.DEFAULT_CCD_INTEGRATION_UNIT))


@gen.coroutine
def callback_update_data():
    # Tornado async coroutine to update rawdata
    if ser.inWaiting():
        intensities = CCD_protocol_parser.read_data(ser)
        new_data = dict()
        new_data['intensities'] = intensities
        new_data['rawdata_x'] = rawdata_x
        new_data['raman_spec_x'] = calibrate_model(rawdata_x)
        waveform_data_source.data = new_data


@gen.coroutine
def callback_update_raman_spec():
    new_data = dict()
    new_data['intensities'] = waveform_data_source.data['intensities']
    new_data['rawdata_x'] = rawdata_x
    new_data['raman_spec_x'] = calibrate_model(rawdata_x)
    waveform_data_source.data = new_data


@gen.coroutine
def callback_update_calibrate_curve():
    new_data = dict()
    new_data['pixel_indices'] = calibrate_curve_data_source.data['pixel_indices']
    new_data['wavenumbers'] = calibrate_model(new_data['pixel_indices'])
    calibrate_curve_data_source.data = new_data


def callback_start_collecting_data_button():
    ser.write(raman_configs.START_COMMAND)
    # Check if there is new data every 10 ms
    doc.add_periodic_callback(callback_update_data, 10)


def callback_stop_button():
    try:
        doc.remove_periodic_callback(callback_update_data)
    except Exception as inst:
        print(type(inst), inst.args)
    try:
        doc.remove_periodic_callback(callback_collect_noise_data_average)
    except Exception as inst:
        print(type(inst), inst.args)
    try:
        doc.remove_periodic_callback(callback_collect_signal_data_average)
    except Exception as inst:
        print(type(inst), inst.args)
    try:
        ser.write(raman_configs.STOP_COMMAND)
    except Exception as inst:
        print(type(inst), inst.args)


def callback_onestep_button():
    ser.write(raman_configs.ONESTEP_COMMAND)
    doc.add_next_tick_callback(callback_update_data)


def callback_select_integration_time_text_input(attr, old, new):
    global user_CCD_integration_interval
    try:
        user_CCD_integration_interval = int(
            select_integration_time_text_input.value)
    except Exception as inst:
        print(type(inst), inst.args)


def callback_select_integration_time_unit_radio_button_group(attr, old, new):
    global user_CCD_integration_unit
    user_CCD_integration_unit = ['ms', 's'][int(
        select_integration_time_unit_radio_button_group.active)]


def callback_set_integration_time_button():
    global user_CCD_integration_interval, user_CCD_integration_unit
    ser.write(CCD_protocol_parser.to_set_integration_time_command(
        user_CCD_integration_interval, user_CCD_integration_unit))
    # print(user_CCD_integration_interval, user_CCD_integration_unit)


def callback_save_path_text_input(attr, old, new):
    global user_save_path
    user_save_path = save_path_text_input.value


def callback_auto_append_current_time_or_not_radio_button_group(attr, old, new):
    global auto_append_current_time
    auto_append_current_time = [
        True, False][int(auto_append_current_time_or_not_radio_button_group.active)]


def callback_select_data_file_format_select(attr, old, new):
    global user_selected_data_file_format
    user_selected_data_file_format = select_data_file_format_select.value

# old style, save to some path without prompting. The new save button uses its own CustomJS callback


def callback_save_data_button():
    global user_selected_data_file_format
    global user_save_path
    global auto_append_current_time
    CCD_utils.save_data(user_selected_data_file_format,
                        user_save_path, waveform_data_source.data,
                        auto_append_current_time)


# --- load local file
file_source = ColumnDataSource({'file_contents': [], 'file_name': []})


def file_callback(attr, old, new):
    loaded_file_div.text = '<font color=#006699>'+ raman_languages.TEXT__LOADED_FILE +': </font>' + \
        file_source.data['file_name'][0]
    raw_contents = file_source.data['file_contents'][0]
    # # remove the prefix that JS adds
    prefix, b64_contents = raw_contents.split(",", 1)
    file_contents = base64.b64decode(b64_contents).decode()
    file_io = io.StringIO(file_contents)
    data_dict_from_file = json.load(file_io)
    rawdata_waveform.data_source.data = data_dict_from_file


file_source.on_change('data', file_callback)


def callback_select_calibration_regression_model_select(attr, old, new):
    global user_selected_calibration_regression_model, calibrate_model
    user_selected_calibration_regression_model = select_calibration_regression_model_select.value
    calibrate_model = CCD_utils.create_1d_regression(
        calibrate_params_source.data, user_selected_calibration_regression_model)
    doc.add_next_tick_callback(callback_update_raman_spec)
    doc.add_next_tick_callback(callback_update_calibrate_curve)


def callback_calibrate_params_change(attr, old, new):
    global calibrate_model
    calibrate_model = CCD_utils.create_1d_regression(
        calibrate_params_source.data, user_selected_calibration_regression_model)
    doc.add_next_tick_callback(callback_update_raman_spec)
    doc.add_next_tick_callback(callback_update_calibrate_curve)


def callback_auto_detect_peaks_snr_slider(attr, old, new):
    global user_AUTO_PEAK_DETECT_MIN_SNR
    user_AUTO_PEAK_DETECT_MIN_SNR = auto_detect_peaks_snr_slider.value


def callback_auto_detect_peaks_widths_range_slider(attr, old, new):
    global user_AUTO_PEAK_DETECT_WIDTHS_MIN, user_AUTO_PEAK_DETECT_WIDTHS_MAX
    user_AUTO_PEAK_DETECT_WIDTHS_MIN, user_AUTO_PEAK_DETECT_WIDTHS_MAX = auto_detect_peaks_widths_range_slider.value


def callback_auto_detect_peaks_button():
    global peaks
    global user_AUTO_PEAK_DETECT_MIN_SNR
    peaks = signal.find_peaks_cwt(
        waveform_data_source.data['intensities'], np.arange(user_AUTO_PEAK_DETECT_WIDTHS_MIN, user_AUTO_PEAK_DETECT_WIDTHS_MAX), min_snr=user_AUTO_PEAK_DETECT_MIN_SNR,
    )
    new_peaks_data = dict()
    new_peaks_data['peaks'] = peaks
    new_peaks_data['wavenumber_peaks'] = calibrate_model(peaks)
    new_peaks_data['intensities'] = np.array([
        waveform_data_source.data['intensities'][i] for i in peaks]) + raman_configs.PEAK_MARKS_OVERHANG
    peaks_data_source.data = new_peaks_data


def callback_set_sample_interval_text_input(attr, old, new):
    global user_SAMPLE_INTERVAL_IN_SECONDS
    try:
        user_SAMPLE_INTERVAL_IN_SECONDS = int(
            set_sample_interval_text_input.value)
    except Exception as inst:
        print(type(inst), inst.args)
    # print(user_SAMPLE_INTERVAL_IN_SECONDS)


def callback_set_noise_sample_size_text_input(attr, old, new):
    global user_NOISE_SAMPLE_SIZE
    try:
        user_NOISE_SAMPLE_SIZE = int(
            set_noise_sample_size_text_input.value)
    except Exception as inst:
        print(type(inst), inst.args)
    # print(user_NOISE_SAMPLE_SIZE)


def callback_set_signal_sample_size_text_input(attr, old, new):
    global user_SIGNAL_SAMPLE_SIZE
    try:
        user_SIGNAL_SAMPLE_SIZE = int(
            set_signal_sample_size_text_input.value)
    except Exception as inst:
        print(type(inst), inst.args)
    # print(user_SIGNAL_SAMPLE_SIZE)

noise_sample_counter = 0

@gen.coroutine
def callback_collect_noise_data_average():
    global noise_sample_counter
    global noise_data_list
    global noise_data_averaged_dict
    if noise_sample_counter <= 0:
        doc.remove_periodic_callback(callback_collect_noise_data_average)
        sampling_noise_div.text = raman_languages.TEXT__NOISE_FINISHED_SAMPLING
        noise_data_averaged_dict = CCD_utils.average_over_samples(noise_data_list)
        waveform_data_source.data = noise_data_averaged_dict
    if ser.inWaiting():
        intensities = CCD_protocol_parser.read_data(ser)
        new_data = dict()
        new_data['intensities'] = intensities
        new_data['rawdata_x'] = rawdata_x
        new_data['raman_spec_x'] = calibrate_model(rawdata_x)
        waveform_data_source.data = new_data
        noise_data_list.append(new_data)
        sampling_noise_div.text = raman_languages.TEXT__SAMPLING_NOISE + ": {noise_sample_counter}".format(noise_sample_counter=noise_sample_counter)
        noise_sample_counter = noise_sample_counter - 1


def callback_sample_noise_button():
    global user_SAMPLE_INTERVAL_IN_SECONDS
    global user_NOISE_SAMPLE_SIZE
    global ser
    # # stop current jobs
    # doc.add_next_tick_callback(callback_stop_button)
    # set integration time
    ser.write(CCD_protocol_parser.to_set_integration_time_command(
        user_SAMPLE_INTERVAL_IN_SECONDS, 's'))
    # prepare a new list to store data
    global noise_data_list
    noise_data_list = list()
    # check counter status, start to collect data
    global noise_sample_counter
    noise_sample_counter = user_NOISE_SAMPLE_SIZE
    doc.add_periodic_callback(callback_collect_noise_data_average, 10)


signal_sample_counter = 0

@gen.coroutine
def callback_collect_signal_data_average():
    global signal_sample_counter
    global signal_data_list
    global signal_data_averaged_dict
    if signal_sample_counter <= 0:
        doc.remove_periodic_callback(callback_collect_signal_data_average)
        sampling_signal_div.text = raman_languages.TEXT__SIGNAL_FINISHED_SAMPLING
        signal_data_averaged_dict = CCD_utils.average_over_samples(signal_data_list)
        waveform_data_source.data = signal_data_averaged_dict
    if ser.inWaiting():
        intensities = CCD_protocol_parser.read_data(ser)
        new_data = dict()
        new_data['intensities'] = intensities
        new_data['rawdata_x'] = rawdata_x
        new_data['raman_spec_x'] = calibrate_model(rawdata_x)
        waveform_data_source.data = new_data
        signal_data_list.append(new_data)
        sampling_signal_div.text = raman_languages.TEXT__SAMPLING_SIGNAL + ": {signal_sample_counter}".format(signal_sample_counter=signal_sample_counter)
        signal_sample_counter = signal_sample_counter - 1


def callback_sample_signal_button():
    global user_SAMPLE_INTERVAL_IN_SECONDS
    global user_SIGNAL_SAMPLE_SIZE
    global ser
    # # stop current jobs
    # doc.add_next_tick_callback(callback_stop_button)
    # set integration time
    ser.write(CCD_protocol_parser.to_set_integration_time_command(
        user_SAMPLE_INTERVAL_IN_SECONDS, 's'))
    # prepare a new list to store data
    global signal_data_list
    signal_data_list = list()
    # check counter status, start to collect data
    global signal_sample_counter
    signal_sample_counter = user_SIGNAL_SAMPLE_SIZE
    doc.add_periodic_callback(callback_collect_signal_data_average, 10)


def callback_subtract_noise_from_signal_button():
    global signal_data_averaged_dict
    global noise_data_averaged_dict
    waveform_data_source.data = CCD_utils.subtract_dict_data(signal_data_averaged_dict, noise_data_averaged_dict)
    doc.add_next_tick_callback(callback_update_raman_spec)



### -------------- define callbacks --------------- ###

### -------------- make the document -------------- ###


# --- add widgets
# Select Serial Port Text Input
select_serial_port_text_input = TextInput(
    title=raman_languages.TEXT__SERIAL_PORT, value=raman_configs.DEFAULT_SERIAL_PORT)
select_serial_port_text_input.on_change(
    'value', callback_select_serial_port_text_input)

# Select Baud Rate
select_baud_rate_text_input = TextInput(
    title=raman_languages.TEXT__BAUD_RATE, value=str(raman_configs.DEFAULT_BAUD_RATE))
select_baud_rate_text_input.on_change(
    'value', callback_select_baud_rate_text_input)

# Open Serial Port Button
open_serial_port_button = Button(label=raman_languages.TEXT__OPEN_SERIAL_PORT)
open_serial_port_button.on_click(callback_open_serial_port)

# Start Button
start_collect_data_button = Button(
    label=raman_languages.TEXT__START_COLLECTING_DATA, button_type='success')
start_collect_data_button.on_click(callback_start_collecting_data_button)

# Stop Button
stop_button = Button(label=raman_languages.TEXT__STOP_COLLECTING_DATA, button_type='warning')
stop_button.on_click(callback_stop_button)

# Onestep Button
onestep_button = Button(label=raman_languages.TEXT__ONESTEP)
onestep_button.on_click(callback_onestep_button)

# Select Integration Time
select_integration_time_text_input = TextInput(
    title=raman_languages.TEXT__INTEGRATION_TIME, value=str(raman_configs.DEFAULT_CCD_INTEGRATION_INTERVAL))
select_integration_time_text_input.on_change(
    'value', callback_select_integration_time_text_input)

# Unit of Integration Time
select_integration_time_unit_radio_button_group = RadioButtonGroup(
    labels=['ms', 's'], active=(1 if raman_configs.DEFAULT_CCD_INTEGRATION_UNIT == 's' else 0))
select_integration_time_unit_radio_button_group.on_change('active',
                                                          callback_select_integration_time_unit_radio_button_group)
# Set Integration Time
set_integration_time_button = Button(label=raman_languages.TEXT__SET_INTEGRATION_TIME)
set_integration_time_button.on_click(callback_set_integration_time_button)

# Save path
save_path_text_input = TextInput(
    title=raman_languages.TEXT__SAVE_TO, value=raman_configs.DEFAULT_SAVE_PATH)
save_path_text_input.on_change(
    'value', callback_save_path_text_input)
# If current time is automatically appended to the file name
auto_append_current_time_or_not_radio_button_group = RadioButtonGroup(
    labels=[raman_languages.TEXT__APPEND_TIME_TO_FILENAMES, raman_languages.TEXT__DONT_APPEND], active=(0 if raman_configs.AUTO_APPEND_CURRENT_TIME else 0))
auto_append_current_time_or_not_radio_button_group.on_change('active',
                                                             callback_auto_append_current_time_or_not_radio_button_group)

# Select file formats
select_data_file_format_select = Select(
    title=raman_languages.TEXT__DATA_FILE_FORMAT, value="JSON", options=["JSON", "XML", "CSV", "XLSX"])
select_data_file_format_select.on_change('value',
                                         callback_select_data_file_format_select)

# # Save Data Button
save_data_button = Button(label=raman_languages.TEXT__SAVE_CURRENT_DATA)
save_data_button.on_click(callback_save_data_button)

# # 20180704: just another way of saving data
with open(os.path.join(__location__, 'static/js/export_to_json.js'), 'r') as f:
    export_to_json_js = f.read()

export_data_as_json_button = Button(label=raman_languages.TEXT__EXPORT_CURRENT_DATA_AS_JSON, callback=CustomJS(
    args=dict(
        source=waveform_data_source,
    ),
    code=export_to_json_js))

with open(os.path.join(__location__, 'static/js/export_to_csv.js'), 'r') as f:
    export_to_csv_js = f.read()

export_data_as_csv_button = Button(label=raman_languages.TEXT__EXPORT_CURRENT_DATA_AS_CSV, callback=CustomJS(
    args=dict(
        source=waveform_data_source,
    ),
    code=export_to_csv_js))

# Load file button
with open(os.path.join(__location__, 'static/js/load_file.js'), 'r') as f:
    load_file_js = f.read()
load_file_button = Button(label=raman_languages.TEXT__LOAD_DATA_FROM_JSON_FILE, button_type='success', callback=CustomJS(
    args=dict(file_source=file_source), code=load_file_js))

loaded_file_div = Div(text=raman_languages.TEXT__LOADED_FILE_NONE)

# Calibration parameters list
calibrate_params_source = ColumnDataSource(user_calibration_params)
calibrate_params_source.on_change('data', callback_calibrate_params_change)

manual_calibrate_data_table_columns = [
    TableColumn(field="pixel_indices", title=raman_languages.TEXT__PIXEL_INDEX,
                editor=NumberEditor(), formatter=NumberFormatter()),
    TableColumn(field="wavenumbers", title=raman_languages.TEXT__WAVENUMBER+"/"+raman_languages.WAVELENGTH_UNIT,
                editor=NumberEditor(), formatter=NumberFormatter()),
]

manual_calibrate_data_table = DataTable(
    source=calibrate_params_source, columns=manual_calibrate_data_table_columns, editable=True, reorderable=True, sortable=True, width=300)

# Select model
select_calibration_regression_model_select = Select(
    title=raman_languages.TEXT__CALIBRATION_REGRESSION_MODEL, value=raman_configs.DEFAULT_CALIBRATION_REGRESSION_MODEL, options=raman_configs.CALIBRATION_REGRESSION_MODEL_CHOICES)
select_calibration_regression_model_select.on_change('value',
                                                     callback_select_calibration_regression_model_select)

# calibrate curve figure
calibrate_curve_figure = figure(title=raman_languages.TEXT__CALIBRATE_CURVE,
                                x_axis_label=raman_languages.TEXT__PIXEL,
                                y_axis_label=raman_languages.WAVELENGTH_UNIT, width=300, height=300)

calibrate_curve_data_source = ColumnDataSource(
    dict(
        pixel_indices=np.array(range(raman_configs.PIXELS_WIDTH)),
        wavenumbers=calibrate_model(
            np.array(range(raman_configs.PIXELS_WIDTH)))
    ))

calibrate_curve = calibrate_curve_figure.line(
    "pixel_indices", "wavenumbers", source=calibrate_curve_data_source, line_width=1)


# automatic peak detections
auto_detect_peaks_snr_slider = Slider(
    start=1, end=10, value=raman_configs.AUTO_PEAK_DETECT_MIN_SNR, step=1, title=raman_languages.TEXT__MINIMUM_SNR)
auto_detect_peaks_snr_slider.on_change(
    'value', callback_auto_detect_peaks_snr_slider)


auto_detect_peaks_widths_range_slider = RangeSlider(start=1, end=100, value=(
    raman_configs.AUTO_PEAK_DETECT_WIDTHS_MIN, raman_configs.AUTO_PEAK_DETECT_WIDTHS_MAX), step=1, title=raman_languages.TEXT__WIDTHS_TO_USE_FOR_CALCULATING_CWT_MATRIX)
auto_detect_peaks_widths_range_slider.on_change(
    'value', callback_auto_detect_peaks_widths_range_slider)

auto_detect_peaks_button = Button(label=raman_languages.TEXT__AUTOMATIC_PEAK_DETECTION)
auto_detect_peaks_button.on_click(callback_auto_detect_peaks_button)


auto_detect_peaks_columns = [
    TableColumn(field="wavenumber_peaks", title=raman_languages.TEXT__PEAKS+"/"+raman_languages.WAVELENGTH_UNIT,
                formatter=NumberFormatter()),
    TableColumn(field="intensities", title=raman_languages.TEXT__INTENSITY,
                formatter=NumberFormatter()),
]

auto_detect_peaks_data_table = DataTable(
    source=peaks_data_source, columns=auto_detect_peaks_columns, editable=False, reorderable=True, sortable=True, width=300)


# Sampling Noise and Signal by Averaging and Substraction

set_sample_interval_text_input = TextInput(
    title=raman_languages.TEXT__SAMPLIE_INTERVAL_IN_SECONDS, value=str(raman_configs.DEFAULT_SAMPLE_INTERVAL_IN_SECONDS))
set_sample_interval_text_input.on_change(
    'value', callback_set_sample_interval_text_input)

set_noise_sample_size_text_input = TextInput(
    title=raman_languages.TEXT__NOISE_SAMPLE_SIZE, value=str(raman_configs.DEFAULT_NOISE_SAMPLE_SIZE))
set_noise_sample_size_text_input.on_change(
    'value', callback_set_noise_sample_size_text_input)

set_signal_sample_size_text_input = TextInput(
    title=raman_languages.TEXT__SIGNAL_SAMPLE_SIZE, value=str(raman_configs.DEFAULT_SIGNAL_SAMPLE_SIZE))
set_signal_sample_size_text_input.on_change(
    'value', callback_set_signal_sample_size_text_input)

sample_noise_button = Button(label=raman_languages.TEXT__SAMPLE_NOISE)
sample_noise_button.on_click(callback_sample_noise_button)

sampling_noise_div = Div(text=raman_languages.TEXT__SAMPLING_NOISE+": 0")

sample_signal_button = Button(label=raman_languages.TEXT__SAMPLE_SIGNAL)
sample_signal_button.on_click(callback_sample_signal_button)

sampling_signal_div = Div(text=raman_languages.TEXT__SAMPLING_SIGNAL+": 0")

subtract_noise_from_signal_button = Button(label=raman_languages.TEXT__SUBTRACT_NOISE_FROM_SIGNAL)
subtract_noise_from_signal_button.on_click(callback_subtract_noise_from_signal_button)


# Place Holders
place_holder1 = Div(text="", height=20)
place_holder2 = Div(text="", height=20)
place_holder3 = Div(text="", height=20)


# --- Layouts

input_widgets = column(select_serial_port_text_input,
                       select_baud_rate_text_input,
                       open_serial_port_button,
                       start_collect_data_button,
                       stop_button, onestep_button, place_holder1,
                       select_integration_time_text_input,
                       select_integration_time_unit_radio_button_group,
                       set_integration_time_button,
                       place_holder2,
                       save_path_text_input,
                       select_data_file_format_select,
                       auto_append_current_time_or_not_radio_button_group,
                       save_data_button,
                       export_data_as_json_button,
                       export_data_as_csv_button,
                       place_holder3,
                       load_file_button,
                       loaded_file_div
                       )


figure_widgets = column(raman_spec_figure, rawdata_figure)

auto_peak_detection_widgets = column(auto_detect_peaks_snr_slider,
                                     auto_detect_peaks_widths_range_slider,
                                     auto_detect_peaks_button, auto_detect_peaks_data_table
                                     )

calibrate_widgets = column(manual_calibrate_data_table,
                           select_calibration_regression_model_select, calibrate_curve_figure)

signal_averaging_widgets = column(set_sample_interval_text_input,
                                  set_noise_sample_size_text_input, 
                                  set_signal_sample_size_text_input,
                                  sample_noise_button,
                                  sampling_noise_div,
                                  sample_signal_button,
                                  sampling_signal_div,
                                  subtract_noise_from_signal_button
                                  )


column1 = row(figure_widgets, input_widgets)
column2 = row(calibrate_widgets, auto_peak_detection_widgets,
              signal_averaging_widgets)


# put the button and plot in a layout and add to the document
doc.add_root(column(column1,
                    column2))

### -------------- make the document -------------- ###
