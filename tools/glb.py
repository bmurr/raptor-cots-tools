from collections import OrderedDict, Counter
import struct

class GLBArchiveFile(object):

    def __init__(self, name, encrypted, offset, length, index):
        self.name = name
        self.index = index
        self.encrypted = encrypted
        self.offset= offset
        self.length = length

    def __repr__(self):
        return '<{0.name}-{0.index}:{0.encrypted}:{0.offset}:{0.length}>'.format(self)

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
        filename_counter = Counter()
        previous_file = None
        for n in range(num_files):
            offset = cls.FAT_ENTRY_LENGTH + n * cls.FAT_ENTRY_LENGTH
            file_header = data[offset:offset + cls.FAT_ENTRY_LENGTH]
            decrypted_file_header = cls.decrypt(file_header)
            flags, offset, length, filename = struct.unpack('<III16s', decrypted_file_header)
            filename = filename.split('\x00', 1)[0]
            if filename and filename not in ['STARTHELP', 'ENDHELP', 'START_SFX', 'END_SFX']:                
                file = GLBArchiveFile(filename, bool(flags), offset, length, filename_counter[filename])                
                if previous_file and previous_file.length == 0:
                    previous_file.length = file.offset - previous_file.offset
                if filename_counter[filename] == 0:
                    filelist[filename] = file
                else:
                    if filelist.get(filename):
                        if '_' in filename:
                            base_filename, ext = filename.rsplit('_', 1)
                            frame_filename = '_'.join(["{}-{}".format(base_filename, 0), ext])
                        else:
                            frame_filename = "{}-{}".format(filename, 0)
                        filelist[frame_filename] = filelist.get(filename)
                        del(filelist[filename])
                    count = filename_counter[filename]
                    if '_' in filename:
                        base_filename, ext = filename.rsplit('_', 1)
                        frame_filename = '_'.join(["{}-{}".format(base_filename, count), ext])
                    else:
                        frame_filename = "{}-{}".format(filename, count)
                    filelist[frame_filename] = file
                filename_counter[filename] += 1
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
