# Copyright (c) Genome Research Ltd 2014
# Author Guy Coates <gmpc@sanger.ac.uk>
# This program is released under the GNU Public License V2 or later (GPLV2+)
import os
import readdir
import stat
import safestat

def fastwalk (sourcedir, onerror=None, topdown=True):
    """
    Traverses a directory tree and yields a tuple of (source directory, subdirectory
    list, file list) for each directory it encounters. It also recursively traverses
    subdirectories and yields additional tuples for each directory found.

    Args:
        sourcedir (osPathLike|str): Used to specify the starting directory for the
            recursive walk.
        onerror (Optional[Callable]): Used to handle errors that occur during the
            recursive traversal of the directory tree. It takes an exception object
            as input and can be used to perform custom error handling.
        topdown (bool): Used to indicate whether the walk should be performed
            recursively or not. If set to True, the function will perform a recursive
            walk of the directory tree; if set to False, it will only return the
            direct children of the starting directory.

    Yields:
        Tuple[str,List[str],List[str]]: A source directory path, a list of
        directories, and a list of files.

    """
    
    dirlist = []
    filelist = []

    try:
        entries = readdir.readdir(sourcedir)
    except Exception as  err:
        if onerror is not None:
            onerror(err)
        return

    for entry in entries:
        name = entry.d_name
        filetype = entry.d_type
    
        if not name in (".", ".."):
            if filetype == readdir.dirent.DT_UNKNOWN:
                fullname = os.path.join(sourcedir, name)
                mode = safestat.safestat(fullname).st_mode
                if stat.S_ISDIR(mode):
                    filetype = readdir.dirent.DT_DIR
                else:
                    filetype = readdir.dirent.DT_REG

            if filetype == readdir.dirent.DT_DIR:
                dirlist.append(name)
            else:
                filelist.append(name)

    if topdown:
        yield sourcedir, dirlist, filelist

    for d in dirlist:
        fullname = os.path.join(sourcedir, d)
        for entries in fastwalk(fullname, onerror, topdown):
            yield entries

    if not topdown:
        yield sourcedir, dirlist, filelist
