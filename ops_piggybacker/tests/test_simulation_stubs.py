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

        nojoin = oink.ShootingStub(tps_ensemble, pre_joined=False)
        self.nojoin_pseudosim = oink.ShootingPseudoSimulator(
            storage=self.storage,
            initial_conditions=paths.SampleSet([initial_sample]),
            mover=nojoin,
            network=network
        )

    
    def teardown(self):
        if os.path.isfile(data_filename(self.fname)):
            os.remove(data_filename(self.fname))

    def test_noprejoin_run_and_analyze(self):
        moves = [(move[0], move[4], move[2], move[3], move[5]) 
                 for move in common.tps_shooting_moves]
        self.nojoin_pseudosim.run(moves)
        self.storage.close()
        # open the file for analysis, check that its content is reasonable
        analysis = paths.AnalysisStorage(data_filename(self.fname))
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

    def test_run_and_analyze(self):
        moves = [tuple(move[0:4]) for move in common.tps_shooting_moves]

        trajs = zip(*moves)[1]
        init_traj = self.pseudosim.initial_conditions[0].trajectory
        # print hex(id(init_traj)), hex(id(trajs[0]))
        shared = init_traj.shared_subtrajectory(trajs[0])
        # print len(shared), [s for s in shared]
        # print len(init_traj.shared_subtrajectory(trajs[0]))
        # print [len(trajs[i].shared_subtrajectory(trajs[i+1]))
               # for i in range(len(trajs)-1)]

        self.pseudosim.run(moves)
        self.storage.close()

        # open the file for analysis, check that its content is reasonable
        analysis = paths.AnalysisStorage(data_filename(self.fname))
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
