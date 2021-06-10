#!/usr/bin/python3
# -*- coding: utf-8; -*-
# Authors: Cedric Bosdonnat <cbosdonnat@suse.com>
#
# Copyright (C) 2021 SUSE, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Setup script used for building, testing, and installing modules
based on setuptools.
"""

import codecs
import os
import re
import sys
import subprocess
import time
import setuptools
from setuptools.command.install import install
from setuptools.command.sdist import sdist

sys.path.insert(0, "src")
import virt_tuner


def read(fname):
    """
    Utility function to read the text file.
    """
    path = os.path.join(os.path.dirname(__file__), fname)
    with codecs.open(path, encoding="utf-8") as fobj:
        return fobj.read()


class PostInstallCommand(install):
    """
    Post-installation commands.
    """

    def run(self):
        """
        Post install script
        """
        cmd = [
            "pod2man",
            "--center=VM definition tuner",
            "--name=VIRT-TUNER",
            "--release=%s" % virt_tuner.__version__,
            "man/virt-tuner.pod",
            "man/virt-tuner.1",
        ]
        if subprocess.call(cmd) != 0:
            raise RuntimeError("Building man pages has failed")
        install.run(self)


class CheckLint(setuptools.Command):
    """
    Check python source files with pylint and black.
    """

    user_options = [("errors-only", "e", "only report errors")]
    description = "Check code using pylint and black"

    def initialize_options(self):
        """
        Initialize the options to default values.
        """
        self.errors_only = False

    def finalize_options(self):
        """
        Check final option values.
        """
        pass

    def run(self):
        """
        Call black and pylint here.
        """
        files = ["src", "tests/"]

        print(">>> Running black ...")
        processes = []
        processes.append(subprocess.run(["black", "--check"] + files))

        output_format = "colorized" if sys.stdout.isatty() else "text"

        pylint_opts = ["--output-format=%s" % output_format]

        if self.errors_only:
            pylint_opts.append("-E")

        print(">>> Running pylint ...")
        processes.append(subprocess.run(["pylint", "src"] + pylint_opts))

        print(">>> Running pylint ...")
        processes.append(
            subprocess.run(
                ["pylint", "tests", "--rcfile", "tests/.pylintrc"] + pylint_opts,
                env={"PYTHONPATH": "src"},
            )
        )

        sys.exit(sum([p.returncode for p in processes]))


# SdistCommand is reused from the libvirt python binding (GPLv2+)
class SdistCommand(sdist):
    """
    Custom sdist command, generating a few files.
    """

    user_options = sdist.user_options

    description = "Update AUTHORS and ChangeLog; build sdist-tarball."

    def gen_authors(self):
        """
        Generate AUTHORS file out of git log
        """
        fdlog = os.popen("git log --pretty=format:'%aN <%aE>'")
        authors = []
        for line in fdlog:
            line = "   " + line.strip()
            if line not in authors:
                authors.append(line)

        authors.sort(key=str.lower)

        with open("AUTHORS.in", "r") as fd1, open("AUTHORS", "w") as fd2:
            for line in fd1:
                fd2.write(line.replace("@AUTHORS@", "\n".join(authors)))

    def gen_changelog(self):
        """
        Generate ChangeLog file out of git log
        """
        cmd = "git log '--pretty=format:%H:%ct %an  <%ae>%n%n%s%n%b%n'"
        fd1 = os.popen(cmd)
        fd2 = open("ChangeLog", "w")

        for line in fd1:
            match = re.match(r"([a-f0-9]+):(\d+)\s(.*)", line)
            if match:
                timestamp = time.gmtime(int(match.group(2)))
                fd2.write(
                    "%04d-%02d-%02d %s\n"
                    % (
                        timestamp.tm_year,
                        timestamp.tm_mon,
                        timestamp.tm_mday,
                        match.group(3),
                    )
                )
            else:
                if re.match(r"Signed-off-by", line):
                    continue
                fd2.write("    " + line.strip() + "\n")

        fd1.close()
        fd2.close()

    def run(self):
        if not os.path.exists("build"):
            os.mkdir("build")

        if os.path.exists(".git"):
            try:
                self.gen_authors()
                self.gen_changelog()

                sdist.run(self)

            finally:
                files = ["AUTHORS", "ChangeLog"]
                for item in files:
                    if os.path.exists(item):
                        os.unlink(item)
        else:
            sdist.run(self)


setuptools.setup(
    name="virt-tuner",
    version=virt_tuner.__version__,
    author="Cedric Bosdonnat",
    author_email="cbosdonnat@suse.com",
    description="VM definition tuner",
    license="GPLv3+",
    long_description=read("README.md"),
    url="https://github.com/cbosdo/virt-tuner",
    keywords="virtualization",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    entry_points={
        "console_scripts": [
            "virt-tuner=virt_tuner.main:main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    cmdclass={
        "install": PostInstallCommand,
        "lint": CheckLint,
        "sdist": SdistCommand,
    },
    data_files=[("share/man/man1", ["man/virt-tuner.1"])],
    tests_require=["mock>=2.0"],
    extras_require={"dev": ["pylint", "black"]},
)
