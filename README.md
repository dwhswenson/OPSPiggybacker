# OPSPiggybackers

The goal of this little toy project is to create an OPS mover that creates
fake shooting moves. This could be useful either for testing, or for mapping
output from another software package into formats that OPS can analyze.

The approach we use is to create a generic mover, which pretends to be a
one-way shooting mover. Note that we can always add additional fake moves in
a similar way: fake replica exchange, fake minus, etc.

One of the tricky bits is that it is possible that not all the information
will be available. Of particular note, we might have a system that doesn't
save all its frames. Figuring out how to handle that will be more difficult.


## Installation

### Simple installation

(TODO: this is whatever the ECAM preferred approach is)

### Developer installation

If you intend to develop, or stay up to date with the bleeding edge of
development, you'll want to install 

1. Install [OpenPathSampling](http://openpathsampling.org/). All other
   required packaged for `OPSPiggybacker` are also required packages for OPS.
2. Clone this git repository.
3. Change to the root directory of your clone, and use `python setup.py
   develop` or `pip install -e .`. You may need to preface that with `sudo`.

