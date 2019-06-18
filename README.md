Bazel Project Creator
---------

A python3 script that realizes easy creation of bazel projects
for embedded c. Run
```
$ wget https://raw.githubusercontent.com/es-ude/BazelCProjectCreator/master/create_bazel_project.py \
  && chmod +x && ./create_bazel_project.py path/to/my/Project
```
to create a new project.
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
or define your own platform (see [here](https://embeddedsystemsbuildscripts.readthedocs.io/en/latest/Platforms.html)

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
