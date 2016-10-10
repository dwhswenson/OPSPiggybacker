import openpathsampling as paths
import sys
def make_tipsi_dat(trajfile, top, stateA, stateB, cvs, start_time=0.0,
                   dt=1.0, frame_size=0.0, output=None):
    ensemble = paths.AllOutXEnsemble(stateA) | paths.AllOutXEnsemble(stateB)
    if output is None:
        output = sys.stdout
    traj = ops_load(trajfile, top=top)
    time = start_time
    frame = 0
    for i in range(len(traj)):
        snap = traj[i]
        state = "I"
        if stateA(snap):
            state = "A"
        elif stateB(snap):
            state = "B"
        stop = not ensemble(traj[:i+1])
        cv_str = "\t".join([str(cv(snap)[0]) for cv in cvs])
        out_str = (state + "\t" + str(time) + "\t" + str(stop) + "\t" 
                   + "../../" + trajfile + "\t" + str(frame) + "\t" 
                   + cv_str + "\n")
        output.write(out_str)
        output.flush()
        time += dt
        frame += frame_size

