#!/usr/bin/env python

import os
import os.path
import sys

def create_bazel_project(project_root):
    name = os.path.basename(project_root)

    def create_file(path, content):
        full_path = os.path.abspath(os.path.join(project_root, path))
        print(full_path)
        dir = os.path.dirname(full_path)
        if os.path.isfile(full_path):
            raise FileExistsError(full_path)
        os.makedirs(dir, exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(content)

    def create_package(path, build_file_content):
        build_file_path = os.path.join(path, "BUILD.bazel")
        create_file(build_file_path, build_file_content)

    create_file("WORKSPACE",
                """workspace(
    name = "{project_name}"
)

load("//:github.bzl", "es_github_archive")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

es_github_archive(
    name = "EmbeddedSystemsBuildScripts",
    version = "0.5.3",
   # sha256 = "<checksum>"
)

load("@EmbeddedSystemsBuildScripts//AvrToolchain:avr.bzl", "avr_toolchain")

avr_toolchain()

http_archive(
    name = "Unity",
    build_file = "@EmbeddedSystemsBuildScripts//:BUILD.Unity",
    strip_prefix = "Unity-master",
    urls = ["https://github.com/ThrowTheSwitch/Unity/archive/master.tar.gz"],
    sha256 = "2757ff718ef4c507a7c294f62bfd8d63a780b9122840c9b28ca376784f3baa6e"
)

http_archive(
    name = "CException",
    build_file = "@EmbeddedSystemsBuildScripts//:BUILD.CException",
    strip_prefix = "CException-master",
    urls = ["https://github.com/ThrowTheSwitch/CException/archive/master.tar.gz"],
)

http_archive(
    name = "CMock",
    build_file = "@EmbeddedSystemsBuildScripts//:BUILD.CMock",
    strip_prefix = "CMock-master",
    urls = ["https://github.com/ThrowTheSwitch/CMock/archive/master.tar.gz"],
)

#http_archive(
#    name = "LUFA",
#    build_file = "@EmbeddedSystemsBuildScripts//:BUILD.LUFA",
#    strip_prefix = "lufa-LUFA-170418",
#    urls = ["http://fourwalledcubicle.com/files/LUFA/LUFA-170418.zip"],
#)
""".format(project_name=name))

    create_package("app/setup",
                   """load("@AvrToolchain//platforms/cpu_frequency:cpu_frequency.bzl", "cpu_frequency_flag")

cc_library(
    name = "Setup",
    srcs = glob(["*.c"]),
    hdrs = glob(["*.h"]),
    deps = ["//:Library"],
    visibility = ["//visibility:public"],
)
""")

    create_package("app",
                   """load("@AvrToolchain//:helpers.bzl", "default_embedded_binaries")
load("@AvrToolchain//platforms/cpu_frequency:cpu_frequency.bzl", "cpu_frequency_flag")

default_embedded_binaries(
    main_files = glob(["*.c"]),
    copts = cpu_frequency_flag(),
    deps = [
        "//app/setup:Setup",
        "//:Library"
        ],
)
""")
    create_file("app/main.c",
    		"""#include <avr/io.h>
#include <util/delay.h>
#include <stdbool.h>

int
main(void)
{
  DDRD = _BV(5);
  while (true)
  {
    _delay_ms(500);
    PORTB ^= _BV(5);
  }
}""")
    create_package(name,
                   """cc_library(
   name = "HdrOnlyLib",
   hdrs = glob(["**/*.h"]),
   visibility = ["//visibility:public"],
)
""")

    create_package("",
                   """cc_library(
    name = "Library",
    srcs = glob(["src/**/*.c", "src/**/*.h"]),
    visibility = ["//visibility:public"],
    deps = [
        "//{}:HdrOnlyLib"
    ]
)
""".format(name))

    create_package("test",
                   """load("@EmbeddedSystemsBuildScripts//Unity:unity.bzl", "generate_a_unity_test_for_every_file", "unity_test")

generate_a_unity_test_for_every_file(
    cexception = False,
    file_list = glob(["*_Test.c"]),
    deps = [
        "//:Library",
    ],
)
""")
    create_file("test/first_Test.c",
                """#include "unity.h"

void 
test_shouldFail(void)
{
   TEST_FAIL();
}
""")
    create_file("github.bzl",
    		"""load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

URL = "https://github.com/es-ude/{repo}/archive/v{version}.tar.gz"

def es_github_archive(name, version, repo = "",  **kwargs):
  '''Convenient wrapper for embedded systems department
     open source projects. It assumes version tags
     are prefixed with the letter 'v'.'''
  if repo == "":
      repo = name
  http_archive(
    name = name,
    strip_prefix = "{}-{}".format(name, version),
    urls = [URL.format(repo = repo, version = version)],
    **kwargs
  )
""")

    create_file(".bazelrc",
                """test --test_output=errors
build --incompatible_enable_cc_toolchain_resolution=true
try-import user.bazelrc
""")
    create_file(".gitignore",
	            """.vscode/
.clwb/
bazel-*
user.bazelrc
""")
    create_file("docs/conf.py",
       """
# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import subprocess, sys


def run_doxygen(file):
    # Run the doxygen make command in the designated folder
    filedir = os.path.dirname(file)
    try:
        retcode = subprocess.call("sed -e \\"s:@@OUTPUT_DIRECTORY@@:{{}}:\\" <{{}} | doxygen -".format(filedir, file), shell=True)
        if retcode < 0:
            sys.stderr.write("doxygen terminated by signal %s" % (-retcode))
    except OSError as e:
        sys.stderr.write("doxygen execution failed: %s" % e)


# read_the_docs_build = os.environ.get('READTHEDOCS', None) == 'True'

# if read_the_docs_build:
#     run_doxygen("./doxy.conf")

run_doxygen("./doxy.conf")
# def generate_doxygen_xml(app):
#     #Run the doxygen make commands if we're on the ReadTheDocs server
#
#     read_the_docs_build = os.environ.get('READTHEDOCS', None) == 'True'
#
#     if read_the_docs_build:
#
#         run_doxygen("./doxy.conf")

# def setup(app):
#
#     # Add hook for building doxygen xml when needed
#     app.connect("builder-inited", generate_doxygen_xml)

# -- Project information -----------------------------------------------------

project = '{project}'
copyright = ''
author = ''

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = 'v0.3'


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '2.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.intersphinx',
#	'sphinx.ext.pngmath',
	'sphinx.ext.todo',
	'breathe'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = ['.rst', '.md']
#source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {{}}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {{}}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'HtmlHelpdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {{
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}}

# --- Breathe ----


breathe_projects = {{"EmbeddedUtil": "xml/"}}
breathe_default_project = "EmbeddedUtil"

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {{'https://docs.python.org/': None}}
""".format(project = name))
    create_file("docs/requirements.txt",
    """Sphinx >= 2.0
breathe
""")
    create_file("docs/doxy.conf",
	"""INPUT = ../{headers}/
GENERATE_XML = YES
GENERATE_LATEX = NO
GENERATE_HTML = NO
XML_OUTPUT = @@OUTPUT_DIRECTORY@@/xml
""".format(headers = name))
    create_file("docs/index.rst", "**{}**".format(name))
    print("""
Run
 $ bazel query //...
from the new project's root directory
to see a list of available targets.

To build local documentation
install
  * Sphinx
  * breathe (plugin for sphinx)
  * doxygen

and Run
 $ sphinx -T -b html docs/ docs/_build
to create the documentation in the folder docs/_build
""")


def main():
    create_bazel_project(sys.argv[1])


if __name__ == "__main__":
    main()
