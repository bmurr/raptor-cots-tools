import struct
import numpy as np
from PIL import Image
import sys
import math
import os
from collections import OrderedDict

from .palette import RAPTOR_PALETTE


class RaptorTileset(object):

    def __init__(self, tiles):
        self.tiles = tiles
    
    @classmethod
    def from_data(cls, data):        
        TILE_SIZE = 0x414
        tile_bytes = [data[i:i+TILE_SIZE] for i in range(0, len(data), TILE_SIZE)]

        tiles = []
        for data in tile_bytes:
            tile_fields = struct.unpack('IIIII{}s'.format(len(data) - 5 * 4), data)
            tiles.append(RaptorTile(*tile_fields))

        return cls(tiles)

class RaptorTile(object):

    def __init__(self, u1, u2, u3, height, width, palette_pixels):
        self.palette_pixels = palette_pixels

class RaptorTileInfo(object):

    def __init__(self, tile_index, tileset_index):
        self.tile_index = tile_index
        self.tileset_index = tileset_index

class RaptorMap(object):

    height = 150
    width = 9
    tile_side = 32

    def __init__(self, tile_infos, actors):
        self.tile_infos = tile_infos
        self.actors = actors

    def to_image(self, tileset, scale=1):
        out = np.zeros((self.height * self.tile_side, self.width * self.tile_side, 4), dtype=np.uint8)

        for y in range(0, self.height * self.tile_side, self.tile_side):
            for x in range(0, self.width * self.tile_side, self.tile_side):
                tile_index = self.tile_infos[(y / 32 * self.width) + x / 32].tile_index
                tile = tileset.tiles[tile_index]
                tile_pixels = [RAPTOR_PALETTE[ord(i)] + [255] for i in tile.palette_pixels]
                
                
                shaped_tile_data = np.array(tile_pixels).reshape(self.tile_side, self.tile_side, 4)
                out[y:y+self.tile_side, x:x+self.tile_side] = shaped_tile_data
        
        i = Image.fromarray(out, 'RGBA')
        return i


    @classmethod
    def from_data(cls, data):

        file_size, actor_offset, actor_count = struct.unpack('<III{}x'.format(len(data) - 4*3), data)
        header_size = 3 * 4
        tile_data_size = actor_offset - header_size
        actor_data_size = file_size - actor_offset
        file_size, actor_offset, actor_count, tile_data, actor_data = struct.unpack('<III{}s{}s'.format(tile_data_size, actor_data_size), data)

        tile_size = 4
        tiles = [tile_data[i:i+tile_size] for i in range(0, len(tile_data), tile_size)]
        tiles = [struct.unpack('hh', t) for t in tiles]
        tiles = [RaptorTileInfo(*t) for t in tiles]
        actors = []

        return cls(tiles, actors)
        
    

if __name__ == '__main__':
    with open('./data/FILE0001.GLB/STARTG1TILES') as f:
        data = f.read()
        tileset = RaptorTileset.from_data(data)

    with open('./data/FILE0001.GLB/map/MAP1G1.MAP') as f:
        data = f.read()

    raptor_map = RaptorMap.from_data(data)
    map_image = raptor_map.to_image(tileset, scale=4)
    map_image.show()
    
    
    