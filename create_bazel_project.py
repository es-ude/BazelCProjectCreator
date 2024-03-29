#!/usr/bin/env python3

import os
import os.path
import sys


elasticNodeMiddleware = False
if len(sys.argv) >= 3 and str(sys.argv[2]) == "ElasticNodeMiddlewareProject":
    elasticNodeMiddleware = True


def create_workspace_content(project_name, use_comm_lib=False):
    content = """workspace(
    name = "{project_name}"
)

load("//:github.bzl", "es_github_archive")
load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

es_github_archive(
    name = "EmbeddedSystemsBuildScripts",
    version = "1.0.2",
   # sha256 = "<checksum>"
)

load("@EmbeddedSystemsBuildScripts//Toolchains/Avr:avr.bzl", "avr_toolchain")

avr_toolchain()

http_archive(
    name = "Unity",
    build_file = "@EmbeddedSystemsBuildScripts//:BUILD.Unity",
    strip_prefix = "Unity-master",
    urls = ["https://github.com/ThrowTheSwitch/Unity/archive/master.tar.gz"],
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

http_archive(
    name = "LUFA",
    build_file = "@EmbeddedSystemsBuildScripts//:BUILD.LUFA",
    strip_prefix = "lufa-LUFA-170418",
    urls = ["https://fourwalledcubicle.com/files/LUFA/LUFA-170418.zip"],
)
""".format(
        project_name=project_name
    )
    if use_comm_lib:
        content += """
es_github_archive(
    name = "CommunicationModule",
    repo = "CommunicationLibrary",
    version = "0.1.7"
)

es_github_archive(
    name = "PeripheralInterface",
    version = "0.7.1"
)

es_github_archive(
    name = "EmbeddedUtilities",
    repo = "EmbeddedUtil",
    version = "0.3.2"
)
"""
    return content


