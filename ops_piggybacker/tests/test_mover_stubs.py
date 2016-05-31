import ops_piggybacker as oink
import openpathsampling as paths

class testNoEngine(object):
    def test_init(self):
        # only test that it instantiates
        oink.mover_stubs.NoEngine()


class testShootingStub(object):
    def setup(self):
        # this instantiates an object, and ensures that instantiation works
        pass

    def test_forward_move(self):
        # this checks that we get a reasonable PMC out of a given move
        pass

    def test_backward_move(self):
        pass

    def test_rejected_move(self):
        pass
