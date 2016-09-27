"""
Conversion helpers for one-way TPS simulations

These classes are used to make it very easy to convert from existing one-way
TPS simulations. They require the user to do the following:

1. Create an OPS network representing their TPS simulation.
2. Create a summary file, which consists of one line per MC step, where each
line is the space-separated ``file_name shooting_point direction accepted``,
where ``file_name`` is the name of the file for the partial trajectory,
``shooting_point`` is the index of the shooting point from (from zero) in
the *previous* trajectory, ``direction`` tells whether this was a forward
or backward shot, and ``accepted`` tells whether the path was accepted.
Valid values for forward ``direction`` include ``+1``, ``1``, ``FW``,
``forward``, with backward given by ``-1``, ``BW``, or ``backward``. Valid
values for a trajectory that is ``accepted`` are ``T``, ``True``, ``1``,
``Y``, and ``Yes``. If the trajectory is not accepted, use ``F``, ``False``,
``0``, ``N``, or ``No``.

In general, we suggest the ``FW``/``BW`` pair for ``direction``, and
``True``/``False`` for ``accepted``. These tend to be most readable.
"""


import mdtraj as md
import ops_piggybacker as oink
from openpathsampling.engines.openmm import trajectory_from_mdtraj

class OneWayTPSConverter(oink.ShootingPseudoSimulator):
    """
    Single-ensemble network shooting pseudo-simulator from external
    trajectories.
    
    This object handles a wide variety of external simulators. The idea is
    that the user must create a "simulation summary" file, which contains
    the information we need to perform the pseudo-simulation, where the
    trajectories are loaded via mdtraj.

    """
    def __init__(self, storage, network, initial_file):
        # TODO: mke the initial file into an initial trajectory
        traj = self.load_trajectory(initial_file)
        # assume we're TPS here
        ensemble = network.ensembles[0]
        initial_trajectories = ensemble.split(traj)
        if len(initial_trajectories) == 0:
            raise RuntimeError("Initial trajectory in " + str(initial_file)
                               + " has no subtrajectory satisfying the "
                               + "TPS ensemble.")
        elif len(initial_trajectories) > 1:
            raise RuntimeWarning("More than one potential initial "
                                 + "subtrajectory. We use the first.")
        else:
            initial_trajectory = initial_trajectories[0]

    def load_trajectory(self, file_name):
        # TODO: implement some simple toy for testing
        return file_name

    def _get_direction(val):
        """Identifies the direction based on val"""
        is_forward = ['+1', '1', 'FW', 'F', 'FORWARD']
        is_backward = ['-1', 'BW', 'B', 'BACKWARD']
        if val.upper() in is_forward:
            return +1
        elif val.upper() in is_backward:
            return -1
        else:
            raise ValueError("Unrecognized direction: " + str(val))

    def _get_accepted(val):
        is_true = ['1', 'T', 'TRUE', 'Y', 'YES']
        is_false = ['0', 'F', 'FALSE', 'N', 'NO']
        if val.upper() in is_true:
            return True
        elif val.upper() in is_false:
            return False
        else:
            raise ValueError("Unknown truth value for acceptance: " +
                             str(val))

    def parse_summary_line(self, line, trim=True, auto_reverse=False,
                           includes_shooting_point=True):
        """Parse a line from the summary file.

        Parameters
        ----------
        line : str
            the input line
        trim : bool
            whether to trim the file trajectories to minimum acceptable
            length (default True)
        auto_reverse : bool
            whether to reverse backward trajectories (if the file version is
            forward, instead of backward, default False)
        includes_shooting_point : bool
            whether the one-way trial trajectory includes the shooting
            point, and therefore must have it trimmed off (default True)

        Returns
        -------
        replica : 0
            always zero for now
        trial_trajectory : openpathsampling.Trajectory
            one-way trial segments
        shooting_point_index : int
            index of the shooting point based on the previous trajectory
            (None if no previous trajectory)
        accepted : bool
            whether the trial was accepted
        direction : 1 or -1
            positive if forward shooting, negative if backward
        """
        splitted = line.split()
        assert len(splitted) == 4, \
                "Incorrect number of fields in input: " + line

        replica = 0
        file_name = splitted[0]
        trajectory = self.load_trajectory(file_name)
        shooting_index = int(splitted[1])
        direction = self._get_direction(splitted[2])
        accepted = self._get_accepted(splitted[3])

        # ensure the trajectory doesn't have extra frames
        if trim:
            ensemble = self.network.ensembles[0]  # assume TPS
            trajectory = ensemble.split(trajectory)[0]
        
        # if reversed, make sure time is in the right direction
        if auto_reverse and direction < 0:
            trajectory = trajectory.reversed()

        # remove shooting point from trial, if necessary
        if includes_shooting_point:
            if direction > 0:
                trajectory = trajectory[1:]
            else:
                trajectory = trajectory[:-1]
        
        return (replica, trajectory, shooting_index, direction, accepted)

    def run(self, summary_file):
        # this will basically create the move_info_list for part of the
        # summary_file, and then call super's RUN
        pass


class GromacsOneWayTPSConverter(OneWayTPSConverter):
    def __init__(self, storage, network, initial_file, topology_file):
        self.topology_file = topology_file
        super(GromacsOneWayTPSConverter, self).__init__(
            storage=storage, network=network, initial_file=initial_file
        )

    def load_trajectory(self, file_name):
        """Creates an OPS trajectory from the given file"""
        return trajectory_from_mdtraj(md.load(file_name, self.topology_file))



