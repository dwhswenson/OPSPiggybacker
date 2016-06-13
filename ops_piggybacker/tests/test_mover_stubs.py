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

    def test_join_one_way(self):
        raise SkipTest

    def test_backward_move(self):
        initial_sample = common.initial_tps_sample
        move = common.tps_shooting_moves[0]
        replica = move[0]
        trial_trajectory = move[1]
        shooting_point = initial_sample.trajectory[move[2]]
        accepted = move[3]
        change = self.stub.move(initial_sample, trial_trajectory,
                                shooting_point, accepted)
        # assertions about the shape of the decision history
        assert_equal(change.mover, self.stub.mimic)
        assert_equal(change.subchange, change.canonical)
        assert_equal(change.subchange.subchange, None)
        assert_equal(len(change.trials), 1)
        # assertions true for any OneWayShooting
        details0 = change.canonical.trials[0].details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, True)
        assert_equal(type(change.canonical.mover), paths.BackwardShootMover)

    def test_backward_move_not_pre_joined(self):
        raise SkipTest

    def test_forward_move(self):
        init_traj = common.tps_shooting_moves[0][1]
        initial_sample = paths.Sample(replica=0,
                                      trajectory=init_traj,
                                      ensemble=common.tps_ensemble)
        move = common.tps_shooting_moves[1]
        replica = move[0]
        trial_trajectory = move[1]
        shooting_point = initial_sample.trajectory[move[2]]
        accepted = move[3]
        change = self.stub.move(initial_sample, trial_trajectory,
                                shooting_point, accepted)
        # assertions about the shape of the decision history
        assert_equal(change.mover, self.stub.mimic)
        assert_equal(change.subchange, change.canonical)
        assert_equal(change.subchange.subchange, None)
        assert_equal(len(change.trials), 1)
        # assertions true for any OneWayShooting
        details0 = change.canonical.trials[0].details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, True)
        assert_equal(type(change.canonical.mover), paths.ForwardShootMover)

    def test_forward_move_not_pre_joined(self):
        raise SkipTest

    def test_rejected_move(self):
        initial_sample = common.initial_tps_sample
        move = common.tps_shooting_moves[0]
        replica = move[0]
        trial_trajectory = move[1]
        shooting_point = initial_sample.trajectory[move[2]]
        accepted = False
        change = self.stub.move(initial_sample, trial_trajectory,
                                shooting_point, accepted)
        # assertions about the shape of the decision history
        assert_equal(change.mover, self.stub.mimic)
        assert_equal(change.subchange, change.canonical)
        assert_equal(change.subchange.subchange, None)
        assert_equal(len(change.trials), 1)
        # assertions true for any OneWayShooting
        details0 = change.canonical.trials[0].details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, False)
        assert_equal(type(change.canonical.mover), paths.BackwardShootMover)

    def test_rejected_move_not_pre_joined(self):
        raise SkipTest
