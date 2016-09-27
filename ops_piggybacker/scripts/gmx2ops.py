#!/usr/bin/env python

def build_parser():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--top", "-t", type=str, 
                        help="Gromacs topology file")
    parser.add_argument("--initial", "-i", type=str, 
                        help=("File for initial trajectory. " 
                              + "If not provided, simulation summary file "
                              + "must begin with full initial trajectory. "
                              + "Other information on that line is ignored."))
    parser.add_argument("--output", "-o", type=str,
                        help="Output file. If not provided, use the input nc")
    parser.add_argument("--nc", type=str,
                        help="Input NetCDF file containing OPS objects")
    summary_file_help = """
    Simulation summary file. Format is one MC step per line, with the
    following space-separated fields: `trajectory_file shooting_index
    direction accepted`, where trajectory_file is a file name,
    shooting_index is the index of the shooting point in the *previous*
    trajectory, direction is either +1/-1 or "FW/BW" (forward/backward) and
    accepted is "T/F" or "True/False" or "1/0"."""
    parser.add_argument("summary_file", type=str, help=summary_file_help)
    return parser


if __name__ == "__main__":
    parser = build_parser()
    parser.parse_args()
