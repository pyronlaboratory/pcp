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
    Defines a structure to represent a directory entry, comprising various fields
    for storing information such as file type, name, and length.

    Attributes:
        _fields_ (ctypesListctypesStructure): A list of field names and data types
            for the structure, including ino_t, off_t, d_reclen, d_type, and d_name.

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
    Provides a way to represent directory entries as structures with various
    attributes such as type, name, and file status. It also allows for initialization
    with either a default value or an existing `cdirent` object.

    Attributes:
        DT_UNKNOWN (int): 0 or 1, representing the file type as unknown or not
            known, respectively.
        DT_FIFO (1bit): 0 by default, indicating that the file is a FIFO (first-in,
            first-out) stream.
        DT_CHR (2bit): 0 or 1, indicating whether the directory entry is a character
            special device.
        DT_DIR (4bit): 0 by default, indicating that the file is a directory.
        DT_BLK (6bit): 1 of the possible values for the `DT` field, indicating
            that the file is a block device.
        DT_REG (8bit): 0 or 1 indicating if the directory entry is a regular file.
        DT_LNK (10bit): Used to represent a symbolic link.
        DT_SOCK (12bit): Used to represent a socket.
        DT_WHT (14bit): 0 by default, indicating that the file is a whiteout.

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
        Sets attributes of a `dirent` object based on those of an input `cdirent`
        object, either by copying values or setting them to `None`.

        Args:
            cdirent (object): Used to store an instance of the class `_CDirent`.

        """
        attributes = [a[0] for a in _cdirent._fields_]
        for a in attributes:
            if cdirent:
                setattr(self, a, getattr(cdirent, a))
            else:
                setattr(self, a, None)

def readdir(directory):
    """
    List directory entries. It opens a directory using the `_opendir` function,
    reads the contents of the directory using the `_readdir` function, and returns
    a list of directory entries using the `dirent` function.

    Args:
        directory (str): A path to a directory or file that represents the location
            from which entries will be read.

    Returns:
        list: A collection of directory entry objects.

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
