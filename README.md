# raptor-cots-tools
A tool for manipulating Raptor: Call of the Shadows files.

This tool can be used to extract the files from Raptor archives (.GLB).
It can also view images in .PIC format and palettes in .DAT format and convert them to PNG.

### External dependencies:
  - numpy
  - pillow

### Example Usage:
- extracting files from archive:  
  `./raptor_tools.py archive -i Raptor/data/file0000.glb --extract`
- viewing extracted palette with color blocks as 20x20 :  
  `./raptor_tools.py palette -i Raptor/data/extracted/file0001.glb/PALETTE.DAT --view --scale=20`
- viewing extracted image with non-default palette :  
  `./raptor_tools.py image -i Raptor/data/extracted/file0001.glb/APOGEE.PIC --palette Raptor/data/extracted/file0001.glb/POGPAL.DAT --view`
- convert all extracted images to PNG and write them:
  `./raptor_tools.py image -i Raptor/data/extracted/file0001.glb/ --convert --out Raptor/data/extracted/file0001.glb/pics/`


Thanks to the work done at http://www.shikadi.net/moddingwiki/Raptor for the information about file headers and structure.

