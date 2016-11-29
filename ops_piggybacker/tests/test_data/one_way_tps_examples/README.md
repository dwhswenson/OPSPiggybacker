This directory contains test data for the `one_way_tps` object.

There are several ways of setting that object up, so there are several
copies of simple toy data.

Each test is essentially the same, and consists of 5 trajectories plus a
`summary` file, which provides the overview of the simulation. The files
with no suffix are intended for the standard simulation, with no trimming.
The files with the `_extra` suffix are intended for the case that there are
frames to trim. The files with the `_full` suffic are intended for the case
that the input trajectories include the full trajectory, not just the
one-way part.
