from distutils import sysconfig
from distutils.core import setup
from distutils.command.build import build

import subprocess
import ctypes.util
import os
import sys
import shutil
import re

VERSION_PY = """
# This file is originally generated from Git information by running 
#'setup.py  sdist'.  Distribution tarballs contain a pre-generated 
#copy of this file.

__version__ = '%s'
"""
def update_version():
    """
    Updates the version number in a Python project by checking if it's a Git
    repository, running `git describe` command if it is, or checking the version
    number from distribution files if not. It then prints the updated version
    number and returns it.

    Returns:
        str: The current version of the software.

    """

    ver = "UNKNOWN"
    if os.path.isdir(".git"):
        try:
            p = subprocess.Popen(["git", "describe",
                                  "--abbrev=4", "--tags",
                                  "--dirty"],
                                 stdout=subprocess.PIPE)
        except EnvironmentError:
            print "In a git repository, but unable to run git."

        stdout = p.communicate()[0]
        if p.returncode != 0:
            print "In a git repository, but unable to run git."

        ver = stdout.strip()
        f = open("_version.py", "w")
        f.write(VERSION_PY % ver)
        f.close()
        print "Setting version from git." 
    else:
        try:
            from _version import __version__ as ver
            print "Setting version from distribution."
        except ImportError:
            try:
                ver = os.path.basename(os.getcwd()).split("-")[1]
                print "Setting version from directory name."
            except IndexError:
                print "unable to determine version from directory name."
    print "version '%s'" % ver
    return (ver)

def build_liblustre():
    """
    Checks for the presence of the `liblustreapi` shared or static library on the
    system, and copies it to the `pcplib` directory if not found.

    Returns:
        void: Not captured or defined.

    """

    # See if we have a .so already installed in the system.
    liblocation = ctypes.util.find_library("lustreapi")
    if liblocation:
        print "Found a system liblustreapi.so."
        print "Not packaging our own."
        return()
    # if we have a copy our lib directory, leave it alone.
    if os.path.exists("pcplib/liblustreapi.so"):
        print "Lustre library already built."
        return()

    have_sharedlib = False
    have_staticlib = False

    # Search user defined and system library locations until
    # we find one.
    lib_locations = ["/usr/lib","/lib"]
    if LIBLUSTRE_LOC:
        lib_locations.insert(0, LIBLUSTRE_LOC)

    for location in lib_locations:
        print "Looking for liblustreapi.[so|a] in %s" % location
        liblustre_shared = (os.path.join(location, "liblustreapi.so"))
        liblustre_static = (os.path.join(location, "liblustreapi.a"))

        if os.path.exists(liblustre_shared):
            have_sharedlib = True
            break
        if  os.path.exists(liblustre_static):
            have_staticlib = True
            break
    # Copy shared library into the dist tree.
    if have_sharedlib:
        print "Using liblustreapi.so from %s" %location
        shutil.copy(liblustre_shared,"pcplib/liblustreapi.so")
    # static lib needs converting to a .so
    if have_staticlib:
        print "Found liblustreapi.a in %s" % location
        convert_liblustre(location)

    if not ( have_staticlib or have_sharedlib ):
        print """
WARNING: Unable to find liblustreapi C library.
It should be installed as part of the lustre client package.

Continuing, but pcp will be build without lustre features.

If the library is installed in a non standard location,
use the following option to setup.py to point to the
libary location:

--with-liblustre=/path/to/library
"""

def convert_liblustre(lib_location):
    """
    1) extracts the liblustreapi.a library, 2) compiles it into a shared library
    (.so), and 3) loads the resulting library into memory using ctypes.

    Args:
        lib_location (str): Used to specify the location of the `liblustreapi.a`
            library file.

    """
    
    liblustre=os.path.join(lib_location,"liblustreapi.a")
    print "Converting liblustreapi.a to liblustreapi.so"
    p = subprocess.Popen(["ar","-x","-v",liblustre],
                         stdout=subprocess.PIPE)
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print "Error extracting liblustreapi.a"
        exit(1)

    p = subprocess.Popen(["gcc","-shared","liblustreapi.o",
                          "-o","pcplib/liblustreapi.so"],
                         stdout=subprocess.PIPE)
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print "Error recompiling liblustreapi.so"
        exit(1)

    try:
        lustre = ctypes.CDLL("pcplib/liblustreapi.so")
        funptr = lustre.llapi_file_create

    except OSError, AttributeError:
        print "Unable to convert liblustreapi.a to a .so."
        print "Please read the README for hints on how to try"
        print "this yourself."
        exit(1)
    print "liblustreapi.a -> .so conversion sucessful."


class mybuild_py(build):
    """
    Performs two functions: calling `build_liblustre()` and delegating to `run()`.

    """
    def run(self):
        """
        Of `mybuild_py` class invokes the `build.run()` method, passing `self` as
        argument, to execute the build process.

        """
        build_liblustre()
        build.run(self)
        

# Parse our optional argument
LIBLUSTRE_LOC = None
for arg in sys.argv:
    if "--with-liblustre=" in arg:
        LIBLUSTRE_LOC = arg.split("=")[1]
        sys.argv.remove(arg)

# Grab version out of git, or the dist tarball.
version = update_version()

# We may not have a liblustreapi.so to ship, but
# it looks like setuptools silently ignores missing
# data files, so the right thing happens.
setup(name = "pcp",
      cmdclass={"build": mybuild_py, 
                },
      description = "A parallel copy program",
      url = "https://github.com/wtsi-ssg/pcp",
      version = version,
      author = "Guy Coates",
      author_email = "gmpc@sanger.ac.uk",
      scripts = ["pcp"],
      packages=["pcplib"],
      package_data = {"pcplib": ["liblustreapi.so"]}
)
