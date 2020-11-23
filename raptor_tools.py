#!/usr/bin/env python
import sys
import os
import struct
import argparse

from PIL import Image
import numpy as np

from tools.glb import GLBArchiveFile, GLBArchive
from tools.palette import VGAPalette, RAPTOR_PALETTE
from tools.pic import PICImage

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
        
        for filename, file in glbfile.files.items():
            byte_count = glbfile.files.get(filename).length
            print '{name:>{padding}} {index:> 3} {bytes:>{bytes_padding}} bytes@{offset}'.format(name=file.name, index=file.index, bytes=byte_count, padding=padding, bytes_padding=bytes_padding, offset=file.offset)
            
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
            if files_written > 0:
                print "Wrote {} files to {}.".format(files_written, os.path.dirname(output_path))
            else:
                print "Wrote 0 files."
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
    
    