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
        shoot = oink.ShootingStub(tps_ensemble, pre_joined=False)
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
            assert_equal(parsed_line[3], move[3])  # acceptance
            assert_equal(parsed_line[4], move[5])  # directions

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
            assert_equal(parsed_line[3], move[3])  # acceptance
            assert_equal(parsed_line[4], move[5])  # direction

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
        self.converter.run(self.data_filename("summary.txt"))
        self.converter.storage.close()
        analysis = paths.AnalysisStorage(self.data_filename("output.nc"))

        # next is same as test_simulation_stubs  (move to a common test?)
        assert_equal(len(analysis.steps), 5) # initial + 4 steps
        scheme = analysis.schemes[0]
        assert_equal(scheme.movers.keys(), ['shooting'])
        assert_equal(len(scheme.movers['shooting']), 1)
        mover = scheme.movers['shooting'][0]

        # use several OPS tools to analyze this file
        ## scheme.move_summary
        devnull = open(os.devnull, 'w')
        scheme.move_summary(analysis.steps, output=devnull) 
        mover_keys = [k for k in scheme._mover_acceptance.keys()
                      if k[0] == mover]
        assert_equal(len(mover_keys), 1)
        assert_equal(scheme._mover_acceptance[mover_keys[0]], [3,4])

        ## move history tree
        import openpathsampling.visualize as ops_vis
        history = ops_vis.PathTree(
            analysis.steps,
            ops_vis.ReplicaEvolution(replica=0)
        )
        assert_equal(len(history.generator.decorrelated_trajectories), 2)

        ## path length histogram
        path_lengths = [len(step.active[0].trajectory) 
                        for step in analysis.steps]
        assert_equal(path_lengths, [11, 9, 7, 7, 7])
