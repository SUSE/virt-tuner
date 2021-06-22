"""
Test functions for module virt_tuner.xmlutil
"""

from xml.etree import ElementTree

import pytest

import virt_tuner.xmlutil


@pytest.fixture(name="doc")
def fixture_doc():
    """
    Create a test XML document
    """
    return ElementTree.fromstring(
        """<domain>
      <cpu mode='custom' match='exact' check='none'>
        <model fallback='forbid'>qemu64</model>
      </cpu>
    </domain>"""
    )


def test_get_node_existing(doc):
    """
    Test get_node() function on a node that already exists
    """
    assert virt_tuner.xmlutil.get_node(doc, ["cpu", "model"]) == doc.find("./cpu/model")
    assert virt_tuner.xmlutil.get_node(
        doc, ["cpu", "model[@fallback='forbid']"]
    ) == doc.find("./cpu/model[1]")
    assert virt_tuner.xmlutil.get_node(doc, ["cpu", "model[1]"]) == doc.find(
        "./cpu/model[1]"
    )
    assert len(doc.findall("cpu/model")) == 1


def test_get_node_new(doc):
    """
    Test get_node() function on missing nodes
    """
    assert virt_tuner.xmlutil.get_node(doc, ["cpu", "feature"]) == doc.find(
        "./cpu/feature"
    )
    assert (
        virt_tuner.xmlutil.get_node(doc, ["cpu", "feature[@name='pcid']"]) is not None
    )
    assert virt_tuner.xmlutil.get_node(doc, ["cpu", "feature[2]"]) == doc.find(
        "./cpu/feature[2]"
    )
    assert [node.get("name") for node in doc.findall("cpu/feature")] == [
        None,
        "pcid",
    ]


@pytest.mark.parametrize("has_value", (True, False))
def test_set_attribute(doc, has_value):
    """
    Test the set_attribute() function
    """
    virt_tuner.xmlutil.set_attribute(
        doc, ["cpu", "feature"], "name", "pcid" if has_value else None
    )

    feature_node = doc.find("./cpu/feature")
    if has_value:
        assert feature_node is not None
        assert feature_node.get("name") == "pcid"
    else:
        assert feature_node is None


@pytest.mark.parametrize("has_value", (True, False))
def test_set_text(doc, has_value):
    """
    Test the set_text() function
    """
    virt_tuner.xmlutil.set_text(doc, ["currentMemory"], "123" if has_value else None)

    mem_node = doc.find("./currentMemory")
    if has_value:
        assert mem_node is not None
        assert mem_node.text == "123"
    else:
        assert mem_node is None


@pytest.mark.parametrize("has_value", (True, False))
def test_set_mem_attr(doc, has_value):
    """
    Test the set_mem_attr() function
    """
    virt_tuner.xmlutil.set_mem_attr(
        doc, ["currentMemory"], "size", "123 KiB" if has_value else None
    )

    mem_node = doc.find("./currentMemory")
    if has_value:
        assert mem_node is not None
        assert mem_node.get("size") == "123"
        assert mem_node.get("unit") == "KiB"
    else:
        assert mem_node is None


@pytest.mark.parametrize("has_value", (True, False))
def test_set_mem(doc, has_value):
    """
    Test the set_mem() function
    """
    virt_tuner.xmlutil.set_mem(doc, ["currentMemory"], "123 KiB" if has_value else None)

    mem_node = doc.find("currentMemory")
    if has_value:
        assert mem_node is not None
        assert mem_node.text == "123"
        assert mem_node.get("unit") == "KiB"
    else:
        assert mem_node is None


def test_merge_config(doc):
    """
    Test the merge_config() function
    """
    config = {
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
                    0: "0-1",
                    1: "0-1",
                    2: "2-3",
                    3: "2-3",
                    4: "4-5",
                    5: "4-5",
                    6: "6-7",
                    7: "6-7",
                    8: "8-9",
                    9: "8-9",
                    10: "10-11",
                    11: "10-11",
                    12: "12-13",
                    13: "12-13",
                    14: "14-15",
                    15: "14-15",
                },
            },
            "numa": {
                0: {
                    "cpus": "0,1,2,3",
                    "memory": "768 MiB",
                    "distances": {"0": 10, "1": 20, "2": 20, "3": 20},
                },
                1: {
                    "cpus": "4,5,6,7",
                    "memory": "768 MiB",
                    "distances": {"0": 20, "1": 10, "2": 20, "3": 20},
                },
                2: {
                    "cpus": "8,9,10,11",
                    "memory": "768 MiB",
                    "distances": {"0": 20, "1": 20, "2": 10, "3": 20},
                },
                3: {
                    "cpus": "12,13,14,15",
                    "memory": "768 MiB",
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
            "boot": "3072 MiB",
            "current": "3072 MiB",
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
    xml_def = ElementTree.tostring(doc)
    merged = virt_tuner.xmlutil.merge_config(xml_def, config)
    merged_doc = ElementTree.fromstring(merged)

    assert merged_doc.find("vcpu").get("placement") == "static"
    assert merged_doc.find("vcpu").text == "16"
    assert merged_doc.find("cpu/topology").get("sockets") == "4"
    assert merged_doc.find("cpu/topology").get("cores") == "2"
    assert merged_doc.find("cpu/topology").get("threads") == "2"
    assert merged_doc.find("cpu").get("mode") == "host-passthrough"
    assert merged_doc.find("cpu").get("check") == "none"
    assert "match" not in merged_doc.find("cpu").keys()
    assert [
        node.get("name")
        for node in merged_doc.findall("cpu/feature[@policy='require']")
    ] == ["rdtscp", "invtsc", "x2apic"]
    assert merged_doc.find("cputune/vcpupin[@vcpu='11']").get("cpuset") == "10-11"
    assert merged_doc.find("cpu/numa/cell[@id='2']").get("cpus") == "8,9,10,11"
    assert merged_doc.find("cpu/numa/cell[@id='2']").get("memory") == "768"
    assert merged_doc.find("cpu/numa/cell[@id='2']").get("unit") == "MiB"
    assert (
        merged_doc.find("cpu/numa/cell[@id='2']/distances/sibling[@id='0']").get(
            "value"
        )
        == "20"
    )
    assert merged_doc.find("numatune/memory").get("mode") == "strict"
    assert merged_doc.find("numatune/memory").get("nodeset") == "0,1,2,3"
    assert merged_doc.find("numatune/memnode[@cellid='1']").get("mode") == "strict"
    assert merged_doc.find("numatune/memnode[@cellid='1']").get("nodeset") == "1"
    assert merged_doc.find("features/kvm/hint-dedicated").get("state") == "on"
    assert merged_doc.find("memory").get("unit") == "MiB"
    assert merged_doc.find("memory").text == "3072"
    assert merged_doc.find("currentMemory").get("unit") == "MiB"
    assert merged_doc.find("currentMemory").text == "3072"
    assert merged_doc.find("memoryBacking/nosharepages") is not None
    assert merged_doc.find("memoryBacking/hugepages/page[@size='1']").get("unit") == "G"
    assert merged_doc.find("clock/timer[@name='rtc']").get("tickpolicy") == "catchup"
    assert merged_doc.find("clock/timer[@name='hpet']").get("present") == "no"
