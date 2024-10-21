#Copyright Genome Research Ltd 2014
# Author gmpc@sanger.ac.uk
# This program is released under the GNU Public License V2 or later (GPLV2+)

import ctypes
import os
"""
This module provides a python interface to the readdir
system call.
"""

# Ctypes boilerplate for readdir/opendir/closedir
_clib = ctypes.CDLL("libc.so.6", use_errno=True)

class _cdirent(ctypes.Structure):
    """
    Represents a directory entry, a structure used in C to describe a file or
    directory in a directory. It contains fields for inode number, offset, record
    length, file type, and file name, allowing for manipulation and inspection of
    directory entries.

    Attributes:
        _fields_ (List[Dict[str,Union[ctypesStructure,ctypes_SimpleCData]]]):
            Define. It is a list of dictionaries where each dictionary represents
            a field of the struct. Each field is defined by a name and a type,
            which can be either a ctypes structure or a simple ctypes data type.

    """
    _fields_ = [
        ("ino_t", ctypes.c_ulong),
        ("off_t", ctypes.c_ulong),
        ("d_reclen", ctypes.c_short),
        ("d_type",  ctypes.c_ubyte),
        ("d_name", ctypes.c_char * 4000)
]

class _c_dir(ctypes.Structure):
    pass

_dirent_p = ctypes.POINTER(_cdirent)
_c_dir_p = ctypes.POINTER(_c_dir)
_opendir = _clib.opendir
_opendir.argtypes = [ctypes.c_char_p]
_opendir.restype = _c_dir_p
_closedir = _clib.closedir
_closedir.argtypes = [_c_dir_p]
_closedir.restype = ctypes.c_int
_readdir = _clib.readdir
_readdir.argtypes = [_c_dir_p]
_readdir.restype = _dirent_p


class dirent(ctypes.Structure):
    """
    Represents a directory entry. It is based on a `ctypes.Structure` and inherits
    its fields. The class can be initialized with or without a `cdirent` object,
    and it sets the attributes of the `cdirent` object to the corresponding fields
    in the class.

    Attributes:
        DT_UNKNOWN (int): Defined as a constant with a value of 0. It represents
            an unknown file type in a directory.
        DT_FIFO (int): Defined as 1. It represents a file type, specifically a
            first-in-first-out (FIFO) file in Unix-like file systems.
        DT_CHR (int): Represented by the value 2, indicating that the file is a
            character device.
        DT_DIR (int): Equal to 4. It represents a directory in the file system,
            indicating that the file is a directory.
        DT_BLK (int): Assigned the value 6. It is used to represent a block device,
            such as a hard drive or flash drive, in the directory structure.
        DT_REG (int): Defined as 8. It represents a regular file type in the file
            system, indicating a file that is not a directory, symbolic link, or
            special file.
        DT_LNK (int): Defined as 10. It represents a symbolic link.
        DT_SOCK (int): Defined as 12. It represents a socket in the file system,
            indicating that a file is a socket.
        DT_WHT (int): Defined as 14. It represents a whiteout file type, which is
            a file type in some file systems that marks a directory entry as deleted.

    """
    DT_UNKNOWN = 0
    DT_FIFO    = 1
    DT_CHR     = 2
    DT_DIR     = 4
    DT_BLK     = 6
    DT_REG     = 8
    DT_LNK     = 10
    DT_SOCK    = 12
    DT_WHT     = 14

    def __init__(self, cdirent=None):
        """
        Copies attributes from the cdirent object to the current object, if cdirent
        is not None. If cdirent is None, it sets all attributes to None. The
        attributes are extracted from the _fields_ attribute of the cdirent object,
        which is assumed to be a ctypes.Structure.

        Args:
            cdirent (Any): Used to initialize the object's attributes with values
                from an existing `_cdirent` object, if provided.

        """
        attributes = [a[0] for a in _cdirent._fields_]
        for a in attributes:
            if cdirent:
                setattr(self, a, getattr(cdirent, a))
            else:
                setattr(self, a, None)

def readdir(directory):
    """
    Lists the contents of a specified directory. It opens the directory, reads its
    entries one by one, and stores them in a list, which is then returned.

    Args:
        directory (str): Used to specify the path of the directory to be read.

    Returns:
        List[dirent]: A list of directory entries. Each entry is a `dirent` object,
        containing information about a file or directory in the specified directory.

    """
    entries = []
    dirp = _opendir(directory)
    if not bool(dirp):
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    else:
        while True:
            p = _readdir(dirp)
            if not p:
                break
            d = dirent(p.contents)
            entries.append(d)
    _closedir(dirp)
    return (entries)
