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
    Defines a structure for representing directory entry points, containing fields
    for inode number, offset, record length, type, and name.

    Attributes:
        _fields_ (ctypesPyStructSequence): Defined as a list of tuples, where each
            tuple contains the name of a field followed by its data type. The
            fields are: `ino_t`, `off_t`, `d_reclen`, `d_type`, and `d_name`.

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
    Is an extension of the `ctypes.Structure` class and provides attributes for
    representing different types of directory entries. It includes methods for
    setting and retrieving attributes, such as file type, name, and size.

    Attributes:
        DT_UNKNOWN (int): 0.
        DT_FIFO (1bit): 0 or 1, indicating whether the directory entry is a FIFO
            (file-if-one-doesn't-exist).
        DT_CHR (2bit): 0 or 1 indicating whether the directory entry is a character
            special file.
        DT_DIR (4bit): 10 in value, indicating that the directory entry is a directory.
        DT_BLK (6bit): 1 of the 8 possible types of directories represented by
            this struct. It indicates whether the directory is a block device.
        DT_REG (8bit): 14 in the summary.
        DT_LNK (10byte): Used to store the link target for a symbolic link.
        DT_SOCK (12bit): 12-bit binary integer that represents a socket file.
        DT_WHT (14bit): 0 by default, indicating that the file or directory is a
            whiteout.

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
        Sets attributes of a `dirent` object, either by inheriting values from its
        parent `cdirent` object or by setting them to `None`.

        Args:
            cdirent (object): Used to initialize the instance attributes of the
                class using the attribute names and values from an object.

        """
        attributes = [a[0] for a in _cdirent._fields_]
        for a in attributes:
            if cdirent:
                setattr(self, a, getattr(cdirent, a))
            else:
                setattr(self, a, None)

def readdir(directory):
    """
    Recursively reads and returns a list of directory entries in the specified directory.

    Args:
        directory (str): Used to specify the directory to be searched for files
            or subdirectories.

    Returns:
        list: A collection of directory entry objects representing the contents
        of a directory.

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
