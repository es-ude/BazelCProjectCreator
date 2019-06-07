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

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "EmbeddedSystemsBuildScripts",
    type = "tar.gz",
    strip_prefix = "EmbeddedSystemsBuildScripts-0.5",
    urls = ["https://github.com/es-ude/EmbeddedSystemsBuildScripts/archive/v0.5.tar.gz"],
	 sha256 = "6259c248d977f8e61f36347eedffcc63f580685dd13063da35be93fd27853440"
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
    print("""
Run
 $ bazel query //...
from the new project's root directory
to see a list of available targets.
""")


def main():
    create_bazel_project(sys.argv[1])


if __name__ == "__main__":
    main()
