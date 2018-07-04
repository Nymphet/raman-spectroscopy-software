import numpy as np
import struct
import time


fake_data_generation_interval = 1


def random_walk(start, length, step_size):
    walks = (np.random.randint(0, 2, length) * 2 -1) * step_size
    return np.array([start + sum(walks[:i]) for i in range(length)])

class FakeSerial():
    last_time = time.time()

    def reset_input_buffer(self):
        pass

    def write(self, bytes_buffer):
        return len(bytes_buffer)

    def read(self, bytes_length):
        self.data_length = bytes_length // 2
        self.fmt = '<{data_length}H'.format(data_length=self.data_length)
        # self.fake_data = np.random.randint(1, 3000, self.data_length)
        self.fake_data = random_walk(15000, self.data_length, 3)
        return struct.pack(self.fmt, *self.fake_data)

    def inWaiting(self):
        self.new_time = time.time()
        if self.new_time - self.last_time > fake_data_generation_interval:
            self.last_time = self.new_time
            return 123
        else:
            return 0
