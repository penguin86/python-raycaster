# Python raycaster

A simple [raycasting engine](https://en.wikipedia.org/wiki/Ray_casting), like the one used for [Wolfenstein 3D](https://en.wikipedia.org/wiki/Wolfenstein_3D), written in Python using the [SDL graphics library](https://en.wikipedia.org/wiki/Simple_DirectMedia_Layer).
Inspired by [this video of 3DSage](https://www.youtube.com/watch?v=gYRrGTC7GtA)

## Requirements
Install SDL libs for Python and PNG lib (required for texture loading):
```
pip install pysdl2 pysdl2-dll pypng
```

## Run
Run with
```
./raycaster.py
```

## Context
Being this an educational project (done to teach myself SDL and how a raycasting engine works), the performances are pretty bad. The code is written to be documental, more than efficient. I decided to keep the various milestones in different folders (v1, v2, v3...) instead of relying on git versioning to allow easier compare between different milestones.

## License
Copyright (C) 2023 Daniele Verducci

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
