#!/usr/bin/env python

import sys
import os
import struct
from collections import OrderedDict
import argparse
from PIL import Image
import numpy as np

RAPTOR_PALETTE = [[0, 0, 0], [226, 222, 222], [218, 214, 214], [210, 206, 206], [202, 198, 198], [194, 194, 194], [186, 186, 186], [182, 178, 178], [174, 170, 170], [165, 161, 161], [157, 157, 157], [149, 149, 149], [141, 141, 141], [137, 133, 133], [129, 125, 125], [121, 121, 121], [113, 113, 113], [105, 105, 105], [97, 97, 97], [93, 89, 89], [85, 85, 85], [76, 76, 76], [68, 68, 68], [60, 60, 60], [52, 52, 52], [48, 48, 48], [40, 40, 40], [32, 32, 32], [24, 24, 24], [16, 16, 16], [8, 8, 8], [4, 4, 4], [246, 105, 109], [230, 93, 97], [218, 80, 85], [206, 68, 76], [190, 56, 64], [178, 48, 56], [165, 40, 48], [149, 32, 40], [137, 24, 36], [125, 16, 28], [109, 12, 24], [97, 8, 16], [85, 4, 12], [68, 0, 8], [56, 0, 4], [36, 0, 4], [234, 222, 141], [218, 206, 121], [202, 194, 105], [190, 178, 85], [174, 165, 72], [157, 149, 60], [141, 137, 48], [129, 121, 36], [113, 109, 28], [97, 97, 20], [85, 80, 12], [68, 68, 8], [56, 52, 4], [40, 40, 0], [24, 24, 0], [12, 12, 0], [255, 157, 97], [238, 129, 72], [222, 113, 60], [206, 97, 52], [190, 85, 44], [174, 68, 36], [161, 56, 28], [145, 44, 20], [129, 36, 16], [113, 24, 12], [101, 16, 8], [85, 12, 4], [68, 4, 0], [52, 0, 0], [36, 0, 0], [24, 0, 0], [246, 202, 28], [238, 178, 28], [230, 157, 24], [222, 137, 24], [214, 117, 24], [206, 101, 20], [198, 85, 20], [190, 68, 20], [178, 64, 16], [165, 60, 16], [157, 56, 12], [145, 52, 12], [137, 48, 12], [125, 44, 8], [105, 36, 4], [89, 28, 4], [141, 161, 129], [125, 149, 113], [113, 141, 97], [101, 133, 85], [89, 125, 72], [72, 117, 60], [64, 109, 48], [52, 101, 40], [40, 93, 32], [32, 80, 24], [24, 72, 16], [12, 60, 8], [8, 48, 4], [4, 36, 0], [0, 24, 0], [0, 12, 0], [198, 206, 255], [182, 190, 242], [170, 178, 230], [153, 161, 222], [141, 145, 210], [129, 133, 198], [117, 121, 190], [105, 109, 178], [97, 97, 165], [85, 85, 157], [76, 76, 145], [68, 68, 133], [60, 56, 125], [52, 48, 113], [40, 36, 89], [28, 24, 68], [89, 178, 255], [80, 157, 238], [72, 145, 222], [68, 125, 206], [60, 113, 190], [56, 97, 178], [48, 85, 161], [44, 72, 145], [36, 60, 129], [32, 48, 113], [28, 40, 101], [20, 32, 85], [16, 24, 68], [12, 16, 52], [8, 8, 36], [4, 4, 24], [109, 170, 178], [97, 157, 165], [85, 149, 157], [72, 141, 149], [60, 133, 141], [52, 121, 133], [44, 113, 125], [36, 105, 117], [28, 97, 109], [20, 89, 97], [16, 80, 89], [8, 72, 80], [4, 64, 72], [4, 56, 64], [0, 36, 44], [0, 20, 28], [222, 206, 238], [210, 194, 226], [198, 182, 214], [186, 174, 202], [174, 161, 190], [165, 153, 178], [153, 141, 165], [141, 129, 153], [129, 121, 141], [117, 109, 129], [109, 101, 117], [97, 89, 105], [85, 76, 93], [72, 68, 80], [52, 48, 56], [32, 28, 36], [238, 214, 190], [230, 206, 182], [226, 198, 170], [218, 186, 161], [210, 182, 157], [206, 174, 149], [198, 165, 141], [194, 157, 133], [186, 149, 125], [182, 141, 117], [174, 133, 113], [170, 125, 105], [161, 117, 97], [153, 109, 93], [149, 101, 85], [141, 97, 80], [137, 89, 72], [129, 85, 68], [125, 76, 64], [117, 68, 56], [113, 64, 52], [105, 56, 48], [101, 52, 44], [93, 48, 40], [85, 40, 36], [80, 36, 32], [72, 32, 28], [68, 28, 24], [60, 24, 20], [56, 16, 16], [40, 12, 8], [20, 0, 0], [218, 206, 182], [210, 198, 174], [206, 190, 165], [198, 186, 161], [194, 178, 153], [186, 174, 149], [182, 165, 141], [174, 157, 137], [170, 153, 129], [165, 145, 125], [157, 141, 117], [153, 133, 113], [145, 125, 109], [141, 121, 101], [133, 117, 97], [129, 109, 93], [121, 101, 85], [117, 97, 80], [109, 89, 76], [105, 85, 72], [101, 80, 68], [93, 72, 60], [89, 68, 56], [80, 60, 52], [76, 56, 48], [68, 52, 44], [64, 48, 40], [56, 40, 36], [52, 36, 32], [48, 32, 28], [32, 16, 12], [16, 8, 4], [36, 105, 117], [56, 121, 133], [44, 113, 125], [36, 101, 117], [20, 89, 97], [161, 56, 16], [186, 80, 20], [210, 113, 20], [194, 85, 20], [141, 48, 12], [178, 64, 16], [194, 85, 12], [246, 56, 68], [85, 161, 105], [89, 178, 255], [218, 218, 218]]

