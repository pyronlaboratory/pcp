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
    Defines a structure for representing directory entries, including file name,
    inode number, offset within the file, and file type and length.

    Attributes:
        _fields_ (ctypesStructure): A list of fields defined for the structure,
            including field names and data types: `["ino_t", "off_t", "d_reclen",
            "d_type", "d_name"]`.

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
    Defines an object that represents a directory entry, allowing attributes to
    be accessed and modified through its methods.

    Attributes:
        DT_UNKNOWN (int|str): 0 by default, indicating that the file type is unknown
            or not applicable.
        DT_FIFO (int): 1 in the code snippet provided, indicating that the directory
            entry is a FIFO (first-in-first-out) file system.
        DT_CHR (int): 2 in value, indicating that the directory entry is a character
            special file.
        DT_DIR (int): 4, indicating that the file is a directory.
        DT_BLK (Union[int,str]): 6th in the list of possible values for the directory
            entry type.
        DT_REG (int): 8 in value, indicating that the directory entry is a regular
            file.
        DT_LNK (Union[int,str]): 10th in the list of possible values for the `DT`
            field, representing a symbolic link.
        DT_SOCK (int): 12 in value, indicating that the directory entry represents
            a socket file.
        DT_WHT (str|int): 14th in the list of attributes. It represents the file
            type as a whiteout, which can be either a string or an integer value.

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
        Sets attributes to values from either the parent cdirent instance or the
        default value of None if no value is provided.

        Args:
            cdirent (object): Used to initialize instance attributes with values
                from the class dictionary.

        """
        attributes = [a[0] for a in _cdirent._fields_]
        for a in attributes:
            if cdirent:
                setattr(self, a, getattr(cdirent, a))
            else:
                setattr(self, a, None)

def readdir(directory):
    """
    Iteratively reads and returns a list of directories and files in a specified
    directory.

    Args:
        directory (str): A path to a directory for which entries will be read.

    Returns:
        List[str]: A list of file and directory names in a given directory.

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
