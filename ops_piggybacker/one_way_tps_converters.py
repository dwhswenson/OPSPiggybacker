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
3. If the input trajectories are full trajectories instead of only the
partial one-way trajectories for each move, then you need to provide an
addition element on each line (after ``accepted``) for the
``shooting_point_in_trial``, which is the index of the shooting point in the
trial trajectory.

Valid values for forward ``direction`` include ``+1``, ``1``, ``FW``,
``forward``, with backward given by ``-1``, ``BW``, or ``backward``.

Valid values for a trajectory that is ``accepted`` are ``T``, ``True``,
``1``, ``Y``, and ``Yes``. If the trajectory is not accepted, use ``F``,
``False``, ``0``, ``N``, or ``No``.

In general, we suggest the ``FW``/``BW`` pair for ``direction``, and
``True``/``False`` for ``accepted``. These tend to be most readable.
"""

import os
import openpathsampling as paths
import ops_piggybacker as oink
from openpathsampling.engines.openmm.tools import ops_load_trajectory

from collections import namedtuple

_tps_converter_option_list = ('trim trimmed_shooting auto_reverse '
                              + 'includes_shooting_point full_trajectory')


class TPSConverterOptions(namedtuple("TPSConverterOptions",
                                     _tps_converter_option_list)):
    """
    Parameters
    ----------
    trim : bool
        whether to trim the file trajectories to minimum acceptable
        length (default True)
    trimmed_shooting : bool
        whether the shooting point given is based on a trimmed trajectory
        (if the trajectory must be trimmed, but the shooting point frame
        number is from the untrimmed trajectory, this should be False.
        Default True)
    auto_reverse : bool
        whether to reverse backward trajectories (if the file version is
        forward, instead of backward, default False)
    includes_shooting_point : bool
        whether the one-way trial trajectory includes the shooting
        point, and therefore must have it trimmed off (default True)
    full_trajectory : bool
        whether the input trajectories are the full trajectories, instead of
        the partial one-way trajectories (default False). Note that if you
        use full_trajectory=True, you should also use trim=False; otherwise
        these options conflict with each other.
    """
    __slots__ = ()

    def __new__(cls, trim=True, trimmed_shooting=True, auto_reverse=False,
                includes_shooting_point=True, full_trajectory=False):
        return super(TPSConverterOptions, cls).__new__(
            cls, trim, trimmed_shooting, auto_reverse,
            includes_shooting_point, full_trajectory
        )


class OneWayTPSConverter(oink.ShootingPseudoSimulator):
    """
    Single-ensemble network shooting pseudo-simulator from external
    trajectories.

    This object handles a wide variety of external simulators. The idea is
    that the user must create a "simulation summary" file, which contains
    the information we need to perform the pseudo-simulation, where the
    trajectories are loaded via mdtraj.
    """
    def __init__(self, storage, initial_file, mover, network, options=None,
                 options_rejected=None):
        # TODO: mke the initial file into an initial trajectory
        if options is None:
            options = TPSConverterOptions()
        if options_rejected is None:
            options_rejected = options
        self.options = options
        self.options_rejected = options_rejected

        self.initial_file = initial_file  # needed for restore
        traj = self.load_trajectory(initial_file)
        # assume we're TPS here
        ensemble = network.sampling_ensembles[0]
        initial_trajectories = ensemble.split(traj)
        if len(initial_trajectories) == 0:  # pragma: no cover
            raise RuntimeError("Initial trajectory in " + str(initial_file)
                               + " has no subtrajectory satisfying the "
                               + "TPS ensemble.")
        elif len(initial_trajectories) > 1:  # pragma: no cover
            raise RuntimeWarning("More than one potential initial "
                                 + "subtrajectory. We use the first.")

        initial_trajectory = initial_trajectories[0]
        initial_conditions = paths.SampleSet([
            paths.Sample(replica=0,
                         trajectory=initial_trajectory,
                         ensemble=ensemble)
        ])
        self.summary_root_dir = None
        self.report_progress = None
        super(OneWayTPSConverter, self).__init__(
            storage=storage,
            initial_conditions=initial_conditions,
            mover=mover,
            network=network
        )

        # initial_states = self.network.initial_states
        # final_states = self.network.final_states
        # TODO: prefer the above, but the below work until fix for network
        # storage
        initial_states = [self.network.sampling_transitions[0].stateA]
        final_states = [self.network.sampling_transitions[0].stateB]

        all_states = paths.join_volumes(initial_states + final_states)

        self.fw_ensemble = paths.SequentialEnsemble([
            paths.AllOutXEnsemble(all_states),
            paths.AllInXEnsemble(all_states) & paths.LengthEnsemble(1)
        ])
        self.bw_ensemble = paths.SequentialEnsemble([
            paths.AllInXEnsemble(all_states) & paths.LengthEnsemble(1),
            paths.AllOutXEnsemble(all_states)
        ])
        self.full_ensemble = paths.SequentialEnsemble([
            paths.AllInXEnsemble(all_states) & paths.LengthEnsemble(1),
            paths.AllOutXEnsemble(all_states),
            paths.AllInXEnsemble(all_states) & paths.LengthEnsemble(1),
            paths.AllOutXEnsemble(all_states)
        ])

        self.extra_fw_frames = 0
        self.extra_bw_frames = 0

    def load_trajectory(self, file_name):
        raise NotImplementedError(
            "Can't instantiate abstract OneWayTPSConverter: Use a subclass"
        )

    @staticmethod
    def _get_direction(val):
        """Identifies the direction based on val"""
        is_forward = ['+1', '1', 'FW', 'F', 'FORWARD']
        is_backward = ['-1', 'BW', 'B', 'BACKWARD']
        if val.upper() in is_forward:
            return +1
        elif val.upper() in is_backward:
            return -1
        else:  # pragma: no cover
            raise ValueError("Unrecognized direction: " + str(val))

    @staticmethod
    def _get_accepted(val):
        is_true = ['1', 'T', 'TRUE', 'Y', 'YES', 'ACC']
        is_false = ['0', 'F', 'FALSE', 'N', 'NO', 'REJ']
        if val.upper() in is_true:
            return True
        elif val.upper() in is_false:
            return False
        else:  # pragma: no cover
            raise ValueError("Unknown truth value for acceptance: " +
                             str(val))

    def parse_summary_line(self, line):
        """Parse a line from the summary file.

        To control the parsing, set the OneWayTPSConverter.options (see
        :class:`.TPSConverterOptions`).

        Parameters
        ----------
        line : str
            the input line

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
        assert 4 <= len(splitted) <= 5, \
            "Incorrect number of fields in input: " + line

        replica = 0
        file_name = splitted[0]
        full_file_name = os.path.join(self.summary_root_dir, file_name)
        trajectory = self.load_trajectory(full_file_name)
        shooting_index = int(splitted[1])
        direction = self._get_direction(splitted[2])
        accepted = self._get_accepted(splitted[3])

        if accepted:
            options = self.options
        else:
            options = self.options_rejected

        # if reversed, make sure time is in the right direction
        if options.auto_reverse and direction < 0:
            trajectory = trajectory.reversed
        
        if not options.trimmed_shooting:
            if shooting_index >= 0:
                shooting_index += self.extra_bw_frames
            else:
                shooting_index -= self.extra_fw_frames

        # if reversed, make sure time is in the right direction
        # ensure the trajectory doesn't have extra frames
        if options.trim and not options.full_trajectory:
            len_pre_trim = len(trajectory)
            if direction > 0:
                trajectory = self.fw_ensemble.split(trajectory)[0]
            elif direction < 0:
                trajectory = self.bw_ensemble.split(trajectory)[-1]
                if accepted:
                    self.extra_bw_frames = len_pre_trim - len(trajectory)

        # if this is a full trajectory, cut it down to one-way segments
        if options.full_trajectory:
            shooting_index_in_trial = int(splitted[4])
            shoot_pt = 0 if options.includes_shooting_point else 1
            if direction > 0:
                trajectory = trajectory[shooting_index_in_trial+shoot_pt:]
            elif direction < 0:
                trajectory = trajectory[0:shooting_index_in_trial+1-shoot_pt]

        # remove shooting point from trial, if necessary
        if options.includes_shooting_point:
            if direction > 0:
                trajectory = trajectory[1:]
            else:
                trajectory = trajectory[:-1]

        return (replica, trajectory, shooting_index, accepted, direction)

    def run(self, summary_file_name, n_trajs_per_block=None):
        # this will basically create the move_info_list for part of the
        # summary_file, and then call super's RUN
        summary = open(summary_file_name, 'r')
        if self.summary_root_dir is None:
            self.summary_root_dir = os.path.dirname(summary_file_name)
        lines = [l for l in summary]
        n_steps = len(lines)

        if n_trajs_per_block is None:
            n_trajs_per_block = n_steps

        line_num = 0
        while line_num < n_steps:
            if self.report_progress is not None:
                self.report_progress.write("Working on MC step " +
                                           str(line_num) + "\n")
                self.report_progress.flush()

            end = min(line_num + n_trajs_per_block, n_steps)
            block = lines[line_num:end]
            moves = [self.parse_summary_line(l) for l in block]
            super(OneWayTPSConverter, self).run(moves)
            line_num += n_trajs_per_block


class GromacsOneWayTPSConverter(OneWayTPSConverter):
    def __init__(self, storage, network, initial_file, topology_file,
                 options=None, options_rejected=None):
        self.topology_file = topology_file
        mover = oink.ShootingStub(ensemble=network.sampling_ensembles[0],
                                  selector=paths.UniformSelector(),
                                  pre_joined=False)

        super(GromacsOneWayTPSConverter, self).__init__(
            storage=storage, network=network, initial_file=initial_file,
            mover=mover, options=options, options_rejected=None
        )

    def load_trajectory(self, file_name):
        """Creates an OPS trajectory from the given file"""
        return ops_load_trajectory(file_name, top=self.topology_file)
