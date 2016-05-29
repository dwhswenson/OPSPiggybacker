import openpathsampling as paths

class ShootingPseudoSimulator(paths.PathSimulator):
    def __init__(self, storage, initial_conditions, mover, network):
        super(ShootingPseudoSimulator, self).__init__(storage)
        self.scheme = paths.LockedMoveScheme(mover, network)
        self.scheme.movers = {'shooting': [mover.mimic]}
        self.scheme.choice_probability = {mover.mimic: 1.0}
        self.mover = mover
        self.globalstate = initial_conditions
        self.initial_conditions = initial_conditions
        self.network = network
        self.root_mover = self.scheme.move_decision_tree()
        self._path_sim_mover = paths.PathSimulatorMover(mover.mimic, self)


    def run(self, step_info_list):
        """
        Parameters
        ----------
        step_info_list : list of tuple
            (replica, trial_trajectory, shooting_point_index, accepted)
        """
        mcstep = None

        if self.step == 0:
            if self.storage is not None:
                self.storage.save(self.scheme)
            self.save_initial()

        for step_info in step_info_list:
            self.step += 1
            
            replica = step_info[0]
            trial_trajectory = step_info[1]
            shooting_point_index = step_info[2]
            accepted = step_info[3]

            input_sample = self.globalstate[replica]
            shooting_point = input_sample.trajectory[shooting_point_index]

            subchange = self.mover.move(input_sample, trial_trajectory,
                                        shooting_point, accepted)

            change = paths.PathSimulatorPathMoveChange(
                subchange=subchange,
                mover=self._path_sim_mover,
                details=paths.MoveDetails(step=self.step)
            )
            samples = change.results
            new_sampleset = self.globalstate.apply_samples(samples)
            mcstep = paths.MCStep(
                simulation=self,
                mccycle=self.step,
                previous=self.globalstate,
                active=new_sampleset,
                change=change
            )

            if self.storage is not None:
                self.storage.steps.save(mcstep)
            if self.step % self.save_frequency == 0:
                self.globalstate.sanity_check()
                self.sync_storage()

            self.globalstate = new_sampleset

        self.sync_storage
