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

        setup_storage = paths.Storage(data_filename("tps_setup.nc"), "r")
        network = setup_storage.networks[0]
        tps_ensemble = network.sampling_ensembles[0]
        initial_sample = paths.Sample(
            replica=0, 
            trajectory=common.initial_tps_sample.trajectory,
            ensemble=tps_ensemble
        )
        template = initial_sample.trajectory[0]

        shoot = oink.ShootingStub(tps_ensemble)
        self.storage = paths.Storage(data_filename(self.fname), "w",
                                     template)

        self.pseudosim = oink.ShootingPseudoSimulator(
            storage=self.storage,
            initial_conditions=paths.SampleSet([initial_sample]),
            mover=shoot,
            network=network
        )
    
    def teardown(self):
        if os.path.isfile(data_filename(self.fname)):
            os.remove(data_filename(self.fname))


    def test_run_and_analyze(self):
        self.pseudosim.run(common.tps_shooting_moves)
        self.storage.close()
        raise SkipTest
