import os, struct, builtins
import numpy as np

#
# A simple reader for MNIST files
#

def open(filename):
    return MnistFile(filename, 'rb')

class MnistFile:
    def __init__(self, filename, mode):
        self.file = builtins.open(filename, mode)
        # first 8 bytes are a magic number that tells us file type
        # and the number of samples
        self.magic, self.length = struct.unpack('>II', self.file.read(8))
        if self.magic == 2051:
            self.filetype = 'images'
            self.rows, self.columns = struct.unpack('>II', self.file.read(8))
            self.byte_depth = self.rows * self.columns # do I need int() here?
            self.read_params = {'format': '{:0}B'.format(self.byte_depth), 'byte depth': self.byte_depth}
        elif self.magic == 2049:
            self.filetype = 'labels'
            self.read_params = {'format': 'B', 'byte depth': 1}
        else:
            raise IOError('Unknown MNIST file type')
    
    
    @property
    def data_shape(self):
        if self.filetype == 'images':
            return (self.length, self.rows, self.columns)
        elif self.filetype == 'labels':
            return (self.length, )
    
    @property
    def samples(self):
        while True:
            data = self.file.read(self.read_params['byte depth'])
            if data:
                sample = np.array(struct.unpack(self.read_params['format'], data))
                if self.filetype == 'images':
                    sample = np.array(sample).reshape((self.rows, self.columns))
                yield sample
            else:
                self.close() # extra context management at EOF in case with() is not used
                break
    
    def close(self):
        self.file.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self):
        self.close()
