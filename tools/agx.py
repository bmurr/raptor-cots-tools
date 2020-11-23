import struct
import re
from hashlib import md5
from collections import OrderedDict

import numpy as np
from PIL import Image

from raptor_tools import GLBArchive, GLBArchiveFile
from palette import RAPTOR_PALETTE
from helpers import read_int32, read_int16, read_uint32, read_uint16
   
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

def make_frame(data, image_data, frame_index):
    
    if frame_index == 0:
        data = data[1:]
        image_data = list('\x00' * 64000)    
    image_data = list(image_data)

    offset = 0
    more_blocks = True
    block_index = 0
    while more_blocks:              
        more_blocks = read_uint32(data[offset:])
        dest_index = read_uint16(data[offset+4:])        
        num_bytes = read_uint16(data[offset+6:])        
        src_index = offset + 8    
        src_bytes = data[src_index:src_index+num_bytes]
        image_data[dest_index:dest_index+num_bytes] = src_bytes    

        offset += num_bytes + 8
        block_index += 1

    image_data = ''.join(image_data)
    return image_data

if __name__ == '__main__':
    bytes_to_read = 8

    with open('./data/archives/FILE0001.GLB') as f:
        data = f.read()

    a = GLBArchive.from_data(data)

    frame_data = []
    for name, f in a.files.items():     
        if name.startswith('CHASE'):
            file_data = a.read_file(name)
            # print " ".join("{:02x}".format(ord(c)) for c in file_data[0:0+20])  
            frame_data.append(file_data)
        
    frames = []
    last_frame = None
    for frame_index, data in enumerate(frame_data):   
        frame = make_frame(data, last_frame, frame_index)
        frames.append(frame)
        last_frame = frame

    
    frame_images = [create_image(f, 200, 320, scale=1) for f in frames]    
    default_duration = 1
    deduplicated_frames = OrderedDict()
    
    for i, image in enumerate(frame_images):        
        frame_id = md5(image.tobytes()).hexdigest()
        if deduplicated_frames.get(frame_id):
            frame_info = deduplicated_frames.get(frame_id)
            frame_info[1] += default_duration
            deduplicated_frames[frame_id] = frame_info
        else:
            deduplicated_frames[frame_id] = [image, default_duration]

    
    frame_images = []
    frame_durations = []
    for image, duration in deduplicated_frames.values():
        frame_images.append(image)
        frame_durations.append(duration)
    
    animation = frame_images[0]
    animation.save('./CHASE.gif', 'GIF', save_all=True, append_images=frame_images[1:], optimize=False, duration=frame_durations, loop=0)

   

    