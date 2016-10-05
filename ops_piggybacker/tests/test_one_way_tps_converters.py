import ops_piggybacker as oink
import openpathsampling as paths

from .tools import *
from . import common_test_data as common
from openpathsampling.tests.test_helpers import make_1d_traj
import os.path

class StupidOneWayTPSConverter(oink.OneWayTPSConverter):
    """Test-ready subclass"""
    def __init__(self, storage, initial_file, mover, network, options=None):
        self.test_dir = os.path.join(
            os.path.dirname(__file__),
            "test_data", "one_way_tps_examples"
        )
        super(StupidOneWayTPSConverter, self).__init__(
            storage=storage,
            initial_file=initial_file,
            mover=mover,
            network=network,
            options=options
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
        self.network = old_store.networks[0]
        tps_ensemble=self.network.sampling_ensembles[0]
        shoot = oink.ShootingStub(tps_ensemble)
        self.converter = StupidOneWayTPSConverter(
            storage=paths.Storage(self.data_filename("output.nc"), "w"),
            initial_file="file0.data",
            mover=shoot,
            network=self.network,
            options=oink.TPSConverterOptions(includes_shooting_point=False,
                                             trim=False)
        )
        self.extras_converter = StupidOneWayTPSConverter(
            storage=paths.Storage(self.data_filename("extras.nc"), 'w'),
            initial_file="file0_extra.data",
            mover=shoot,
            network=self.network,
            options=oink.TPSConverterOptions(trim=True,
                                             auto_reverse=True,
                                             includes_shooting_point=True)
        )

    def tearDown(self):
        if os.path.isfile(self.data_filename("output.nc")):
            os.remove(self.data_filename("output.nc"))
        if os.path.isfile(self.data_filename("extras.nc")):
            os.remove(self.data_filename("extras.nc"))

    def test_parse_summary_line(self):
        summary = open(self.data_filename("summary.txt"), "r")
        lines = [l for l in summary]
        moves = common.tps_shooting_moves
        
        for line, move in zip(lines, moves):
            parsed_line = self.converter.parse_summary_line(line)
            assert_equal(parsed_line[0], move[0])  # replicas
            assert_array_almost_equal(parsed_line[1].coordinates, 
                                      move[4].coordinates)  # trajectories
            assert_equal(parsed_line[2], move[2])  # shooting points
            assert_equal(parsed_line[3], move[5])  # directions
            assert_equal(parsed_line[4], move[3])  # acceptance

    def test_parse_summary_line_extras(self):
        summary = open(self.data_filename("summary_extra.txt"), "r")
        lines = [l for l in summary]
        moves = common.tps_shooting_moves

        for line, move in zip(lines, moves):
            parsed_line = self.extras_converter.parse_summary_line(line)
            assert_equal(parsed_line[0], move[0])  # replicas
            assert_array_almost_equal(parsed_line[1].coordinates, 
                                      move[4].coordinates)  # trajectories
            assert_equal(parsed_line[2], move[2])  # shooting points
            assert_equal(parsed_line[3], move[5])  # directions
            assert_equal(parsed_line[4], move[3])  # acceptance

    def test_default_options(self):
        converter = StupidOneWayTPSConverter(
            storage=None,
            initial_file="file0.data",
            mover=oink.ShootingStub(self.network.sampling_ensembles[0]),
            network=self.network
        )
        assert_equal(converter.options.trim, True)
        assert_equal(converter.options.auto_reverse, False)
        assert_equal(converter.options.includes_shooting_point, True)

    def test_run(self):
        raise SkipTest

    def test_run_without_initial(self):
        raise SkipTest
