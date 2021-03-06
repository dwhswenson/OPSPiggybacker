from nose.tools import (
    assert_equal, assert_not_equal, assert_almost_equal, raises, assert_true
)
from nose.plugins.skip import Skip, SkipTest



from numpy.testing import assert_array_almost_equal
import numpy as np

import os
from pkg_resources import resource_filename

def data_filename(fname, subdir='test_data'):
    return resource_filename('ops_piggybacker',
                             os.path.join('tests', subdir, fname))

def assert_items_equal(truth, beauty):
    assert_equal(len(truth), len(beauty))
    for (t, b) in zip(truth, beauty):
        assert_equal(t, b)

import logging
logging.getLogger('openpathsampling.netcdfplus').setLevel(logging.CRITICAL)
logging.getLogger('openpathsampling.ensemble').setLevel(logging.CRITICAL)
logging.getLogger('openpathsampling.initialization').setLevel(logging.CRITICAL)
logging.getLogger('openpathsampling.storage').setLevel(logging.CRITICAL)
