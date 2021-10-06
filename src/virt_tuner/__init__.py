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
Utility functions to generate tuned configuration virtual machines
"""

from collections import namedtuple
import gettext
import logging
import itertools
import virt_tuner.virt

gettext.bindtextdomain("virt-tuner", "/usr/share/locale")
gettext.textdomain("virt-tuner")
try:
    gettext.install("virt-tuner", localedir="/usr/share/locale")
except IOError:
    import builtins

    builtins.__dict__["_"] = str

log = logging.getLogger(__name__)

__version__ = "0.0.3"


Template = namedtuple("Template", ["description", "function", "parameters"])


def single():
    """
    Compute parameters for single VM per host.
    """
    cells = virt_tuner.virt.host_topology()
    cpus = [cell.cpus for cell in cells]
    cpus = [cpu for sublist in cpus for cpu in sublist]

    key_fn = lambda c: "{}-{}".format(c["socket_id"], c["core_id"])

    # Sort the cpus to have the consecutive IDs for the siblings:
    # QEMU needs this trick to think the two virtual cpus are located on the same core.
    cpus = sorted(cpus, key=key_fn)
    for id, cpu in enumerate(cpus):
        cpu['id'] = id

    cpu_topology = {
        "sockets": len({c["socket_id"] for c in cpus}),
        "cores": len({c["core_id"] for c in cpus}),
        "threads": {
            len(list(g)) for k, g in itertools.groupby(sorted(cpus, key=key_fn), key_fn)
        }.pop(),
    }

    # Compute the amount of 1GiB pages per cell.
    # We want an even number of pages on each cell
    # and at least 9% of the total memory amount for the host
    cells_mem = [cell.memory for cell in cells]
    cells_pages = [int(mem / (1024 ** 2)) for mem in cells_mem]
    cell_pages_max = min(cells_pages)

    pages_per_cell = int(sum(cells_mem) * 0.91 / (1024 ** 2) / len(cells_mem))
    if cell_pages_max * len(cells_mem) * 1024 ** 2 / sum(cells_mem) <= 0.91:
        pages_per_cell = cell_pages_max

    vm_memory = pages_per_cell * len(cells)

    return {
        "cpu": {
            "placement": "static",
            "maximum": cpu_topology["sockets"]
            * cpu_topology["cores"]
            * cpu_topology["threads"],
            "topology": cpu_topology,
            "mode": "host-passthrough",
            "check": "none",
            "features": {
                "rdtscp": "require",
                "invtsc": "require",
                "x2apic": "require",
            },
            "tuning": {
                "vcpupin": {cpu["id"]: cpu["siblings"] for cpu in cpus},
            },
            "numa": {
                c.id: {
                    "cpus": ",".join([str(cpu["id"]) for cpu in sorted(c.cpus, key=lambda c: c["id"])]),
                    "memory": str(pages_per_cell) + " GiB",
                    "distances": c.distances,
                }
                for c in cells
            },
        },
        "numatune": {
            "memory": {
                "mode": "strict",
                "nodeset": ",".join([str(cell.id) for cell in cells]),
            },
            "memnodes": {
                cell.id: {"mode": "strict", "nodeset": cell.id} for cell in cells
            },
        },
        "mem": {
            "boot": str(vm_memory) + " GiB",
            "current": str(vm_memory) + " GiB",
            "nosharepages": True,
            "hugepages": [{"size": "1 G"}],
        },
        "hypervisor_features": {"kvm-hint-dedicated": True},
        "clock": {
            "timers": {
                "rtc": {"tickpolicy": "catchup"},
                "pit": {"tickpolicy": "catchup"},
                "hpet": {"present": False},
            },
        },
    }


templates = {
    "single": Template(
        _("Single virtual machine using almost all the host resources"),
        single,
        [],
    ),
}
