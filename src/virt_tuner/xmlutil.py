"""
XML utility functions
"""
from xml.etree import ElementTree
import re


def get_node(doc, path):
    """
    Get the node corresponding to a given path. The path is an array of tag names.
    """
    node = doc
    for segment in path:
        child = node.find(segment)
        if child is None:
            matcher = re.fullmatch(
                r"(?P<tag>\w+)\[(?:(?:@(?P<attr>\w+)=['\"](?P<value>[^'\"]+)['\"])|[0-9]+)\]",
                segment,
            )
            tag = matcher.group("tag") if matcher else segment
            child = ElementTree.SubElement(node, tag)
            if matcher and matcher.group("attr"):
                child.set(matcher.group("attr"), matcher.group("value"))
        node = child
    return node


def serialize(value):
    """
    Serialize a value for libvirt's xml
    """
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def set_attribute(doc, path, attr, value):
    """
    Set the attribute of a node if defined.
    """
    if value is not None:
        node = get_node(doc, path)
        node.set(attr, serialize(value))


def set_text(doc, path, value):
    """
    Set the text content of a node if defined.
    """
    if value is not None:
        node = get_node(doc, path)
        node.text = serialize(value)


def set_mem(doc, path, value):
    """
    Set a memory value as node text with its unit
    """
    if value:
        parts = value.split(" ")
        if len(parts) == 2:
            set_text(doc, path, parts[0])
            set_attribute(doc, path, "unit", parts[1])


def set_mem_attr(doc, path, attr, value):
    """
    Set a memory value as attribute with its unit
    """
    if value:
        parts = value.split(" ")
        if len(parts) == 2:
            set_attribute(doc, path, attr, parts[0])
            set_attribute(doc, path, "unit", parts[1])


def merge_cpu_config(doc, config):
    """
    Merge the cpu configuration with the input XML definition ElementTree document
    """
    set_attribute(doc, ["vcpu"], "placement", config.get("placement"))
    set_text(doc, ["vcpu"], config.get("maximum"))

    for attribute in ["sockets", "cores", "threads"]:
        set_attribute(
            doc,
            ["cpu", "topology"],
            attribute,
            config.get("topology", {}).get(attribute),
        )

    set_attribute(doc, ["cpu"], "mode", config.get("mode"))
    if config.get("mode") in ["host-model", "host-passthrough"]:
        cpu_node = doc.find("cpu")
        if cpu_node is not None:
            cpu_node.attrib.pop("match", None)
    set_attribute(doc, ["cpu"], "check", config.get("check"))

    for feature, policy in config.get("features", []).items():
        set_attribute(doc, ["cpu", f"feature[@name='{feature}']"], "policy", policy)

    for vcpu_id, vcpuset in config.get("tuning", {}).get("vcpupin", {}).items():
        set_attribute(
            doc, ["cputune", f"vcpupin[@vcpu='{vcpu_id}']"], "cpuset", vcpuset
        )

    for cell_id, numa in config.get("numa", {}).items():
        numa_path = ["cpu", "numa", f"cell[@id='{cell_id}']"]
        set_attribute(doc, numa_path, "cpus", numa.get("cpus"))
        memory = numa.get("memory")
        if memory and memory.endswith(" MiB"):
            memory = memory.split(" ")[0]
            set_attribute(doc, numa_path, "memory", memory)
            set_attribute(doc, numa_path, "unit", "MiB")

        for sibling_id, distance in numa.get("distances", {}).items():
            set_attribute(
                doc,
                numa_path + ["distances", f"sibling[@id='{sibling_id}']"],
                "value",
                distance,
            )


def merge_numatune_config(doc, config):
    """
    Merge the NUMA tune configuration with the input XML definition ElementTree document
    """
    for attribute in ["mode", "nodeset"]:
        set_attribute(
            doc,
            ["numatune", "memory"],
            attribute,
            config.get("memory", {}).get(attribute),
        )

    for node_id, memnode in config.get("memnodes", {}).items():
        for attribute, value in memnode.items():
            set_attribute(
                doc, ["numatune", f"memnode[@cellid='{node_id}']"], attribute, value
            )


def merge_memory_config(doc, config):
    """
    Merge the memory configuration with the input XML definition ElementTree document
    """
    set_mem(doc, ["memory"], config.get("boot"))
    set_mem(doc, ["currentMemory"], config.get("current"))

    if config.get("nosharepages"):
        get_node(doc, ["memoryBacking", "nosharepages"])
    elif config.get("nosharepages") is not None:
        backing_node = doc.find("memoryBacking")
        if backing_node is not None:
            child_node = backing_node.find("nosharepages")
            if child_node is not None:
                backing_node.remove(child_node)

    for i, page in enumerate(config.get("hugepages", [])):
        set_mem_attr(
            doc,
            ["memoryBacking", "hugepages", f"page[{i + 1}]"],
            "size",
            page.get("size"),
        )


def merge_config(def_in, config):
    """
    Merge the computed configuration with the input XML definition
    """
    doc = ElementTree.fromstring(def_in)

    merge_cpu_config(doc, config.get("cpu", {}))
    merge_numatune_config(doc, config.get("numatune", {}))
    merge_memory_config(doc, config.get("mem", {}))

    if config.get("hypervisor_features", {}).get("kvm-hint-dedicated"):
        set_attribute(doc, ["features", "kvm", "hint-dedicated"], "state", "on")

    for timer_name, timer in config.get("clock", {}).get("timers", {}).items():
        for attribute, value in timer.items():
            set_attribute(
                doc, ["clock", f"timer[@name='{timer_name}']"], attribute, value
            )
    return ElementTree.tostring(doc, "utf-8")
