#Copyright Genome Research Ltd 2014
# Author gmpc@sanger.ac.uk
# This program is released under the GNU Public License V2 or later (GPLV2+)

import os
import errno

def safestat(filename):
    """
    Attempts to retrieve file metadata using the `os.lstat()` method, and returns
    the result if successful, or raises an exception if there is an error.

    Args:
        filename (str): Used to represent the name of the file for which the file
            status is being checked.

    Returns:
        osStatData: A tuple containing information about the file or directory
        such as its size, permissions, and access time.

    """
    while True:
        try:
            statdata = os.lstat(filename)
            return(statdata)
        except IOError, error:
            if error.errno != errno.EINTR:
                raise
