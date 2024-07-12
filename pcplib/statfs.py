#Copyright Genome Research Ltd 2014
# Author gmpc@sanger.ac.uk
# This program is released under the GNU Public License V2 or later (GPLV2+)

import ctypes
"""
This module provides python bindings for statfs.
"""

# C data structures
class _fsid(ctypes.Structure):
    """
    Defines a structure with two `ctypes.c_int` members, which likely represent a
    file system identifier for use in low-level system interactions.

    Attributes:
        _fields_ (ctypesStructure): 2-element list of `ctypes.c_int`.

    """
    _fields_ = [
        ("val", ctypes.c_int * 2)
]

class _struct_statfs(ctypes.Structure):
    """
    Defines a structure for representing file system information, including type,
    block size, blocks, available blocks, free space, files, and various flags.

    Attributes:
        _fields_ (ctypesStructure): A list of fields that make up the `struct
            statfs`. The list includes field names, data types, and sizes.

    """
    _fields_ = [
    ('f_type', ctypes.c_long),
    ('f_bsize', ctypes.c_long),
    ('f_blocks', ctypes.c_ulong),
    ('f_bfree', ctypes.c_ulong),
    ('f_bavail', ctypes.c_ulong),
    ('f_files', ctypes.c_ulong),
    ('f_ffree', ctypes.c_ulong),
    ('f_fsid', _fsid),
    ('f_namelen', ctypes.c_long),
    ('f_frsize', ctypes.c_long),
    ('f_flags', ctypes.c_long),
    ('f_spare', ctypes.c_long * 4)
]


_clib = ctypes.CDLL("libc.so.6", use_errno=True)
_struct_statfs_p = ctypes.POINTER(_struct_statfs)
_statfs = _clib.statfs
_statfs.argtypes = [ctypes.c_char_p, _struct_statfs_p]


def fstype(path):
    """
    Calculates the file system type of a path based on the struct statfs data
    returned by `_statfs`.

    Args:
        path (ctypesbyrefobject): Required to pass the path of a file system to
            be analyzed for its type.

    Returns:
        ctypesc_ushort: A 16-bit unsigned integer that represents the file system
        type of a given path.

    """

    data = _struct_statfs()
    _statfs(path, ctypes.byref(data))
    return data.f_type
