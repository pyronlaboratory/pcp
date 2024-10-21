#Copyright Genome Research Ltd 2014
# Author gmpc@sanger.ac.uk
# This program is released under the GNU Public License V2 or later (GPLV2+)

import os
import errno

def safestat(filename):
    """
    Attempts to retrieve file status information for a given filename, using a
    retry mechanism to handle interrupted system calls and other transient errors.

    Args:
        filename (str): Designated to hold the path to a file for which the file
            status data is to be retrieved.

    Returns:
        osstat_result: A collection of file status information, including file
        type, permissions, owner, group, and other attributes.

    """
    while True:
        try:
            statdata = os.lstat(filename)
            return(statdata)
        except IOError, error:
            if error.errno != errno.EINTR:
                raise
