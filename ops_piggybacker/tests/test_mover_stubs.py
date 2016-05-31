import ops_piggybacker as oink
import openpathsampling as paths

from . import common_test_data as common
from .tools import *

class testNoEngine(object):
    def test_init(self):
        # only test that it instantiates
        oink.mover_stubs.NoEngine()


class testShootingStub(object):
    def setup(self):
        # this instantiates an object, and ensures that instantiation works
        self.stub = oink.ShootingStub(common.tps_ensemble)

    def test_forward_move(self):
        # this checks that we get a reasonable PMC out of a given move
        # TODO: check the return value in detail
        pass

    def test_backward_move(self):
        # TODO: check the return value in detail
        pass

    def test_rejected_move(self):
        # TODO: check the return value in detail
        pass
