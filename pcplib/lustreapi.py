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
    Defines a data structure to store user-defined OST (Object Storage Target)
    data, likely in a Lustre file system, containing object ID, group ID, generation
    number, and index.

    Attributes:
        _fields_ (List[Union[str,ctypesStructure]]): Specify the structure of the
            class.

    """
    _fields_ = [
        ("l_object_id", ctypes.c_ulonglong),
        ("l_object_gr", ctypes.c_ulonglong),
        ("l_ost_gen", ctypes.c_uint),
        ("l_ost_idx", ctypes.c_uint)
        ]
class lov_user_md_v1(ctypes.Structure):
    """
    Represents a data structure for a Lustre file system metadata version 1. It
    contains fields for storing metadata, such as object ID, stripe size, and
    count, as well as an array to store object data.

    Attributes:
        _fields_ (List[Union[str,ctypesStructure,ctypesArray]]): Defines a list
            of fields that make up the structure. Each field is represented by a
            tuple containing the field name and its corresponding ctypes type.

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
    Represents a striped storage object, containing metadata such as stripe count,
    size, and offset. It also stores a list of OST (Object Storage Target) objects,
    which are associated with the striped object.

    Attributes:
        lovdata (lov_user_md_v1): Initialized in the `__init__` method, suggesting
            that it is a data object related to LOV (List of Values) data, possibly
            used for configuration or metadata purposes.
        stripecount (int): Initialized with a value of -1 in the `__init__` method.
            It represents the number of stripes in a striped data layout.
        stripesize (int): Initialized to 0 in the `__init__` method. It represents
            the size of a stripe.
        stripeoffset (int): Initialized to -1 in the `__init__` method. It is used
            to store the stripe offset, a value that likely represents the starting
            position of a stripe in a larger data structure.
        ostobjects (List[object]): Initialized as an empty list in the `__init__`
            method. It appears to store objects of class type `ostobjects` with
            attributes `l_ost_idx` and `l_object_id`.

    """
    def __str__(self):
        """
        Converts the object's attributes into a formatted string for representation.
        It includes stripe-related information and details about the OST objects
        associated with the stripe.

        Returns:
            str: A formatted string containing information about the object,
            including stripe count, stripe size, stripe offset, and details of its
            OST objects, formatted in a tabular layout.

        """
        string = "Stripe Count: %i Stripe Size: %i Stripe Offset: %i\n" \
                 % (self.stripecount, self.stripesize, self.stripeoffset)
        for ost in self.ostobjects:
            string += ("Objidx:\t %i \tObjid:\t %i\n" % (ost.l_ost_idx,
                                                         ost.l_object_id))
        return(string)
        
    def __init__(self):
        """
        Initializes the object's attributes, including a lovdata object, stripe
        count, stripe size, stripe offset, and an empty list to store ost objects.

        """
        self.lovdata = lov_user_md_v1()
        self.stripecount = -1
        self.stripesize = 0
        self.stripeoffset = -1
        self.ostobjects = []



    def isstriped(self):
        """
        Determines whether the stripe count is greater than one or equal to -1,
        indicating that the object is striped.

        Returns:
            bool: True when the object has more than one stripe or no stripes, and
            False when it has exactly one stripe.

        """
        if self.stripecount > 1 or self.stripecount == -1:
            return(True)
        else:
            return(False)
    
    
def getstripe(filename):
    """
    Retrieves stripe information for a given Lustre file and stores it in a
    `stripeObj` object. It handles errors and populates the object's attributes,
    such as `stripecount`, `stripesize`, and `stripeoffset`, based on the file's
    stripe configuration.

    Args:
        filename (str): Referenced by the `lustre.llapi_file_get_stripe` function,
            indicating that it is a file name on a Lustre file system for which
            stripe information is being retrieved.

    Returns:
        stripeObj: Populated with stripe information and a list of OST objects.

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
    Creates a file with specified stripes on a Lustre file system. It opens a file
    with the given name, size, offset, and count, and applies a stripe pattern to
    it.

    Args:
        filename (str): Required. It specifies the name of the file for which the
            stripe settings are being configured.
        stripeobj (Dict[str, int]): Used to override default stripe settings. It
            contains three attributes: `stripesize`, `stripeoffset`, and `stripecount`,
            which are used to set the stripe size, offset, and count, respectively.
        stripesize (int): Optional. It specifies the size of each stripe in bytes.
            If a `stripeobj` is provided, it overrides the specified `stripesize`.
        stripeoffset (int): Defaulted to -1. It represents the offset in bytes of
            the file to start the stripe.
        stripecount (int): Set to a value of 1 by default, indicating a single
            stripe. It can be overridden by passing a value or by using a `stripeobj`
            instance.

    Returns:
        int: 0 when the file is opened successfully, indicating no error.

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
    Redirects the standard error output to a pipe, allowing it to be captured and
    read later. It creates a duplicate of the standard error descriptor, redirects
    it to the pipe, and stores the original descriptor for later restoration.

    Attributes:
        pipeout (int): A file descriptor representing the write end of a Unix pipe
            created by the `os.pipe()` function.
        pipein (int): A file descriptor representing the input end of a pipe created
            in the `__init__` method.
        oldstderr (int): Initialized with the original file descriptor for standard
            error output (file descriptor 2).
        contents (str): Initialized with an empty string, storing the captured
            stderr output.

    """
    def __init__(self):
        """
        Duplicates the standard error stream, redirects it to a pipe, and stores
        the original standard error file descriptor for later restoration.

        """
        self.pipeout, self.pipein = os.pipe()
        self.oldstderr = os.dup(2)
        os.dup2(self.pipein, 2)
        self.contents=""

    def __str__(self):
        return (self.contents)

    def readData(self):
        """
        Continuously reads data from a pipe until there is no more data to read,
        adding it to the self.contents string in chunks of 1024 bytes.

        """
        while self.checkData():
            self.contents += os.read(self.pipeout, 1024)
            
    def checkData(self):
        """
        Checks if data is available on the pipeout file descriptor within a timeout
        of 0 seconds. It uses the select function to wait for readable pipeout,
        returning True if data is available, otherwise False.

        Returns:
            bool: True if there is data available to be read from the pipe, and
            False otherwise.

        """
        r, _, _ = select.select([self.pipeout], [], [], 0)
        return bool(r)

    def stopCapture(self):
        """
        Restores the original stderr stream and closes the pipe connections.

        """
        os.dup2(self.oldstderr, 2)
        os.close(self.pipeout)
        os.close(self.pipein)
