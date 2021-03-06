[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a9fcd475b5694d839e0facc593fe6ffa)](https://www.codacy.com/app/dwhswenson/OPSPiggybacker?utm_source=github.com&utm_medium=referral&utm_content=dwhswenson/OPSPiggybacker&utm_campaign=badger)
[![Build Status](https://travis-ci.org/dwhswenson/OPSPiggybacker.svg?branch=master)](https://travis-ci.org/dwhswenson/OPSPiggybacker)
[![Coverage Status](https://coveralls.io/repos/github/dwhswenson/OPSPiggybacker/badge.svg?branch=master)](https://coveralls.io/github/dwhswenson/OPSPiggybacker?branch=master)
[![Documentation Status](https://readthedocs.org/projects/opspiggybacker/badge/?version=latest)](http://opspiggybacker.readthedocs.io/en/latest/?badge=latest)


# OPSPiggybackers

The goal of this little toy project is to create an OPS mover that creates
a fake simulation with predetermined move behavior (what trial trajectories
are generated; whether they are accepted). This could be useful either for
testing, or for mapping output from another software package into formats
that OPS can analyze.

The approach we use is to create a generic mover, which pretends to be a
one-way shooting mover. Note that we can always add additional fake moves in
a similar way: fake replica exchange, fake minus, etc. However, that
requires a little more generalization.

One of the tricky bits is that it is possible that not all the information
will be available. Of particular note, we might have a system that doesn't
save all its frames. Figuring out how to handle that will be more difficult.


## Installation

### Simple installation

(TODO: this is whatever the E-CAM preferred approach is)

### Developer installation

If you intend to develop, or stay up to date with the bleeding edge of
development, you should use the following installation procedure:

1. Install [OpenPathSampling](http://openpathsampling.org/). All other
   required packages for `OPSPiggybacker` are also required packages for OPS.
2. Clone this git repository.
3. Change to the root directory of your clone, and use `python setup.py
   develop` or `pip install -e .`. You may need to preface that with `sudo`.

## Roadmap

Current release: `0.1.0`

Roadmap:

* `0.1`: Support for shooting moves with only one ensemble (e.g., TPS)
* Coming soon: Support for shooting moves with multiple ensembles (e.g.,
  TIS)
* Coming later: Generalize mover input to handle arbitrary moves (not just
  shooting)