def create_bazel_project(project_root):
    name = os.path.basename(project_root)

    def create_file(path, content):
        full_path = os.path.abspath(os.path.join(project_root, path))
        print(full_path)
        dir = os.path.dirname(full_path)
        if os.path.isfile(full_path):
            raise FileExistsError(full_path)
        os.makedirs(dir, exist_ok=True)
        with open(full_path, "w") as file:
            file.write(content)

    def create_package(path, build_file_content):
        build_file_path = os.path.join(path, "BUILD.bazel")
        create_file(build_file_path, build_file_content)

    def create_elasticNodeMiddlewareFiles():
        print("Creating files for an Elastic Node Middleware Project.")
        try:
            import requests
        except:
            print("You need to install requests with: pip install requests (pip3 install requests)")
            exit()

        os.mkdir(project_root + "/bitfiles")
        create_file("bitfiles/.gitkeep", "")
        # TODO: change to master
        link = "https://raw.githubusercontent.com/es-ude/ElasticNodeMiddleware/master/"
        templates = link + "templates/"

        create_file("init.py", requests.get(templates + "init.py").text.replace(
            "/path/to/MyProject/",
            os.path.abspath("") + "/" + name + "/",
            )
        )
        create_file(
            ".gitignore",
            requests.get(templates + ".gitignore").text,
        )
        create_file(
            "BUILD.bazel",
            requests.get(templates + "BUILD.bazel").text.replace("MyProject", name),
        )
        create_file(
            "WORKSPACE",
            requests.get(link + "WORKSPACE").text.replace("elasticnodemiddleware", name)
            + """
es_github_archive(
    name = "ElasticNodeMiddleware",
    version = """ + '"' + requests.get("https://api.github.com/repos/es-ude/ElasticNodeMiddleware/releases/latest").json()["tag_name"][1:] + '"' + """
)
""",
        )
        create_file("app/BUILD.bazel", requests.get(templates + "appBUILD.bazel").text)
        create_file(
            "app/examples/BUILD.bazel",
            requests.get(templates + "appExamplesBUILD.bazel").text,
        )
        create_file("app/main.c", requests.get(link + "app/main.c").text)
        create_file(
            "app/examples/blinkExample.c",
            requests.get(link + "app/examples/blinkExample.c").text,
        )
        create_file(
            "app/examples/blinkLufaExample.c",
            requests.get(link + "app/examples/blinkLufaExample.c").text,
        )
        create_file(
            "app/examples/blinkUartExample.c",
            requests.get(link + "app/examples/blinkUartExample.c").text,
        )
        create_file(
            "app/examples/monitoringExample.c",
            requests.get(link + "app/examples/monitoringExample.c").text,
        )
        create_file(
            "uploadScripts/uploadBitfiles.py",
            requests.get(templates + "uploadBitfiles.py").text,
        )

    if not elasticNodeMiddleware:
        create_file("WORKSPACE", create_workspace_content(name))

    if not elasticNodeMiddleware:
        create_package(
        "app/setup",
        """load("@AvrToolchain//platforms/cpu_frequency:cpu_frequency.bzl", "cpu_frequency_flag")

cc_library(
    name = "Setup",
    srcs = glob(["*.c"]),
    hdrs = glob(["*.h"]),
    deps = ["//:Library"],
    visibility = ["//visibility:public"],
)
""",
    )
    else:
        create_package(
        "app/setup",
        """load("@AvrToolchain//platforms/cpu_frequency:cpu_frequency.bzl", "cpu_frequency_flag")

cc_library(
    name = "Setup",
    srcs = glob(["*.c"]),
    hdrs = glob(["*.h"]),
    visibility = ["//visibility:public"],
)
""",
    )

    if not elasticNodeMiddleware:
        create_package(
            "app",
            """load("@AvrToolchain//:helpers.bzl", "default_embedded_binaries")
load("@AvrToolchain//platforms/cpu_frequency:cpu_frequency.bzl", "cpu_frequency_flag")

default_embedded_binaries(
    main_files = glob(["*.c"]),
    copts = cpu_frequency_flag(),
#   uploader = "@AvrToolchain//:avrdude_upload_script",
#   uploader = "@AvrToolchain//:dfu_upload_script",    
    deps = [
        "//app/setup:Setup",
        "//:Library",
        "//{}:HdrOnlyLib",
        ],
)
""".format(
                name
            ),
        )

    if not elasticNodeMiddleware:
        create_file(
            "app/main.c",
            """#include <avr/io.h>
#include <util/delay.h>
#include <stdbool.h>

int
main(void)
{
  DDRB = _BV(5);
  while (true)
  {
    _delay_ms(500);
    PORTB ^= _BV(5);
  }
}""",
        )
    create_package(
        name,
        """cc_library(
   name = "HdrOnlyLib",
   hdrs = glob(["**/*.h"]),
   visibility = ["//visibility:public"],
)
""",
    )
    if not elasticNodeMiddleware:
        create_package(
            "",
            """load("@AvrToolchain//platforms/cpu_frequency:cpu_frequency.bzl", "cpu_frequency_flag")

cc_library(
    name = "Library",
    srcs = glob(["src/**/*.c", "src/**/*.h"]),
    copts = cpu_frequency_flag(),
    visibility = ["//visibility:public"],
    deps = [
        "//{}:HdrOnlyLib"
    ]
)
""".format(
                name
            ),
        )

    create_file("src/.gitkeep", "")

    if not elasticNodeMiddleware:
        create_package(
        "test",
        """load("@EmbeddedSystemsBuildScripts//Unity:unity.bzl", "generate_a_unity_test_for_every_file", "unity_test")

generate_a_unity_test_for_every_file(
    cexception = False,
    file_list = glob(["*_Test.c"]),
    deps = [
        "//:Library",
        "//{}:HdrOnlyLib",
    ],
)
""".format(
            name
        ),
    )
    else:
        create_package(
        "test",
        """load("@EmbeddedSystemsBuildScripts//Unity:unity.bzl", "generate_a_unity_test_for_every_file", "unity_test")

generate_a_unity_test_for_every_file(
    cexception = False,
    file_list = glob(["*_Test.c"]),
    deps = [
        "//{}:HdrOnlyLib",
    ],
)
""".format(
            name
        ),
    )

    create_file(
        "test/first_Test.c",
        """#include "unity.h"

void
test_shouldFail(void)
{
   TEST_FAIL();
}
""",
    )
    create_file(
        "github.bzl",
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
""",
    )

    create_file(
        ".bazelrc",
        """test --test_output=errors
build --incompatible_enable_cc_toolchain_resolution=true
try-import user.bazelrc
""",
    )
    if not elasticNodeMiddleware:
        create_file(
        ".gitignore",
        """.vscode/
.clwb/
bazel-*
user.bazelrc
""",
    )
    create_file(
        "docs/conf.py",
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
#    'sphinx.ext.pngmath',
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


breathe_projects = {{"{project}": "xml/"}}
breathe_default_project = "{project}"

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
""".format(
            project=name
        ),
    )
    create_file(
        "docs/requirements.txt",
        """Sphinx >= 2.0
breathe
""",
    )
    create_file(
        "docs/doxy.conf",
        """INPUT = ../{headers}/
GENERATE_XML = YES
GENERATE_LATEX = NO
GENERATE_HTML = NO
XML_OUTPUT = @@OUTPUT_DIRECTORY@@/xml
""".format(
            headers=name
        ),
    )
    create_file("docs/index.rst", "**{}**".format(name))

    if elasticNodeMiddleware:
        create_elasticNodeMiddlewareFiles()

    print(
        """
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
"""
    )


def replace_illegal_characters(project_name):
    illegal_characters = [".", " ", "-"]
    new_character = "_"
    for illegal_character in illegal_characters:
        project_name = project_name.replace(illegal_character, new_character)
    return project_name


def main():
    if len(sys.argv) < 2:
        print("usage: ./create_bazel_project.py PROJECT_NAME")
    else:
        name = replace_illegal_characters(sys.argv[1])
        create_bazel_project(name)


if __name__ == "__main__":
    main()