class GLBArchiveFile(object):

    def __init__(self, name, encrypted, offset, length):
        self.name = name
        self.encrypted = encrypted
        self.offset= offset
        self.length = length

    def __repr__(self):
        return '<{0.name}:{0.encrypted}:{0.offset}:{0.length}>'.format(self)


class GLBArchive(object):
    FAT_ENTRY_LENGTH = 28

    def __init__(self, data, filelist):
        self.data = data
        self.files = filelist
        self.num_files = len(filelist)

    def read_file(self, filename):        
        file = self.files.get(filename)

        if file is None:
            raise Exception("{}: No such file.".format(filename))            


        file_data = self.data[file.offset:file.offset + file.length]
        if file.encrypted:            
            file_data = self.decrypt(file_data)        
        return file_data

    @classmethod
    def from_data(cls, data):
        header = cls.decrypt(data[:cls.FAT_ENTRY_LENGTH])
        flags, num_files = struct.unpack('<II20x', header)


        filelist = OrderedDict()
        previous_file = None
        for n in range(num_files):
            offset = cls.FAT_ENTRY_LENGTH + n * cls.FAT_ENTRY_LENGTH
            file_header = data[offset:offset + cls.FAT_ENTRY_LENGTH]
            decrypted_file_header = cls.decrypt(file_header)
            flags, offset, length, filename = struct.unpack('<III16s', decrypted_file_header)
            filename = filename.split('\x00', 1)[0]
            if filename and filename not in ['STARTHELP', 'ENDHELP', 'START_SFX', 'END_SFX']:                
                file = GLBArchiveFile(filename, bool(flags), offset, length)                
                if previous_file and previous_file.length == 0:
                    previous_file.length = file.offset - previous_file.offset
                filelist[filename] = file
                previous_file = file

            if previous_file and previous_file.length == 0:
                previous_file.length = len(data) - previous_file.offset

        r = cls(data, filelist)
        return r

        
    @staticmethod
    def decrypt(encrypted_bytes, key='32768GLB'):
        initial_position = 25 % len(key)
        previous_byte_read = ord(key[initial_position])
        position = initial_position

        decrypted_bytes = []
        for c in encrypted_bytes:
            b = ord(c) - ord(key[position])
            position += 1
            if position >= len(key):
                position = 0            
            b -= previous_byte_read
            b = b & 0xFF
            decrypted_bytes.append(chr(b))
            previous_byte_read = ord(c)
        
        return ''.join(decrypted_bytes)

