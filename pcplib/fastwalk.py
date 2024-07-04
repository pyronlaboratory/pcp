# Copyright (c) Genome Research Ltd 2014
# Author Guy Coates <gmpc@sanger.ac.uk>
# This program is released under the GNU Public License V2 or later (GPLV2+)
import os
import readdir
import stat
import safestat

def fastwalk (sourcedir, onerror=None, topdown=True):
    """
    Iterates through subdirectories and files within a given source directory,
    recursively calling itself for each directory until all files and directories
    are processed. It returns an iterator over the source directory, its subdirectories,
    and the files within those subdirectories.

    Args:
        sourcedir (ospathPathlike): Used to specify the directory to walk through,
            recursively listing its contents.
        onerror (OptionalCallable): Used to handle errors that may occur during
            the traversal of the directory tree.
        topdown (bool): Used to control the recursion depth of the function. When
            set to `True`, the function recursively traverses directories; when
            set to `False`, it only lists the top-level files in the directory.

    Yields:
        tuple: Composed of three elements: the source directory, a list of
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
