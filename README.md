Bazel Project Creator
---------

A python3 script that realizes easy creation of bazel projects
for embedded c. Run
```
$ curl https://raw.githubusercontent.com/es-ude/BazelCProjectCreator/master/create_bazel_project.py \
  | python - MyProject
```
or for systems mainly using python2 you need to explicitly choose python3 with 
```
$ curl https://raw.githubusercontent.com/es-ude/BazelCProjectCreator/master/create_bazel_project.py \
  | python3 - MyProject
```
to create a the new project `MyProject`.

**Please note that** the project name must not contain dashes, dots or spaces since the bazel synchronization will fail in that case. Illegal characters will be replaced by an underscore. For more information about workspace names klick [here](https://docs.bazel.build/versions/master/be/functions.html#workspace).

If the folder `MyProject` already contains files, the script will fail,
to prevent accidentally overwriting files.
For more information on the Bazel Build Tool see https://bazel.build.
For more information on the Bazel Scripts used in the created project see https://embeddedsystemsbuildscripts.readthedocs.io/en/latest/.

For a list of available targets run
```
$ bazel query //...
```

The project will contain the following directory hierarchy
```
Project/
  app/
  | setup/
  docs/
  Project/
  src/
  test/
```
Each directory serves a specific purpose.
The role of your source files will depend on where
you put them.
The main principle here is keep your code in separate
parts as follows
  * library: with public headers in `Project` and all other files in `src`
  * documentation: in `docs`
  * applications: every file in `app` represents an executable application,
    the `setup` folder for initialization routines that shall be shared between
    applications.
  * tests: unit tests go into the `test` folder

### Applications

All files in `app/` are expected to be `*.c` files
containing a `main` function. Each file will
correspond to a buildable `cc_binary` target.
Assuming you created the file `app/main.c` you can run
```
$ bazel build app:main --platforms @AvrToolchain//platforms:ElasticNode_v3
```
to build a `.hex` file for the [elastic node platform](https://github.com/es-ude?utf8=%E2%9C%93&q=ElasticNode&type=&language=). The file will be located at
```
bazel-bin/app/main.hex
```

You can see a list of available platforms
by running
```
$ bazel query 'kind(platform, @AvrToolchain//platforms:*)'
```
or define your own platform (see [here](https://embeddedsystemsbuildscripts.readthedocs.io/en/latest/Platforms.html))

A target can be flashed by using the `bazel run` command. In order to do that, you need to append _\_upload_ to the target name. The end of the command requires a positional argument, that specifies the port of the programmer, i.e.
```
$ bazel run app:main_upload --platforms @AvrToolchain//platforms:ElasticNode_v4 -- /dev/ttyACM0
```
More information regarding that, can be found [here](https://github.com/es-ude/EmbeddedSystemsBuildScripts#AvrToolchain).

### Documentation
To help you getting started with the documentation for your new project,
we include setup files for [Sphinx](http://www.sphinx-doc.org/en/master/).
The documentation files are written using reStructuredText.
For an overview of the markup we recommend the [reStructuredText Primer](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html).

To allow including information from doxygen comments in your header files we
use the [breathe plugin](https://breathe.readthedocs.io/en/latest/).
E.g. use
```
... doxygenfile: YourHeader.h
```
to include the doxygen output of `YourHeader.h` into your documentation.
More available commands can be found at https://breathe.readthedocs.io/en/latest/directives.html.

To build the documentation run
```
$ sphinx-build -T -b html docs docs/_build
```
from your workspace root. The output can then be found at `docs/_build/`.

### Prerequisites

* Linux or MacOS
* gcc or clang
* bazel >= 0.25
* avr-gcc
* avr-binutils
* avr-libc
* dfu-programmer

For automated test runner
generation
* ruby

For documentation
* doxygen
* Sphinx
* breathe (sphinx plugin)
