Bazel Project Creator
---------

A python3 program that realizes easy creation of bazel projects
for embedded c. Run
```
$ wget https://raw.githubusercontent.com/es-ude/BazelCProjectCreator/master/create_bazel_project.py \
  && ./create_bazel_project.py path/to/my/Project
```
to create a new Project.

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
