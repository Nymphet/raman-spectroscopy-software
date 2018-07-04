# testing mod
IS_TESTING = True

# Width of CCD pixels
PIXELS_WIDTH = 3694

# Serial port settings
DEFAULT_SERIAL_PORT = '/dev/tty.usbserial-A505LIEG'
DEFAULT_BAUD_RATE = 921600

# protocols
STOP_COMMAND = '#Stop%'.encode()
START_COMMAND = '#Start%'.encode()
ONESTEP_COMMAND = '#Onestep%'.encode()

# CCD default integration time
DEFAULT_CCD_INTEGRATION_INTERVAL = 1
DEFAULT_CCD_INTEGRATION_UNIT = 's'

# saving settings
DEFAULT_SAVE_PATH = '../Untitled_Raman_Data'
DEFAULT_FILE_FORMAT = 'JSON'
DEFAULT_FILE_NAME = 'Untitled_Raman_Data'
AUTO_APPEND_CURRENT_TIME = True

# default calibrate parameters
# format: dict({pixel_indices:[...], wavenumber:[...]})
DEFAULT_CALIBRATION_PARAMS = dict(
    {
        "pixel_indices": [10, 400, 700, 900, 2000, 3000, 3200],
        "wavenumbers": [20, 810, 1390, 1820, 3980, 6010, 6400]
    })

CALIBRATION_REGRESSION_MODEL_CHOICES = [
    'B-Spline', 'Polynomial-2', 'Polynomial-3', 'Linear', 'Do Nothing', 'User Defined']
DEFAULT_CALIBRATION_REGRESSION_MODEL = CALIBRATION_REGRESSION_MODEL_CHOICES[0]

# Polynomial model
DEFAULT_POLINOMIAL_ORDER = 3

# B-Spline model
# NOTE: M > K must hold
DEFAULT_B_SPLINE_PARAMS_K = 3
DEFAULT_B_SPLINE_PARAMS_S = 0


# Define your model here.
# The model must accept two parameters: numpy array of pixel_indices and wavenumbers
# The model must return a single function that 
#   accepts a numpy array as input and returns a numpy array with the same length
USER_DEFINED_MODEL = lambda pixel_indices, wavenumbers: (lambda x: x)

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



# Sampling Noise and Signal by Averaging and Substraction
DEFAULT_NOISE_SAMPLE_SIZE = 100
DEFAULT_SIGNAL_SAMPLE_SIZE = 100
DEFAULT_SAMPLE_INTERVAL_IN_SECONDS = 5
