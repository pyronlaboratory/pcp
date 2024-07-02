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
    Defines a structure with two integer members, `val`.

    Attributes:
        _fields_ (ctypesc_int): 2-element array of integers.

    """
    _fields_ = [
        ("val", ctypes.c_int * 2)
]

class _struct_statfs(ctypes.Structure):
    """
    Defines a structure for storing file system statistics, including information
    about files and blocks.

    Attributes:
        _fields_ (ctypesc_long): A list of field names for the struct statfs,
            including f_type, f_bsize, f_blocks, and more.

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
    1/ Calls the `_struct_statfs` function to retrieve file system information.
    2/ Passes the path to be checked to the `_statfs` function.
    3/ Returns the file type based on the information retrieved.

    Args:
        path (str): Used to specify the path to be statfs-ed.

    Returns:
        ctypesbyrefdataf_type: An instance of a struct representing file system
        information, specifically the file type (e.g., regular file, directory, etc.).

    """

    data = _struct_statfs()
    _statfs(path, ctypes.byref(data))
    return data.f_type
