import ops_piggybacker as oink
import openpathsampling as paths

from .tools import *
from openpathsampling.tests.test_helpers import make_1d_traj
import os.path

class StupidOneWayTPSConverter(oink.OneWayTPSConverter):
    """Test-ready subclass"""
    def __init__(self, storage, initial_file, mover, network):
        self.test_dir = os.path.join(
            os.path.dirname(__file__),
            "test_data", "one_way_tps_examples"
        )
        super(StupidOneWayTPSConverter, self).__init__(
            storage=storage,
            initial_file=initial_file,
            mover=mover,
            network=network
        )
        
    def load_trajectory(self, file_name):
        f = open(os.path.join(self.test_dir, file_name), "r")
        traj_list = [float(line) for line in f]
        return make_1d_traj(traj_list)
        

class TestOneWayTPSConverter(object):
    def setUp(self):
        test_dir = "one_way_tps_examples"
        self.data_filename = lambda f : \
                data_filename(os.path.join(test_dir, f))
        old_store = paths.Storage(data_filename("tps_setup.nc"), "r")
        network = old_store.networks[0]
        tps_ensemble=network.sampling_ensembles[0]
        shoot = oink.ShootingStub(tps_ensemble)
        self.converter = StupidOneWayTPSConverter(
            storage=paths.Storage(self.data_filename("output.nc"), "w"),
            initial_file="file0.data",
            mover=shoot,
            network=old_store.networks[0]
        )

    def tearDown(self):
        if os.path.isfile(self.data_filename("output.nc")):
            os.remove(self.data_filename("output.nc"))

    def test_parse_summary_line(self):
        summary = open(self.data_filename("summary.txt"), "r")
        replicas = [0] * 4
        trajectories = [0.0]*4  # TODO: placeholder
        shooting_points = [4, 2, 5, 4]
        directions = [-1, 1, -1, -1]
        acceptances = [True, True, False, True]
        moves = zip(replicas, trajectories, shooting_points, directions,
                    acceptances)
        lines = [l for l in summary]
        for line, move in zip(lines, moves):
            parsed_line = self.converter.parse_summary_line(
                line=line,
                includes_shooting_point=False,
                trim=False  # TODO: switch this to true
            )
            assert_equal(parsed_line[0], move[0])  # replicas
            # trajectories
            assert_equal(parsed_line[2], move[2])  # shooting points
            assert_equal(parsed_line[3], move[3])  # directions
            assert_equal(parsed_line[4], move[4])  # acceptance

        raise SkipTest

    def test_run(self):
        raise SkipTest

    def test_run_without_initial(self):
        raise SkipTest
