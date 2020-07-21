import struct
import numpy as np

import raman_configs

# the following function parses bytes array received from CCD VCP into tuple
# of 3694 unsigned ints.


def parse_CCD_output(bytes_buffer):
    # check the length of the buffer
    assert len(bytes_buffer) == raman_configs.PIXELS_WIDTH * 2, "Illegal buffer size."
    # formatting : little endian, total length 3694 (PIXELS_WIDTH), unsigned short
    fmt = '<{PIXELS_WIDTH}H'.format(PIXELS_WIDTH=raman_configs.PIXELS_WIDTH)
    # formatting : big endian, total length 3694 (PIXELS_WIDTH), unsigned short
    # fmt = '>{PIXELS_WIDTH}H'.format(PIXELS_WIDTH=raman_configs.PIXELS_WIDTH)
    return struct.unpack(fmt, bytes_buffer)


def to_set_integration_time_command(interval=1, unit='s'):
    #assert unit in ['s', 'ms'], "Illegal time unit"
    if unit == 's':
        return '#IT:{interval:0>3}ss%'.format(interval=interval).encode()
    elif unit == 'ms':
        return '#IT:{interval:0>3}ms%'.format(interval=interval).encode()
    else:
        return ''.encode()


def read_data(ser):
    bytes_buffer = ser.read(raman_configs.PIXELS_WIDTH * 2)
    intensities = np.array(parse_CCD_output(bytes_buffer))
    return intensities
