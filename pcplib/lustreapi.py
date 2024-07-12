# Copyright (c) Genome Research Ltd 2012
# Author Guy Coates <gmpc@sanger.ac.uk>
# This program is released under the GNU Public License V2 (GPLv2)

"""
Python bindings to minimal subset of lustre api.
This module requires a dynamically linked version of the lustre
client library (liblustreapi.so). 

Older version of the lustre client only ships a static library (liblustreapi.a).
setup.py should have generated a dynamic version during installation.

You can generate the dynamic library by hand by doing the following:

ar -x liblustreapi.a
gcc -shared -o liblustreapi.so *.o

"""
import ctypes
import ctypes.util
import os
import select
import sys


import pkg_resources
try:
    __version__ = pkg_resources.require("pcp")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = "UNRELEASED"

LUSTREMAGIC = 0xbd00bd0

liblocation = ctypes.util.find_library("lustreapi")
# See if liblustreapi.so is in the same directory as the module
if not liblocation:
    modlocation, module = os.path.split(__file__)
    liblocation = os.path.join(modlocation, "liblustreapi.so")

lustre = ctypes.CDLL(liblocation, use_errno=True)

# ctype boilerplate for C data structures and functions
class lov_user_ost_data_v1(ctypes.Structure):
    """
    Represents user object data, including ID, group ID, generation number, and
    index for an unspecified purpose.

    Attributes:
        _fields_ (ctypesStructure): An array of field names for the structure.

    """
    _fields_ = [
        ("l_object_id", ctypes.c_ulonglong),
        ("l_object_gr", ctypes.c_ulonglong),
        ("l_ost_gen", ctypes.c_uint),
        ("l_ost_idx", ctypes.c_uint)
        ]
class lov_user_md_v1(ctypes.Structure):
    """
    Defines a struct for storing metadata related to user data, including magic
    number, pattern ID, object ID, and other information necessary for efficient
    storage and retrieval.

    Attributes:
        _fields_ (ctypesStructure): A list of field names for the structure,
            including "lmm_magic", "lmm_pattern", "lmm_object_id", and others.

    """
    _fields_ = [
        ("lmm_magic", ctypes.c_uint),
        ("lmm_pattern", ctypes.c_uint),
        ("lmm_object_id", ctypes.c_ulonglong),
        ("lmm_object_gr", ctypes.c_ulonglong),
        ("lmm_stripe_size", ctypes.c_uint),
        ("lmm_stripe_count",  ctypes.c_short),
        ("lmm_stripe_offset", ctypes.c_short),
        ("lmm_objects", lov_user_ost_data_v1 * 2000 ),
        ]
lov_user_md_v1_p = ctypes.POINTER(lov_user_md_v1)
lustre.llapi_file_get_stripe.argtypes = [ctypes.c_char_p, lov_user_md_v1_p]
lustre.llapi_file_open.argtypes = [ctypes.c_char_p, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_ulong, ctypes.c_int,
                                   ctypes.c_int, ctypes.c_int]

class stripeObj:
    """
    Manages stripe-related data and provides methods to access or manipulate that
    data, including counting the number of stripes, calculating their size, and
    checking if a given element is striped.

    Attributes:
        lovdata (lov_user_md_v1): Used to store user metadata for stripes.
        stripecount (int): 1-based, indicating the number of stripes found in the
            object.
        stripesize (int): 0 by default, representing the size of a stripe segment.
        stripeoffset (int): Used to represent the offset of a stripe within a
            larger dataset.
        ostobjects (List[ObjectStriped]): A list of objects that are associated
            with the current stripe.

    """
    def __str__(self):
        """
        Generates a string representation of an object by concatenating various
        attributes, including Stripe Count, Size, Offset, and information about OstObjects.

        Returns:
            str: A string containing various information about the object's stripes,
            offsets, and objects.

        """
        string = "Stripe Count: %i Stripe Size: %i Stripe Offset: %i\n" \
                 % (self.stripecount, self.stripesize, self.stripeoffset)
        for ost in self.ostobjects:
            string += ("Objidx:\t %i \tObjid:\t %i\n" % (ost.l_ost_idx,
                                                         ost.l_object_id))
        return(string)
        
    def __init__(self):
        """
        Sets up instance variables for lovdata, stripecount, stripesize, stripeoffset,
        and ostobjects.

        """
        self.lovdata = lov_user_md_v1()
        self.stripecount = -1
        self.stripesize = 0
        self.stripeoffset = -1
        self.ostobjects = []



    def isstriped(self):
        """
        Determines if the number of stripes in an object is greater than 1 or equal
        to -1, returning True if so and False otherwise.

        Returns:
            bool: True when the stripe count is greater than 1 or equal to -1, and
            False otherwise.

        """
        if self.stripecount > 1 or self.stripecount == -1:
            return(True)
        else:
            return(False)
    
    
