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

    def test_backward_move(self):
        initial_sample = common.initial_tps_sample
        move = common.tps_shooting_moves[0]
        replica = move[0]
        trial_trajectory = move[1]
        shooting_point = move[2]
        accepted = move[3]
        self.stub.move(initial_sample, trial_trajectory, shooting_point,
                       accepted)
        # TODO: check the return value in detail
        raise SkipTest

    def test_forward_move(self):
        init_traj = common.tps_shooting_moves[0][1]
        initial_sample = paths.Sample(replica=0,
                                      trajectory=init_traj,
                                      ensemble=common.tps_ensemble)
        move = common.tps_shooting_moves[1]
        replica = move[0]
        trial_trajectory = move[1]
        shooting_point = move[2]
        accepted = move[3]
        self.stub.move(initial_sample, trial_trajectory, shooting_point,
                       accepted)
        # TODO: check the return value in detail
        raise SkipTest

    def test_rejected_move(self):
        init_traj = common.tps_shooting_moves[1][1]
        initial_sample = paths.Sample(replica=0,
                                      trajectory=init_traj,
                                      ensemble=common.tps_ensemble)
        move = common.tps_shooting_moves[2]
        replica = move[0]
        trial_trajectory = move[1]
        shooting_point = move[2]
        accepted = move[3]
        self.stub.move(initial_sample, trial_trajectory, shooting_point,
                       accepted)
        # TODO: check the return value in detail
        raise SkipTest
