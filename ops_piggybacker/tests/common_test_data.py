
import openpathsampling as paths
from openpathsampling.tests.test_helpers import make_1d_traj
import os

def xval(snap):
    return snap.coordinates[0][0]

cv = paths.FunctionCV("x", xval)
left = paths.CVDefinedVolume(cv, float("-inf"), 0.0).named("left")
right = paths.CVDefinedVolume(cv, 10.0, float("inf")).named("right")

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

    # replica, full trial, shooting idx, one-way trial, direction
    moves = [
        (0, out1, 4, True, t1, -1),
        (0, out2, 2, True, t2, +1),
        (0, out3, 5, False, t3, -1),
        (0, out4, 4, True, t4, -1)
    ]
    initial_sample = paths.Sample(replica=0,
                                  trajectory=t0,
                                  ensemble=tps_ensemble)
    return initial_sample, moves


initial_tps_sample, tps_shooting_moves = shooting_move_info()

template = initial_tps_sample.trajectory[0]

if __name__ == "__main__":
    # can't seem to use pkg_resources.resource_filename here
    my_directory = os.path.dirname(__file__)
    tps_setup_filename = os.path.join(my_directory, "test_data",
                                      "tps_setup.nc")
    print "Putting TPS setup in:", tps_setup_filename
    # note that this assumes that this is the installed package location
    # (if this file is run from another copy, then there are two test_data/
    # directories to worry about here!)
    tps_storage = paths.Storage(tps_setup_filename, "w", template)
    tps_storage.save(tps_network)
    tps_storage.save(template)
    tps_storage.sync()
    tps_storage.close()