def getstripe(filename):
    """
    Retrieves the stripe information for a file and populates an instance of the
    `stripeobj` class with the retrieved data.

    Args:
        filename (str): Used to specify the path to a file for which the stripes
            are to be extracted.

    Returns:
        stripeobj: A class that contains information about a file's stripes,
        including the count, size, and offset.

    """
    stripeobj = stripeObj()
    lovdata = lov_user_md_v1()
    stripeobj.lovdata = lovdata
    err = lustre.llapi_file_get_stripe(filename, ctypes.byref(lovdata))

    # err 61 is due to  LU-541 (see below)
    if err < 0 and err != -61:
        err = 0 - err
        raise IOError(err, os.strerror(err))

    # workaround for Whamcloud LU-541
    # use the filesystem defaults if no properties set
    if err == -61  :
        stripeobj.stripecount = 0
        stripeobj.stripesize = 0
        stripeobj.stripeoffset = -1

    else:
        for i in range(0, lovdata.lmm_stripe_count):
            stripeobj.ostobjects.append(lovdata.lmm_objects[i])

        stripeobj.stripecount = lovdata.lmm_stripe_count
        stripeobj.stripesize = lovdata.lmm_stripe_size
        # lmm_stripe_offset seems to be reported as 0, which is wrong
        if len(stripeobj.ostobjects) > 0:
            stripeobj.stripeoffset = stripeobj.ostobjects[0].l_ost_idx
        else:
            stripeobj.stripeoffset = -1
    return(stripeobj)

def setstripe(filename, stripeobj=None, stripesize=0, stripeoffset=-1,
              stripecount=1):
    """
    Modifies the stripes of a file using the Lustre library, taking into account
    various parameters such as filename, stripe object, size, offset, and count.

    Args:
        filename (str): Used to specify the name of the file to be stripped with
            Lustre.
        stripeobj (object|NoneType): Used to store the stripe object information
            for the file being created or modified, including its size, offset,
            and count.
        stripesize (int): Used to specify the size of each stripe in bytes.
        stripeoffset (int|1): Used to specify the starting offset of the stripes
            in the file.
        stripecount (int): 1 by default, indicating that only one stripe will be
            created for the given file.

    Returns:
        int: 0 when the file is opened successfully, and a negative error code
        when there is an error.

    """
    flags = os.O_CREAT
    mode = 0700
    # only stripe_pattern 0 is supported by lustre.
    stripe_pattern = 0

    if stripeobj:
        stripesize = stripeobj.stripesize
        stripeoffset = stripeobj.stripeoffset
        stripecount = stripeobj.stripecount


    # Capture the lustre error messages, These get printed to stderr via 
    # liblusteapi, and so we need to intercept them.

    message = captureStderr()

    fd = lustre.llapi_file_open(filename, flags, mode, stripesize,
                                stripeoffset, stripecount, stripe_pattern)
    message.readData()
    message.stopCapture()

    if fd < 0:
        err = 0 - fd
        raise IOError(err, os.strerror(err))
    else:
        os.close(fd)
        return(0)


class captureStderr():
    """
    Captures the standard error output of a process and returns it as a string,
    allowing the contents to be read line by line.

    Attributes:
        pipeout (int): Used to read data from a pipe.
        pipein (int|str): A file descriptor that points to the reading end of a
            pipe used for capturing stderr output.
        oldstderr (int|str): Used to restore the original stderr file descriptor
            after capturing the stderr output.
        contents (str): A buffer for storing the captured stderr content during
            the process execution.

    """
    def __init__(self):
        """
        Creates two pipes, one for input and one for output, and redirects stderr
        to the output pipe using dup2.

        """
        self.pipeout, self.pipein = os.pipe()
        self.oldstderr = os.dup(2)
        os.dup2(self.pipein, 2)
        self.contents=""

    def __str__(self):
        return (self.contents)

    def readData(self):
        """
        Reads data from the pipe output by os.read(self.pipeout, 1024) until
        self.checkData() is False.

        """
        while self.checkData():
            self.contents += os.read(self.pipeout, 1024)
            
    def checkData(self):
        """
        Class checks if any data is available in the pipeout variable by calling
        the `select` function and returns a boolean value indicating whether any
        data is present.

        Returns:
            bool: 1 if there are any items in the list `self.pipeout`, and 0 otherwise.

        """
        r, _, _ = select.select([self.pipeout], [], [], 0)
        return bool(r)

    def stopCapture(self):
        """
        Closes pipeout and oldstderr, duplicating stderr to 2 for further use

        """
        os.dup2(self.oldstderr, 2)
        os.close(self.pipeout)
        os.close(self.pipein)
