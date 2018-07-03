# testing mod
IS_TESTING = True

# Width of CCD pixels
PIXELS_WIDTH = 3694

# Serial port settings
SERIAL_PORT = '/dev/tty.usbserial-A505LIEG'
BAUD_RATE = 921600

# protocols
STOP_COMMAND = '#Stop%'.encode()
START_COMMAND = '#Start%'.encode()
ONESTEP_COMMAND = '#Onestep%'.encode()

# CCD default integration time
DEFAULT_CCD_INTEGRATION_INTERVAL = 1
DEFAULT_CCD_INTEGRATION_UNIT = 's'

# saving settings
DEFAULT_SAVE_PATH = '~/RamanData/Untitled_Raman_Data'
DEFAULT_FILE_FORMAT = 'JSON'
DEFAULT_FILE_NAME = 'Untitled_Raman_Data'
AUTO_APPEND_CURRENT_TIME = True

# default calibrate parameters
# format: dict({pixel_indices:[...], wavenumber:[...]})
DEFAULT_CALIBRATION_PARAMS = dict(
    {
        "pixel_indices": [358, 469, 500, 624, 749, 1856, 1899, 1936, 1909, 1897, 1873, 1836, 743, 674, 619, 544, 456, 304],
        "wavenumbers": [882, 1049, 1095, 1275, 1453, 2879, 2929, 2973, 2937, 2923, 2870, 2852, 1443, 1346, 1266, 1157, 1027, 801]
    })

CALIBRATION_REGRESSION_MODEL_CHOICES = [
    'B-Spline', 'Polynomial', 'Log', 'User Defined...']
DEFAULT_CALIBRATION_REGRESSION_MODEL = CALIBRATION_REGRESSION_MODEL_CHOICES[0]

# Polynomial model
DEFAULT_POLINOMIAL_ORDER = 3

# B-Spline model
# NOTE: M > K must hold
DEFAULT_B_SPLINE_PARAMS_K = 3
DEFAULT_B_SPLINE_PARAMS_S = 0

USER_DEFINED_MODEL_PATH = ''


# Automatic Peak Detection settings
# The waveform is convolved with wavelet(width) for each width in widths

# wavelet used, default is the ricker wavelet
# AUTO_PEAK_DETECT_WAVELET =

# minimum Signal Noise Ratio for a maximum to be considered a peak
AUTO_PEAK_DETECT_MIN_SNR = 5
AUTO_PEAK_DETECT_WIDTHS_MIN = 1
AUTO_PEAK_DETECT_WIDTHS_MAX = 10

PEAK_MARKS_OVERHANG = 1000



# just some strings
WAVELENGTH_UNIT = 'cm⁻¹'
