exclude - C++ unused includes removal tool
==========================================

Removes unused includes in C++ code. The script performs these tasks:
- For each include line:
  - Remove the include line
  - Compile (no link) the associated VS project
  - If compilation fails, put the include line back

It can run against an entire code folder or against a single C++ file.

By default, includes that seem used in the current file are not removed. This is done by searching for the include name (without ".h" in the file). For example:

```cpp
#include "Player.h"
#include "Game.h" // this also includes Player.h

CPlayer* player = players[i]; // "Player" found in "CPlayer", include of Player.h not removed
```

Sometimes, an include can actually be removed because it is included by another header. But there can be reasons to want to keep the include anyway (to prevent potential future build break, to avoid breaking different platforms or configs, to be explicit).

This can be turned off with the switch -u or --unsafe.

Tested with python 2.7.2 against VS 2010 projects.

## Usage

```
exclude.py "D:\path\to\code" --projectconfig "Release" --projectplatform "Win32" --projectpath "D:\path\to\code\foo\foo.vcxproj" --file foo.cpp

D:\path\to\code\foo\foo.cpp
Trying to remove bar.h
Trying to remove baz.h
  > Removed baz.h
Trying to remove xyz.h
  > Removed xyz.h

Removed includes in foo.cpp
baz.h
xyz.h
```

```
exclude.py -h
usage: exclude.py [-h] [-d] [-u] [-pc PROJECTCONFIG] [-pp PROJECTPLATFORM]
                  [-pa PROJECTPATH] [-sp SOLUTIONPATH] [-bc BUILDCONFIG]
                  [-bp BUILDPROJECT] [-f FILE]
                  projectcodepath

Unused includes removal tool

positional arguments:
  projectcodepath       Path to the project's code

optional arguments:
  -h, --help            show this help message and exit
  -d, --devenv          Uses devenv instead of msbuild if specified
  -u, --unsafe          Do not keep includes whose name is referenced in code
  -pc PROJECTCONFIG, --projectconfig PROJECTCONFIG
                        Project configuration, must be specified if using
                        msbuild
  -pp PROJECTPLATFORM, --projectplatform PROJECTPLATFORM
                        Project platform, must be specified if using msbuild
  -pa PROJECTPATH, --projectpath PROJECTPATH
                        Path to vcxproj, must be specified if using msbuild
  -sp SOLUTIONPATH, --solutionpath SOLUTIONPATH
                        Path to sln, must be specified if using devenv
  -bc BUILDCONFIG, --buildconfig BUILDCONFIG
                        Build configuration, must be specified if using devenv
  -bp BUILDPROJECT, --buildproject BUILDPROJECT
                        Build project, must be specified if using devenv
  -f FILE, --file FILE  Run only on the specified file

msbuild example:
exclude.py "D:\path\to\code" -pc "Release" -pp "Win32" -pa "D:\path\to\code\foo\
foo.vcxproj"

devenv example:
exclude.py "D:\path\to\code" -d -sp "D:\path\to\code\my.sln" -bc "Release|Win32"
 -bp "Foo"
```

## ISC License

https://github.com/shazbits/mtwr/blob/master/LICENSE.txt

Romain Dura

http://www.shazbits.com
