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
import logging
import itertools
import virt_tuner.virt

log = logging.getLogger(__name__)

__version__ = "0.0.1"


Template = namedtuple("Template", ["description", "function", "parameters"])


def single():
    """
    Compute parameters for single VM per host.
    """
    cells = virt_tuner.virt.host_topology()
    cpus = [cell.cpus for cell in cells]
    cpus = [cpu for sublist in cpus for cpu in sublist]

    key_fn = lambda c: "{}-{}".format(c["socket_id"], c["core_id"])

    cpu_topology = {
        "sockets": len({c["socket_id"] for c in cpus}),
        "cores": len({c["core_id"] for c in cpus}),
        "threads": {
            len(list(g)) for k, g in itertools.groupby(sorted(cpus, key=key_fn), key_fn)
        }.pop(),
    }

    # Round to multiple of 1GiB due to enforced 1GiB hugepages
    vm_memory = int(virt_tuner.virt.host_memory() * 0.9 / 1024) * 1024

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
                    "cpus": ",".join([str(cpu["id"]) for cpu in c.cpus]),
                    "memory": str(int(vm_memory / len(cells))) + " MiB",
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
            "boot": str(vm_memory) + " MiB",
            "current": str(vm_memory) + " MiB",
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
        "Single virtual machine using almost all the host resources",
        single,
        [],
    ),
}
