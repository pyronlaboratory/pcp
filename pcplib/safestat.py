#Copyright Genome Research Ltd 2014
# Author gmpc@sanger.ac.uk
# This program is released under the GNU Public License V2 or later (GPLV2+)

import os
import errno

def safestat(filename):
    """
    Tries to stat a file repeatedly until it succeeds, returning the last successful
    stat data if successful.

    Args:
        filename (str): Passed as the address of a filename to check for modification.

    Returns:
        StatData|None: 16-bit integer containing file metadata or None if an error
        occurs during stat operation.

    """
    while True:
        try:
            statdata = os.lstat(filename)
            return(statdata)
        except IOError, error:
            if error.errno != errno.EINTR:
                raise
