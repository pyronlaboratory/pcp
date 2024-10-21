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
    Represents a file system identifier as a 2-element integer array, where each
    element is a part of the file system ID. The `val` field is a ctypes array of
    two integers.

    Attributes:
        _fields_ (List[Dict[str,Union[ctypesStructure,ctypesc_int]]]): Specifying
            the structure of the class with a list of dictionaries, where each
            dictionary contains information about a field in the class.

    """
    _fields_ = [
        ("val", ctypes.c_int * 2)
]

class _struct_statfs(ctypes.Structure):
    """
    Defines a data structure to represent file system statistics, containing fields
    for file system type, block size, available blocks and inodes, and other file
    system metadata.

    Attributes:
        _fields_ (List[ctypesStructField]): Defined to contain a list of fields
            that make up the `statfs` structure. Each field is represented by a
            `ctypes.StructField` object, which contains information about the
            field's name, type, and offset within the structure.

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
    Returns the file system type of the file system containing the specified `path`.
    It uses the `_statfs` function to retrieve file system statistics and the
    `_struct_statfs` function to define the data structure for these statistics.

    Args:
        path (str): Designated a file system path.

    Returns:
        ctypesc_int32: The file system type of the file system containing the
        specified path.

    """

    data = _struct_statfs()
    _statfs(path, ctypes.byref(data))
    return data.f_type
