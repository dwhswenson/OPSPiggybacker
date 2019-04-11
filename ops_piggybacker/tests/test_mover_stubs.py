import ops_piggybacker as oink
import openpathsampling as paths

from . import common_test_data as common
from .tools import *

class TestNoEngine(object):
    def test_init(self):
        # only test that it instantiates
        oink.mover_stubs.NoEngine()


class TestShootingStub(object):
    def setup(self):
        # this instantiates an object, and ensures that instantiation works
        self.stub = oink.ShootingStub(common.tps_ensemble)
        self.no_prejoin = oink.ShootingStub(common.tps_ensemble,
                                            pre_joined=False)

    def test_join_one_way(self):
        moves = common.tps_shooting_moves
        initial = common.initial_tps_sample.trajectory

        out_1 = moves[0][1]
        sp_1 = initial[moves[0][2]]
        trial_1 = moves[0][4]
        dir_1 = moves[0][5]
        joined_1 = self.no_prejoin.join_one_way(initial, trial_1, sp_1, dir_1)
        assert_equal(joined_1, out_1)

        out_2 = moves[1][1]
        sp_2 = joined_1[moves[1][2]]
        trial_2 = moves[1][4]
        dir_2 = moves[1][5]
        joined_2 = self.no_prejoin.join_one_way(joined_1, trial_2, sp_2, dir_2)
        assert_equal(joined_2, out_2)

        out_3 = moves[2][1]
        sp_3 = joined_2[moves[2][2]]
        trial_3 = moves[2][4]
        dir_3 = moves[2][5]
        joined_3 = self.no_prejoin.join_one_way(joined_2, trial_3, sp_3, dir_3)
        assert_equal(joined_3, out_3)

        out_4 = moves[3][1]
        sp_4 = joined_2[moves[3][2]]
        trial_4 = moves[3][4]
        dir_4 = moves[3][5]
        joined_4 = self.no_prejoin.join_one_way(joined_2, trial_4, sp_4, dir_4)
        assert_equal(joined_4, out_4)

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
        # details0 = change.canonical.trials[0].details
        details0 = change.canonical.details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, True)
        assert_equal(type(change.canonical.mover), paths.BackwardShootMover)

    def test_backward_move_not_pre_joined(self):
        initial_sample = common.initial_tps_sample
        move = common.tps_shooting_moves[0]
        replica = move[0]
        trial_trajectory = move[4]
        shooting_point = initial_sample.trajectory[move[2]]
        accepted = move[3]
        direction = move[5]
        change = self.no_prejoin.move(initial_sample, trial_trajectory,
                                      shooting_point, accepted, direction)
        # assertions about the shape of the decision history
        assert_equal(change.mover, self.no_prejoin.mimic)
        assert_equal(change.subchange, change.canonical)
        assert_equal(change.subchange.subchange, None)
        assert_equal(len(change.trials), 1)
        # assertions true for any OneWayShooting
        # details0 = change.canonical.trials[0].details
        details0 = change.canonical.details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, True)
        assert_equal(type(change.canonical.mover), paths.BackwardShootMover)

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
        # details0 = change.canonical.trials[0].details
        details0 = change.canonical.details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, True)
        assert_equal(type(change.canonical.mover), paths.ForwardShootMover)

    def test_forward_move_not_pre_joined(self):
        init_traj = common.tps_shooting_moves[0][1]
        initial_sample = paths.Sample(replica=0,
                                      trajectory=init_traj,
                                      ensemble=common.tps_ensemble)
        move = common.tps_shooting_moves[1]
        replica = move[0]
        trial_trajectory = move[4]
        shooting_point = initial_sample.trajectory[move[2]]
        accepted = move[3]
        direction = move[5]
        change = self.no_prejoin.move(initial_sample, trial_trajectory,
                                      shooting_point, accepted, direction)
        # assertions about the shape of the decision history
        assert_equal(change.mover, self.no_prejoin.mimic)
        assert_equal(change.subchange, change.canonical)
        assert_equal(change.subchange.subchange, None)
        assert_equal(len(change.trials), 1)
        # assertions true for any OneWayShooting
        # details0 = change.canonical.trials[0].details
        details0 = change.canonical.details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, True)
        assert_equal(type(change.canonical.mover), paths.ForwardShootMover)

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
        # details0 = change.canonical.trials[0].details
        details0 = change.canonical.details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, False)
        assert_equal(type(change.canonical.mover), paths.BackwardShootMover)

    def test_rejected_move_not_pre_joined(self):
        initial_sample = common.initial_tps_sample
        move = common.tps_shooting_moves[0]
        replica = move[0]
        trial_trajectory = move[4]
        shooting_point = initial_sample.trajectory[move[2]]
        accepted = False
        direction = move[5]
        change = self.no_prejoin.move(initial_sample, trial_trajectory,
                                      shooting_point, accepted, direction)
        # assertions about the shape of the decision history
        assert_equal(change.mover, self.no_prejoin.mimic)
        assert_equal(change.subchange, change.canonical)
        assert_equal(change.subchange.subchange, None)
        assert_equal(len(change.trials), 1)
        # assertions true for any OneWayShooting
        # details0 = change.canonical.trials[0].details
        details0 = change.canonical.details
        assert_equal(details0.shooting_snapshot, shooting_point)
        assert_equal(details0.initial_trajectory.index(shooting_point), move[2])
        # assertions specific to this test
        assert_equal(change.accepted, False)
        assert_equal(type(change.canonical.mover), paths.BackwardShootMover)

    @raises(RuntimeError)
    def test_no_overlap(self):
        initial_sample = common.initial_tps_sample
        move = common.tps_shooting_moves[-1]
        replica = move[0]
        trial_trajectory = move[1]
        shooting_point = initial_sample.trajectory[move[2]]
        accepted = True
        direction = move[5]

        change  = self.stub.move(initial_sample, trial_trajectory,
                                 shooting_point, accepted, direction)
