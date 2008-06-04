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
    Filter API and constants
"""

# Pyrex compile-time imports
from h5  cimport herr_t, htri_t

# Runtime imports
import h5
from h5 import DDict
from errors import FilterError

# === Public constants and data structures ====================================

FILTER_ERROR    = H5Z_FILTER_ERROR
FILTER_NONE     = H5Z_FILTER_NONE
FILTER_ALL      = H5Z_FILTER_ALL
FILTER_DEFLATE  = H5Z_FILTER_DEFLATE
FILTER_SHUFFLE  = H5Z_FILTER_SHUFFLE
FILTER_FLETCHER32 = H5Z_FILTER_FLETCHER32
FILTER_SZIP     = H5Z_FILTER_SZIP
FILTER_RESERVED = H5Z_FILTER_RESERVED
FILTER_MAX      = H5Z_FILTER_MAX
FILTER_NMAX     = H5Z_MAX_NFILTERS

FLAG_DEFMASK    = H5Z_FLAG_DEFMASK
FLAG_MANDATORY  = H5Z_FLAG_MANDATORY
FLAG_OPTIONAL   = H5Z_FLAG_OPTIONAL
FLAG_INVMASK    = H5Z_FLAG_INVMASK
FLAG_REVERSE    = H5Z_FLAG_REVERSE
FLAG_SKIP_EDC   = H5Z_FLAG_SKIP_EDC

#skip SZIP options

FILTER_CONFIG_ENCODE_ENABLED = H5Z_FILTER_CONFIG_ENCODE_ENABLED
FILTER_CONFIG_DECODE_ENABLED = H5Z_FILTER_CONFIG_DECODE_ENABLED

ERROR_EDC   = H5Z_ERROR_EDC
DISABLE_EDC = H5Z_DISABLE_EDC
ENABLE_EDC  = H5Z_ENABLE_EDC
NO_EDC      = H5Z_NO_EDC


# === Filter API  =============================================================

def filter_avail(int filter_id):

    cdef htri_t retval
    retval = H5Zfilter_avail(<H5Z_filter_t>filter_id)
    if retval < 0:
        raise FilterError("Can't determine availability of filter %d" % filter_id)
    return bool(retval)

def get_filter_info(int filter_id):

    cdef herr_t retval
    cdef unsigned int flags
    retval = H5Zget_filter_info(<H5Z_filter_t>filter_id, &flags)
    if retval < 0:
        raise FilterError("Can't determine flags of filter %d" % filter_id)
    return flags

# === Python extensions =======================================================

PY_FILTER = DDict({ H5Z_FILTER_ERROR: 'ERROR', H5Z_FILTER_NONE: 'NONE',
            H5Z_FILTER_ALL: 'ALL', H5Z_FILTER_DEFLATE: 'DEFLATE',
            H5Z_FILTER_SHUFFLE: 'SHUFFLE', H5Z_FILTER_FLETCHER32: 'FLETCHER32',
            H5Z_FILTER_SZIP: 'SZIP', H5Z_FILTER_RESERVED: 'RESERVED'})

PY_FLAG = DDict({ H5Z_FLAG_DEFMASK: 'DEFMASK', H5Z_FLAG_MANDATORY: 'MANDATORY',
            H5Z_FLAG_OPTIONAL: 'OPTIONAL', H5Z_FLAG_INVMASK: 'INVMASK',
            H5Z_FLAG_REVERSE: 'REVERSE', H5Z_FLAG_SKIP_EDC: 'SKIP EDC' })

PY_FILTER_CONFIG = DDict({H5Z_FILTER_CONFIG_ENCODE_ENABLED: 'ENCODE ENABLED',
                        H5Z_FILTER_CONFIG_DECODE_ENABLED: 'ENCODE DISABLED'})

PY_EDC   = DDict({H5Z_ERROR_EDC: 'ERROR', H5Z_DISABLE_EDC: 'DISABLE EDC',
                    H5Z_ENABLE_EDC: 'ENABLE EDC', H5Z_NO_EDC: 'NO EDC' })












