#!/usr/bin/env python

#+
# 
# This file is part of h5py, a low-level Python interface to the HDF5 library.
# 
# Copyright (C) 2008 Andrew Collette
# http://h5py.alfven.org
# License: BSD  (See LICENSE.txt for full license)
# 
# $Date$
# 
#-

"""
    Setup script for the h5py package.

    To install h5py, run "python setup.py build" followed by
    "python setup.py install".  You may need sudo priviledges for the second
    command.

    Implements a few new commands, in addition to standard commands like
    "build" and "install":
    
    1.  "test"
        Build the package locally (don't install it) and run unit tests. Exits
        Python with a nonzero error code if any of the unit tests fail.  Test
        output (unittest.TextTestRunner) is written to stdout/stderr.
    
    2.  "dev"
        Developer commands.  Runs "build" and optionally:
        --doc               Rebuilds HTML documentation
        --readme <name>     Generates an HTML form of the README.txt document.

    New option: "--revision" appends the SVN revision and current build number
    to the version string; again mainly for development.
"""

__revision__ = "$Id$"

from distutils.cmd import Command
from distutils.errors import DistutilsError, DistutilsExecError
from distutils.core import setup
from distutils.extension import Extension
import os
import sys

# Distutils tries to use hard links when building source distributions, which 
# fails under a wide variety of network filesystems under Linux.
delattr(os, 'link') # goodbye!

try:
    os.remove('MANIFEST') # why the hell are we caching this information
except OSError:
    pass

# === Global constants ========================================================

NAME = 'h5py'
VERSION = '0.1.1'
REVISION = "$Rev: 0$"

# If you have your HDF5 *.h files and libraries somewhere not in /usr or
# /usr/local, add that path here.
custom_include_dirs = []    # = ["/some/other/path", "/an/other/path"]
custom_library_dirs = []

# === Custom extensions for distutils =========================================

class test(Command):
    description = "Build %s and run unit tests" % NAME
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        buildobj = self.distribution.get_command_obj('build')
        buildobj.run()
        oldpath = sys.path
        sys.path = [os.path.abspath(buildobj.build_lib)] + oldpath
        import h5py.tests
        if not h5py.tests.runtests():
            raise DistutilsError("Unit tests failed.")
        sys.path = oldpath

class dev(Command):
    description = "Developer commands (--doc, --readme=<file>)"
    user_options = [('doc','d','Rebuild documentation'),
                    ('readme=','r','Rebuild HTML readme file'),
                    ('inspect', 'i', 'Don\'t use this.')]
    boolean_options = ['doc', 'inspect']

    def initialize_options(self):
        self.doc = False
        self.readme = False

    def finalize_options(self):
        pass

    def run(self):
        if self.doc:
            buildobj = self.distribution.get_command_obj('build')
            buildobj.run()
        
        if self.doc:
            retval = os.spawnlp(os.P_WAIT, 'epydoc', '-q', '--html', '-o', 'docs/',
                               '--config', 'docs.cfg', os.path.join(buildobj.build_lib, NAME) )
            if retval != 0:
                raise DistutilsExecError("Could not run epydoc to build documentation.")

        if self.readme:
            import docutils.core
            fh = open('README.txt','r')
            parts = docutils.core.publish_parts(fh.read(),writer_name='html')
            fh.close()
            fh = open(self.readme,'w')
            fh.write(parts['body'])
            fh.close()

# === Versioning setup ========================================================

for arg in sys.argv[:]:
    if arg.find('--revision') == 0:
        REVDIGITS = '0'
        try:
            tmpstring = REVISION[5:-2].strip()
            if tmpstring.isdigit(): REVDIGITS = tmpstring
        except KeyError:
            pass

        VERSION = VERSION + '-r' + REVDIGITS
        
        sys.argv.remove(arg)

# Automatically update the h5py source with current version info and
# docstring from current README file
vfile = open(os.path.join(NAME,'version.py'),'w')
rdfile = open('README.txt','r')
vfile.write('# This file is automatically generated; do not edit.\n')
vfile.write('"""\nPackage "h5py" extended information\n\n%s"""\nversion = "%s"\n\n' % (rdfile.read(), VERSION))
rdfile.close()
vfile.close()

# === Setup configuration =====================================================

min_pyrex_version = '0.9.6.4'
min_numpy_version = '1.0.3'

def fatal(instring):
    print "Fatal: "+instring
    exit(2)

# Check Python version
if not (sys.version_info[0] >= 2 and sys.version_info[1] >= 5):
    fatal("At least Python 2.5 is required to install h5py")

# Check for Numpy (required)
try:
    import numpy
    if numpy.version.version < min_numpy_version:
        raise ImportError()
except ImportError:
    fatal("Numpy version >= %s required" % min_numpy_version)

# Check for Pyrex (also required)
try:
    from Pyrex.Compiler.Main import Version
    if Version.version < min_pyrex_version:
        raise ImportError()
    from Pyrex.Distutils import build_ext
except ImportError:
    fatal("Pyrex is unavailable or out of date (>= %s required)." % min_pyrex_version)

ext_exten = '.pyx'

# Pyrex extension modules
pyx_modules = ['h5' , 'h5f', 'h5g', 'h5s', 'h5t', 
               'h5d', 'h5a', 'h5p', 'h5z', 'h5i', 'h5r']

pyx_src_path = 'h5py'
pyx_extra_src = ['utils_low.c']         # C source files required for Pyrex code
pyx_libraries = ['hdf5']            # Libraries to link into Pyrex code

# Compile-time include and library dirs for Pyrex code
pyx_include = [numpy.get_include()] 
pyx_include.extend(['/usr/include', '/usr/local/include'])
pyx_include.extend(custom_include_dirs)
pyx_library_dirs = ['/usr/lib', '/usr/local/lib']
pyx_library_dirs.extend(custom_library_dirs)

# Additional compiler flags for Pyrex code
pyx_extra_args = ['-Wno-unused', '-DH5_USE_16_API']

extra_link_args = []
extra_compile_args = pyx_extra_args


# === Setup implementation ====================================================

# Create extensions
pyx_extensions = []
for module_name in pyx_modules:
    sources  = [os.path.join(pyx_src_path, module_name) + ext_exten]
    sources += [os.path.join(pyx_src_path, x) for x in pyx_extra_src]

    pyx_extensions.append(
        Extension( 
            NAME+'.'+module_name,
            sources, 
            include_dirs = pyx_include, 
            libraries = pyx_libraries,
            library_dirs = pyx_library_dirs, 
            extra_compile_args = extra_compile_args,
            extra_link_args = extra_link_args
        )
    )

# Run setup
setup(
  name = NAME,
  version = VERSION,
  author = 'Andrew Collette',
  url = 'h5py.alfven.org',
  packages = ['h5py','h5py.tests'],
  package_data = {'h5py': ['*.pyx'],  # so source is available for tracebacks
                  'h5py.tests': ['data/*.hdf5']},
  ext_modules= pyx_extensions,
  requires = ['numpy (>=1.0.3)','Pyrex (>=0.9.6)'],  # "0.9.6.4 is not a valid version string"???
  provides = ['h5py'],
  cmdclass = {'build_ext': build_ext, 'dev': dev, 'test': test}
)


