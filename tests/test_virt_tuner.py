"""
Tests for the virt_tuner module
"""

from unittest.mock import patch
import pytest
import virt_tuner


@pytest.mark.parametrize(
    "cell_mems, expected_cell_pages",
    [
        ([13757440, 19270488, 15854592, 16808124], 13),
        ([15854592, 16808124, 15854592, 17173336], 14),
    ],
    ids=["unbalanced cells", "balanced cells"],
)
def test_single(cell_mems, expected_cell_pages):
    """
    Test the virt_tuner.single() function
    """
    cells = [
        virt_tuner.virt.Cell(
            0,
            [
                {"id": 0, "socket_id": 0, "core_id": 0, "siblings": "0,2"},
                {"id": 1, "socket_id": 0, "core_id": 1, "siblings": "1,3"},
                {"id": 2, "socket_id": 0, "core_id": 0, "siblings": "0,2"},
                {"id": 3, "socket_id": 0, "core_id": 1, "siblings": "1,3"},
            ],
            cell_mems[0],
            {"0": 10, "1": 20, "2": 20, "3": 20},
            [
                {"size": "4 KiB", "count": 226383},
                {"size": "2048 KiB", "count": 0},
                {"size": "1048576 KiB", "count": 0},
            ],
        ),
        virt_tuner.virt.Cell(
            1,
            [
                {"id": 4, "socket_id": 1, "core_id": 0, "siblings": "4,6"},
                {"id": 5, "socket_id": 1, "core_id": 1, "siblings": "5,7"},
                {"id": 6, "socket_id": 1, "core_id": 0, "siblings": "4,6"},
                {"id": 7, "socket_id": 1, "core_id": 1, "siblings": "5,7"},
            ],
            cell_mems[1],
            {"0": 20, "1": 10, "2": 20, "3": 20},
            [
                {"size": "4 KiB", "count": 227274},
                {"size": "2048 KiB", "count": 0},
                {"size": "1048576 KiB", "count": 0},
            ],
        ),
        virt_tuner.virt.Cell(
            2,
            [
                {"id": 8, "socket_id": 2, "core_id": 0, "siblings": "8,10"},
                {"id": 9, "socket_id": 2, "core_id": 1, "siblings": "9,11"},
                {"id": 10, "socket_id": 2, "core_id": 0, "siblings": "8,10"},
                {"id": 11, "socket_id": 2, "core_id": 1, "siblings": "9,11"},
            ],
            cell_mems[2],
            {"0": 20, "1": 20, "2": 10, "3": 20},
            [
                {"size": "4 KiB", "count": 227018},
                {"size": "2048 KiB", "count": 0},
                {"size": "1048576 KiB", "count": 0},
            ],
        ),
        virt_tuner.virt.Cell(
            3,
            [
                {"id": 12, "socket_id": 3, "core_id": 0, "siblings": "12,14"},
                {"id": 13, "socket_id": 3, "core_id": 1, "siblings": "13,15"},
                {"id": 14, "socket_id": 3, "core_id": 0, "siblings": "12,14"},
                {"id": 15, "socket_id": 3, "core_id": 1, "siblings": "13,15"},
            ],
            cell_mems[3],
            {"0": 20, "1": 20, "2": 20, "3": 10},
            [
                {"size": "4 KiB", "count": 202115},
                {"size": "2048 KiB", "count": 0},
                {"size": "1048576 KiB", "count": 0},
            ],
        ),
    ]

    with patch("virt_tuner.virt") as virt_mock:
        virt_mock.host_topology.return_value = cells

        assert virt_tuner.single() == {
            "cpu": {
                "placement": "static",
                "maximum": 16,
                "topology": {"sockets": 4, "cores": 2, "threads": 2},
                "mode": "host-passthrough",
                "check": "none",
                "features": {
                    "rdtscp": "require",
                    "invtsc": "require",
                    "x2apic": "require",
                },
                "tuning": {
                    "vcpupin": {
                        0: "0,2",
                        1: "0,2",
                        2: "1,3",
                        3: "1,3",
                        4: "4,6",
                        5: "4,6",
                        6: "5,7",
                        7: "5,7",
                        8: "8,10",
                        9: "8,10",
                        10: "9,11",
                        11: "9,11",
                        12: "12,14",
                        13: "12,14",
                        14: "13,15",
                        15: "13,15",
                    },
                },
                "numa": {
                    0: {
                        "cpus": "0,1,2,3",
                        "memory": str(expected_cell_pages) + " GiB",
                        "distances": {"0": 10, "1": 20, "2": 20, "3": 20},
                    },
                    1: {
                        "cpus": "4,5,6,7",
                        "memory": str(expected_cell_pages) + " GiB",
                        "distances": {"0": 20, "1": 10, "2": 20, "3": 20},
                    },
                    2: {
                        "cpus": "8,9,10,11",
                        "memory": str(expected_cell_pages) + " GiB",
                        "distances": {"0": 20, "1": 20, "2": 10, "3": 20},
                    },
                    3: {
                        "cpus": "12,13,14,15",
                        "memory": str(expected_cell_pages) + " GiB",
                        "distances": {"0": 20, "1": 20, "2": 20, "3": 10},
                    },
                },
            },
            "numatune": {
                "memory": {
                    "mode": "strict",
                    "nodeset": "0,1,2,3",
                },
                "memnodes": {
                    0: {"mode": "strict", "nodeset": 0},
                    1: {"mode": "strict", "nodeset": 1},
                    2: {"mode": "strict", "nodeset": 2},
                    3: {"mode": "strict", "nodeset": 3},
                },
            },
            "hypervisor_features": {"kvm-hint-dedicated": True},
            "mem": {
                "boot": str(expected_cell_pages * len(cell_mems)) + " GiB",
                "current": str(expected_cell_pages * len(cell_mems)) + " GiB",
                "nosharepages": True,
                "hugepages": [{"size": "1 G"}],
            },
            "clock": {
                "timers": {
                    "rtc": {"tickpolicy": "catchup"},
                    "pit": {"tickpolicy": "catchup"},
                    "hpet": {"present": False},
                },
            },
        }
