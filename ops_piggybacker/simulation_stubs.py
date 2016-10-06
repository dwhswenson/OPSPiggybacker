import openpathsampling as paths

class ShootingPseudoSimulator(paths.PathSimulator):
    """Pseudo-simulator for shooting-only mimics.

    Parameters
    ----------
    storage : openpathsampling.netcdfplus.Storage
        file to store OPS-ready analysis
    initial_conditions : openpathsampling.SampleSet
        sample set giving the OPS version of the initial conditions
    mover : ShootingStub
        stub to mimic the shooting mover
    network : openpathsampling.TransitionNetwork
        transition network with information about this system
    """
    def __init__(self, storage, initial_conditions, mover, network):
        super(ShootingPseudoSimulator, self).__init__(storage)
        self.scheme = paths.LockedMoveScheme(mover, network)
        self.scheme.movers = {'shooting': [mover.mimic]}
        self.scheme.choice_probability = {mover.mimic: 1.0}
        self.scheme._real_choice_probability = {mover.mimic: 1.0}
        self.mover = mover
        self.sample_set = initial_conditions
        self.initial_conditions = initial_conditions
        self.network = network
        self.root_mover = self.scheme.move_decision_tree()
        self._path_sim_mover = paths.PathSimulatorMover(mover.mimic, self)


    def run(self, step_info_list):
        """
        Parameters
        ----------
        step_info_list : list of tuple
            (replica, trial_trajectory, shooting_point_index, accepted) or
            (replica, one_way_trial_segment, shooting_point_index, accepted,
            direction)
        """
        mcstep = None

        if self.step == 0:
            if self.storage is not None:
                self.storage.save(self.scheme)
            self.save_initial()

        for step_info in step_info_list:
            self.step += 1
            if len(step_info) == 4 and not self.mover.pre_joined: # pragma: no-cover
                raise RuntimeError(
                    "Shooting trial trajectories not pre-joined: " + 
                    "step_info must be (replica, trial_segment, " + 
                    "shooting_pt_idx, accepted, direction)")
            
            replica = step_info[0]
            trial_trajectory = step_info[1]
            shooting_point_index = step_info[2]
            accepted = step_info[3]
            direction = None
            if len(step_info) == 5:
                direction = step_info[4]

            input_sample = self.sample_set[replica]

            if shooting_point_index < 0:
                shooting_point_index +=len(input_sample.trajectory)

            shooting_point = input_sample.trajectory[shooting_point_index]


            subchange = self.mover.move(input_sample, trial_trajectory,
                                        shooting_point, accepted, direction)

            change = paths.PathSimulatorMoveChange(
                subchange=subchange,
                mover=self._path_sim_mover,
                details=paths.MoveDetails(step=self.step)
            )
            samples = change.results
            new_sampleset = self.sample_set.apply_samples(samples)
            mcstep = paths.MCStep(
                simulation=self,
                mccycle=self.step,
                previous=self.sample_set,
                active=new_sampleset,
                change=change
            )

            if self.storage is not None:
                self.storage.steps.save(mcstep)
            if self.step % self.save_frequency == 0:
                self.sample_set.sanity_check()
                self.sync_storage()

            self.sample_set = new_sampleset

        self.sync_storage()
