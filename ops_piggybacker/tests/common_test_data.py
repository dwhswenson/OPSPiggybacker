
import openpathsampling as paths
from openpathsampling.tests.test_helpers import make_1d_traj
import os

def xval(snap):
    return snap.coordinates[0][0]

cv = paths.CV_Function("x", xval)
left = paths.CVRangeVolume(cv, float("-inf"), 0.0).named("left")
right = paths.CVRangeVolume(cv, 10.0, float("inf")).named("right")

tps_network = paths.TPSNetwork(left, right)
tps_ensemble = tps_network.sampling_ensembles[0]


def shooting_move_info():
    t0 = make_1d_traj([-0.1, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.1])
    t1 = make_1d_traj([-0.11, 2.1])
    t2 = make_1d_traj([5.2, 7.2, 9.2, 10.12])
    t3 = make_1d_traj([-0.13, 2.3, 5.3, 8.3])
    t4 = make_1d_traj([-0.14, 2.4, 4.4, 6.4])

    out1 = paths.Trajectory(t1 + t0[4:])
    out2 = paths.Trajectory(out1[0:3] + t2)
    out3 = paths.Trajectory(t3 + out2[5:])  # REJECT THIS
    out4 = paths.Trajectory(t4 + out2[4:])

    # for traj in [t0, out1, out2, out3, out4]:
        # print [s.xyz[0][0] for s in traj]

    moves = [
        (0, out1, 4, True),
        (0, out2, 2, True),
        (0, out3, 5, False),
        (0, out4, 4, True)
    ]
    initial_sample = paths.Sample(replica=0,
                                  trajectory=t0,
                                  ensemble=tps_ensemble)
    return initial_sample, moves


initial_tps_sample, tps_shooting_moves = shooting_move_info()

template = initial_tps_sample.trajectory[0]
