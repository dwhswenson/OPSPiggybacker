import openpathsampling as paths
import ops_piggybacker as oink
import os

from . import common_test_data as common
from .tools import *
from openpathsampling.tests.test_helpers import make_1d_traj

class testShootingPseudoSimulator(object):
    fname="test_pseudo_shoot.nc"
    def setup(self):
        if os.path.isfile(data_filename(self.fname)):
            os.remove(data_filename(self.fname))

        shoot = oink.ShootingStub(common.tps_ensemble)
        template = make_1d_traj([0.0])[0]
        self.storage = paths.Storage(data_filename(self.fname), "w",
                                     template)

        self.pseudosim = oink.ShootingPseudoSimulator(
            storage=None, #self.storage,
            initial_conditions=paths.SampleSet([common.initial_tps_sample]),
            mover=shoot,
            network=common.tps_network
        )
    
    def teardown(self):
        if os.path.isfile(data_filename(self.fname)):
            os.remove(data_filename(self.fname))


    def test_run_and_analyze(self):
        self.pseudosim.run(common.tps_shooting_moves)
        # self.storage.close()
        raise SkipTest
