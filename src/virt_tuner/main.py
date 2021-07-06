# -*- coding: utf-8 -*-
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
Main entry point of the CLI tool
"""

import argparse
import gettext
import logging
import os.path
import sys

import virt_tuner
import virt_tuner.xmlutil as xmlutil

gettext.bindtextdomain("virt-tuner", "/usr/share/locale")
gettext.textdomain("virt-tuner")
try:
    gettext.install("virt-tuner", localedir="/usr/share/locale")
except IOError:
    import builtins

    builtins.__dict__["_"] = str

logger = logging.getLogger("virt_tuner.main")


def set_logging_conf(loglevel=None):
    """
    Set format and logging level
    """
    # Get logger
    module_logger = logging.getLogger("virt_tuner")

    # Create console handler
    console_handler = logging.StreamHandler()

    # Set logging format
    log_format = "%(levelname)-8s: %(message)s"
    console_handler.setFormatter(logging.Formatter(log_format))

    # Add the handlers to logger
    module_logger.addHandler(console_handler)

    # Set logging level
    module_logger.setLevel(loglevel or logging.INFO)


def list_templates():
    """
    Print the list of templates to stdout
    """
    buf = _("templates:\n")
    for name, template in virt_tuner.templates.items():
        buf += f" - {name}: {template.description}\n"
    return buf


def cli(argv):
    """
    CLI tool main function.
    Returns the exit code and takes parameters for better testability.
    """
    parser = argparse.ArgumentParser(
        description=_("VM definition tuner"),
        conflict_handler="resolve",
        epilog=list_templates(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        help=_("Print the version"),
        action="version",
        version="%(prog)s " + virt_tuner.__version__,
    )
    parser.add_argument(
        "-d",
        "--debug",
        help=_("Show debug messages"),
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )

    parser.add_argument(
        "--template",
        required=True,
        choices=virt_tuner.templates.keys(),
        help=_("the template to apply to tune the virtual machine."),
    )
    parser.add_argument(
        "input",
        metavar="INPUT_PATH",
        help="path to virtual machine XML to tune or '-' to read it from standard input",
    )

    try:
        args = parser.parse_args(argv)

        # Configure logging lovel/format
        set_logging_conf(args.loglevel)

        if not args.template or args.template not in virt_tuner.templates:
            if args.template:
                logging.error(_("Unknown template: " + args.template))
            print(list_templates())
            return 1

        # Update the VM here!
        if args.input == "-":
            definition = sys.stdin.read()
        elif os.path.isfile(args.input):
            with open(args.input, "r") as file_handle:
                definition = file_handle.read()
        else:
            logging.error(_("Input path has to point to a readable file"))
            return 1

        new_config = virt_tuner.templates[args.template].function()
        print(xmlutil.merge_config(definition, new_config).decode())

        return 0
    except KeyboardInterrupt:
        return 0
    except ValueError as err:
        logging.error(err)
        return 1


def main():
    """
    CLI wrapper handling the arguments and exit from sys
    """
    sys.exit(cli(sys.argv[1:]))
