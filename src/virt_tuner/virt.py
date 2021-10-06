# -*- coding: utf-8 -*-
# Authors: Cedric Bosdonnat <cbosdonnat@suse.com>

# Copyright (C) 2021 SUSE, Inc.

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
Functions interacting with libvirt
"""

from collections import namedtuple
import logging
from xml.etree import ElementTree
import libvirt

log = logging.getLogger(__name__)

Cell = namedtuple("Cell", ["id", "cpus", "memory", "distances", "pages"])


def host_topology():
    """
    Extract topology from the host capabilities.
    """
    cnx = libvirt.open()
    cells = []
    try:
        caps = ElementTree.fromstring(cnx.getCapabilities())
        cell_nodes = caps.findall(".//topology/cells/cell")
        cells = [
            Cell(
                int(node.get("id")),
                [cpu.attrib for cpu in node.findall("cpus/cpu")],
                int(node.find("memory").text),  # libvirt always outputs memory in KiB
                {
                    int(dist.get("id")): int(dist.get("value"))
                    for dist in node.findall("distances/sibling")
                },
                [
                    {
                        "size": "{} {}".format(page.get("size"), page.get("unit")),
                        "count": int(page.text),
                    }
                    for page in node.findall("pages")
                ],
            )
            for node in cell_nodes
        ]
    except libvirt.libvirtError as err:
        log.error(err)
    finally:
        cnx.close()

    return cells
