import struct
import re
from hashlib import md5
from collections import OrderedDict, defaultdict
from pprint import pprint


import numpy as np
from PIL import Image

from glb import GLBArchive, GLBArchiveFile
from pic import PICImage
from palette import RAPTOR_PALETTE

class Spriteset(object):

    default_width = 4
    frame_sizes = [32, 64, 128, 256, 512]


    def __init__(self, images):
        self.frames = images

    def save_gif(self, output_path, scale=1):        
        frames = [i.image for i in self.frames]
        frames = [i.resize((i.size[0] * scale, i.size[1] * scale)) for i in frames]
        animation = frames[0]
        animation.save(output_path, 'GIF', save_all=True, append_images=frames[1:], optimize=False, loop=0)

    def to_spritesheet(self, scale=1, size=None):
        if not size:
            height = len(self.frames) / self.default_width if len(self.frames) % self.default_width == 0 else (len(self.frames) / self.default_width ) + 1            
            width = min(self.default_width, len(self.frames))
            size = (width, height)
        else:
            width, height = size
            assert len(self.frames) <= height * width <= len(self.frames) ** 2
        
        frame_sizes = set([f.image.size for f in self.frames])
        assert len(frame_sizes) == 1, "All frames must be of equal dimensions."


        frame_size = list(frame_sizes)[0]
        biggest_frame_dimension = max(frame_size)
        frame_side = [s for s in self.frame_sizes if s > biggest_frame_dimension][0]
        sheet_width, sheet_height = size
        out = np.zeros((sheet_width * frame_side, sheet_height * frame_side, 4), dtype=np.uint8)
        
        i = Image.new('RGBA', (sheet_width * frame_side, sheet_height * frame_side))

        for frame_index, f in enumerate(self.frames):
            frame_location_x = (frame_side / 2) - f.image.size[0] / 2
            frame_location_y = (frame_side / 2) - f.image.size[1] / 2
            frame_location = (frame_location_x + frame_side * (frame_index % self.default_width), frame_location_y + frame_side * (frame_index / self.default_width))            
            i.paste(f.image, frame_location)

        i = i.resize((i.size[0] * scale, i.size[1] * scale))
        return i


        
def create_image(indices, height, width, scale=1, palette=RAPTOR_PALETTE):
    out = np.zeros((height, width, 4), dtype=np.uint8)    
    image_rows = [indices[x:x+width] for x in range(0, len(indices), width)]
    
    for row_index, palette_pixels in enumerate(image_rows):
        pixels = [palette[ord(i)] + [255] for i in palette_pixels]
        out[row_index] = pixels            
    i = Image.fromarray(out, 'RGBA')
    i = i.resize((i.size[0] * scale, i.size[1] * scale)) 
    return i

def show_image(*args, **kwargs):
    i = create_image(*args, **kwargs)
    i.show()

if __name__ == '__main__':
    with open('./data/archives/FILE0001.GLB') as f:
        data = f.read()

    a = GLBArchive.from_data(data)

    spritesets = defaultdict(list)
    
    for filename, f in a.files.items():
        if f.name.endswith('BLK') or f.name.endswith('PIC'):
            file_data = a.read_file(filename)
            spritesets[f.name].append(file_data)
        
    singles = []
    for name, spriteset in spritesets.items():
        if len(spriteset) <= 1:
            singles.append(name)

    for name in singles:
        del spritesets[name]

    for name, frame_datas in spritesets.items():
        frames = [PICImage.from_data(data) for data in frame_datas]        
        spriteset = Spriteset(frames)
        out_path = './sprites/{}.gif'.format(name)
        
        
        spriteset.save_gif('./sprites/gifs/{}.gif'.format(name), scale=3)
        i = spriteset.to_spritesheet()
        i.save('./sprites/sheets/{}_spritesheet.png'.format(name))
    

    

   

    