import struct

from PIL import Image
import numpy as np

from palette import RAPTOR_PALETTE

class PICImage(object):

    def __init__(self, image):
        self.image = image

    def save(self, path):
        return self.image.save(path)

    def show(self):
        return self.image.show()

    @staticmethod
    def read_block_data(remaining):
        image_rows = []

        while True:    
            block_x, block_y, linear_offset, count = struct.unpack('<IIII{}x'.format(len(remaining) - 4 * 4), remaining)          
            if count == 0xFFFFFFFF and linear_offset == 0xFFFFFFFF:
                break

            block_x, block_y, linear_offset, count, pixels, remaining = struct.unpack('<IIII{}s{}s'.format(count, len(remaining) - (4 * 4) - (count)), remaining)
            image_rows.append((block_x, block_y, linear_offset, count, pixels))

        return image_rows

    @classmethod
    def from_data(cls, data, palette=RAPTOR_PALETTE):
        byte_count = len(data)

        u1, u2, transparent_line_count, width, height, remaining = struct.unpack('<IIIII{}s'.format(byte_count - 5 * 4), data)
    
        assert height <= 2048, "Got a height of {}, which is too large.".format(height)
        assert width <= 2048, "Got a width of {}, which is too large.".format(width)

        out = np.zeros((height, width, 4), dtype=np.uint8)

        if transparent_line_count == 0:
            image_rows = [remaining[x:x+width] for x in range(0, len(remaining), width)]
            for row_index, palette_pixels in enumerate(image_rows):
                pixels = [palette[ord(i)] + [255] for i in palette_pixels]
                out[row_index] = pixels            
        else:
            image_rows = cls.read_block_data(remaining)        
            for r in image_rows:
                block_x, block_y, linear_offset, count, palette_pixels = r
                pixels = [palette[ord(i)] + [255] for i in palette_pixels]        
                out[block_y][block_x:block_x + len(pixels)] = pixels

        i = Image.fromarray(out, 'RGBA')
        return cls(i)