class VGAPalette(object):

    def __init__(self, image, lookup):
        self.image = image;
        self.lookup = lookup

    def save(self, path):
        return self.image.save(path)

    def show(self):
        return self.image.show()

    @staticmethod
    def convert_to_rgb(vga):
        return [(i * 255) / 63 for i in vga]

    @classmethod
    def from_data(cls, data, height=16, scale=10):
        width = 256 / height
        out = struct.unpack('<768c', data)
        out = [ord(c) for c in out]
        out_rgb = cls.convert_to_rgb(out)
    
        out_rgb = np.split(np.array(out_rgb), 256)
        lookup = [a.tolist() for a in out_rgb]

        out_rgb = np.array(out_rgb)
        out_rgb = out_rgb.reshape(height, width, 3, order='A').astype(np.uint8)
        out_rgb = out_rgb.repeat(scale, axis=0).repeat(scale, axis=1)
        i = Image.fromarray(out_rgb, 'RGB')
        return cls(i, lookup)

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

def archive(args):
    archive_name = args.input
    output_directory = args.output

    filepath = os.path.abspath(archive_name)
    if not output_directory:
        output_directory = os.path.dirname(filepath)

    with open(filepath) as f:
        data = f.read()

    glbfile = GLBArchive.from_data(data)
    
    if args.list:
        print "There are {} files in this archive:".format(glbfile.num_files)
        padding = len(sorted(glbfile.files, key=lambda f: len(f))[-1])
        bytes_padding = len(str(sorted(glbfile.files.values(), key=lambda f: len(str(f.length)))[-1].length))
        
        for filename in glbfile.files:
            byte_count = glbfile.files.get(filename).length
            print '{name:>{padding}} {bytes:>{bytes_padding}} bytes'.format(name=filename, bytes=byte_count, padding=padding, bytes_padding=bytes_padding)
            
    elif args.extract:                            
        archive_name = os.path.basename(archive_name)
        output_dir = os.path.join(output_directory, 'extracted', archive_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        for filename in glbfile.files:
            f = glbfile.files.get(filename)
            output_filename = filename.replace('_', '.')
            output_filename = output_filename.replace('/', '_')

            output_path = os.path.join(output_dir, output_filename)        
            with open(output_path, 'wb') as f:
                output_data = glbfile.read_file(filename)
                f.write(output_data)
            
        print "Wrote {} files to {}".format(glbfile.num_files, os.path.dirname(output_path))

                    
def palette(args):
    input_name = args.input
    input_filename = os.path.basename(input_name)
    
    filepath = os.path.abspath(input_name)
    with open(filepath) as f:
        data = f.read()

    i = VGAPalette.from_data(data, scale=args.scale, height=args.height)
    
    if args.view:
        i.show()

    if args.write:
        output_path = args.output
        if not args.output:
            output_path = os.path.join(os.path.dirname(filepath),  '{}.png'.format(input_filename))
        i.save(output_path)
        print "Wrote {}".format(output_path)
            
def image(args):
    input_name = args.input    
    filepath = os.path.abspath(input_name)

    if args.palette:
        palette_path = os.path.abspath(args.palette)
        with open(palette_path) as f:
            data = f.read()

        palette = VGAPalette.from_data(data).lookup
    else:
        palette = RAPTOR_PALETTE

    if os.path.isfile(filepath):
        input_filename = os.path.basename(input_name)
        with open(filepath) as f:
            data = f.read()
        i = PICImage.from_data(data, palette=palette)

        if args.view:
            i.show()
        if args.write:
            output_path = args.output
            if not args.output:
                output_path = os.path.join(os.path.dirname(filepath),  '{}.png'.format(input_filename))
            else:
                if not os.path.basename(output_path):
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    output_path = os.path.join(output_path, '{}.png'.format(input_filename))
                else:    
                    if not output_path.endswith('.png'):
                        output_path = '{}.png'.format(output_path)                
            i.save(output_path)
            print "Wrote {}".format(output_path)
    elif os.path.isdir(filepath):
        if args.convert:
            files_written = 0
            for input_filename in os.listdir(filepath):
                if input_filename.endswith('.PIC') and os.path.isfile(os.path.join(filepath, input_filename)):
                    with open(os.path.join(filepath, input_filename)) as f:
                        data = f.read()
                    i = PICImage.from_data(data, palette=palette)

                    if args.output:
                        output_path = args.output
                        if not os.path.basename(output_path):
                            if not os.path.exists(output_path):
                                os.makedirs(output_path)
                            output_path = os.path.join(output_path, '{}.png'.format(input_filename))
                        else:
                            exit("Output path must be a directory with --convert option")
                    else:
                        output_path = os.path.join(filepath, '{}.png'.format(input_filename))

                    i.save(output_path)
                    print "Converting {}".format(input_filename)
                    files_written += 1
            print "Wrote {} files to {}.".format(files_written, os.path.dirname(output_path))
        else:
            exit("Input path is directory but --convert argument was not provided.")
    else:
        exit("Input file does not exist.")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(    
        description='''Tools for manipulating Raptor: Call of the Shadows files.''',
        epilog='''Run %(prog)s [ACTION] -h to see flags for a specific option.''')
        
    subparsers = parser.add_subparsers(title='Actions')
    
    parser_archive = subparsers.add_parser('archive', help="Input is an archive file. (.GLB)")    
    parser_archive.add_argument('-input', help="Path to file.", action='store', required=True)
    archive_actions = parser_archive.add_mutually_exclusive_group(required=True)
    archive_actions.add_argument('--extract',action='store_true', help="Extract the files in an archive. Uses 'extracted/ARCHIVE_NAME' if not specified.")
    archive_actions.add_argument('--list',action='store_true', help="List the files in an archive.")    
    parser_archive.add_argument('--output',action='store', help="Directory to extract files to.")
    parser_archive.set_defaults(func=archive)

    parser_palette = subparsers.add_parser('palette', help="Input is a 768-byte VGA palette file (.DAT).")
    parser_palette.add_argument('-input', help="Path to file.", action='store', required=True)
    palette_actions = parser_palette.add_mutually_exclusive_group(required=True)
    palette_actions.add_argument('--view',action='store_true', help="View the palette.")
    palette_actions.add_argument('--write',action='store_true', help="Write the palette to OUT file as PNG.")    
    parser_palette.add_argument('--output',action='store', help="File to write to.")
    parser_palette.add_argument('--scale',action='store', help="Scaling factor.", default=10, type=int)
    parser_palette.add_argument('--height',action='store', help="Height of output image. This must be a factor of 256.", default=16, type=int)
    parser_palette.set_defaults(func=palette)

    parser_image = subparsers.add_parser('image', help="Input is an image file (.PIC) or a directory.")
    parser_image.add_argument('-input', help="Path to file or directory.", action='store', required=True)
    image_actions = parser_image.add_mutually_exclusive_group(required=True)
    image_actions.add_argument('--view',action='store_true', help="View the image. Uses values from PALETTE.DAT if palette is not specified.")
    image_actions.add_argument('--write',action='store_true', help="Write the image to OUT file as PNG.")    
    image_actions.add_argument('--convert',action='store_true', help="Convert all PIC images in a directory using specified palette. Creates 'images' subdirectory if OUT not specified.")
    parser_image.add_argument('--output',action='store', help="Output file or directory.")
    parser_image.add_argument('--palette',action='store', help="Path to palette file to use.")
    parser_image.set_defaults(func=image)
    
    args = parser.parse_args()
    args.func(args)
    
    