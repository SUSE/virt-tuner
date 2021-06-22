"""
Test functions for the virt_tuner.virt module
"""

from unittest.mock import MagicMock
import virt_tuner.virt

CAPS = """
<capabilities>

  <host>
    <cpu>
      <arch>x86_64</arch>
      <model>Cascadelake-Server</model>
      <vendor>Intel</vendor>
      <microcode version='67121158'/>
      <counter name='tsc' frequency='2394374000' scaling='no'/>
      <topology sockets='1' cores='24' threads='2'/>
      <pages unit='KiB' size='4'/>
      <pages unit='KiB' size='2048'/>
      <pages unit='KiB' size='1048576'/>
    </cpu>
    <iommu support='no'/>
    <topology>
      <cells num='2'>
        <cell id='0'>
          <memory unit='KiB'>32646592</memory>
          <pages unit='KiB' size='4'>8161648</pages>
          <pages unit='KiB' size='2048'>0</pages>
          <pages unit='KiB' size='1048576'>0</pages>
          <distances>
            <sibling id='0' value='10'/>
            <sibling id='1' value='21'/>
          </distances>
          <cpus num='48'>
            <cpu id='0' socket_id='0' core_id='0' siblings='0,48'/>
            <cpu id='1' socket_id='0' core_id='1' siblings='1,49'/>
            <cpu id='2' socket_id='0' core_id='2' siblings='2,50'/>
            <cpu id='3' socket_id='0' core_id='3' siblings='3,51'/>
            <cpu id='4' socket_id='0' core_id='4' siblings='4,52'/>
            <cpu id='5' socket_id='0' core_id='5' siblings='5,53'/>
            <cpu id='6' socket_id='0' core_id='6' siblings='6,54'/>
            <cpu id='7' socket_id='0' core_id='9' siblings='7,55'/>
            <cpu id='8' socket_id='0' core_id='10' siblings='8,56'/>
            <cpu id='9' socket_id='0' core_id='11' siblings='9,57'/>
            <cpu id='10' socket_id='0' core_id='12' siblings='10,58'/>
            <cpu id='11' socket_id='0' core_id='13' siblings='11,59'/>
            <cpu id='12' socket_id='0' core_id='16' siblings='12,60'/>
            <cpu id='13' socket_id='0' core_id='17' siblings='13,61'/>
            <cpu id='14' socket_id='0' core_id='18' siblings='14,62'/>
            <cpu id='15' socket_id='0' core_id='19' siblings='15,63'/>
            <cpu id='16' socket_id='0' core_id='20' siblings='16,64'/>
            <cpu id='17' socket_id='0' core_id='21' siblings='17,65'/>
            <cpu id='18' socket_id='0' core_id='24' siblings='18,66'/>
            <cpu id='19' socket_id='0' core_id='25' siblings='19,67'/>
            <cpu id='20' socket_id='0' core_id='26' siblings='20,68'/>
            <cpu id='21' socket_id='0' core_id='27' siblings='21,69'/>
            <cpu id='22' socket_id='0' core_id='28' siblings='22,70'/>
            <cpu id='23' socket_id='0' core_id='29' siblings='23,71'/>
            <cpu id='48' socket_id='0' core_id='0' siblings='0,48'/>
            <cpu id='49' socket_id='0' core_id='1' siblings='1,49'/>
            <cpu id='50' socket_id='0' core_id='2' siblings='2,50'/>
            <cpu id='51' socket_id='0' core_id='3' siblings='3,51'/>
            <cpu id='52' socket_id='0' core_id='4' siblings='4,52'/>
            <cpu id='53' socket_id='0' core_id='5' siblings='5,53'/>
            <cpu id='54' socket_id='0' core_id='6' siblings='6,54'/>
            <cpu id='55' socket_id='0' core_id='9' siblings='7,55'/>
            <cpu id='56' socket_id='0' core_id='10' siblings='8,56'/>
            <cpu id='57' socket_id='0' core_id='11' siblings='9,57'/>
            <cpu id='58' socket_id='0' core_id='12' siblings='10,58'/>
            <cpu id='59' socket_id='0' core_id='13' siblings='11,59'/>
            <cpu id='60' socket_id='0' core_id='16' siblings='12,60'/>
            <cpu id='61' socket_id='0' core_id='17' siblings='13,61'/>
            <cpu id='62' socket_id='0' core_id='18' siblings='14,62'/>
            <cpu id='63' socket_id='0' core_id='19' siblings='15,63'/>
            <cpu id='64' socket_id='0' core_id='20' siblings='16,64'/>
            <cpu id='65' socket_id='0' core_id='21' siblings='17,65'/>
            <cpu id='66' socket_id='0' core_id='24' siblings='18,66'/>
            <cpu id='67' socket_id='0' core_id='25' siblings='19,67'/>
            <cpu id='68' socket_id='0' core_id='26' siblings='20,68'/>
            <cpu id='69' socket_id='0' core_id='27' siblings='21,69'/>
            <cpu id='70' socket_id='0' core_id='28' siblings='22,70'/>
            <cpu id='71' socket_id='0' core_id='29' siblings='23,71'/>
          </cpus>
        </cell>
        <cell id='1'>
          <memory unit='KiB'>32982940</memory>
          <pages unit='KiB' size='4'>8245735</pages>
          <pages unit='KiB' size='2048'>0</pages>
          <pages unit='KiB' size='1048576'>0</pages>
          <distances>
            <sibling id='0' value='21'/>
            <sibling id='1' value='10'/>
          </distances>
          <cpus num='48'>
            <cpu id='24' socket_id='1' core_id='0' siblings='24,72'/>
            <cpu id='25' socket_id='1' core_id='1' siblings='25,73'/>
            <cpu id='26' socket_id='1' core_id='2' siblings='26,74'/>
            <cpu id='27' socket_id='1' core_id='3' siblings='27,75'/>
            <cpu id='28' socket_id='1' core_id='4' siblings='28,76'/>
            <cpu id='29' socket_id='1' core_id='5' siblings='29,77'/>
            <cpu id='30' socket_id='1' core_id='6' siblings='30,78'/>
            <cpu id='31' socket_id='1' core_id='8' siblings='31,79'/>
            <cpu id='32' socket_id='1' core_id='9' siblings='32,80'/>
            <cpu id='33' socket_id='1' core_id='10' siblings='33,81'/>
            <cpu id='34' socket_id='1' core_id='11' siblings='34,82'/>
            <cpu id='35' socket_id='1' core_id='12' siblings='35,83'/>
            <cpu id='36' socket_id='1' core_id='13' siblings='36,84'/>
            <cpu id='37' socket_id='1' core_id='16' siblings='37,85'/>
            <cpu id='38' socket_id='1' core_id='17' siblings='38,86'/>
            <cpu id='39' socket_id='1' core_id='18' siblings='39,87'/>
            <cpu id='40' socket_id='1' core_id='19' siblings='40,88'/>
            <cpu id='41' socket_id='1' core_id='20' siblings='41,89'/>
            <cpu id='42' socket_id='1' core_id='21' siblings='42,90'/>
            <cpu id='43' socket_id='1' core_id='25' siblings='43,91'/>
            <cpu id='44' socket_id='1' core_id='26' siblings='44,92'/>
            <cpu id='45' socket_id='1' core_id='27' siblings='45,93'/>
            <cpu id='46' socket_id='1' core_id='28' siblings='46,94'/>
            <cpu id='47' socket_id='1' core_id='29' siblings='47,95'/>
            <cpu id='72' socket_id='1' core_id='0' siblings='24,72'/>
            <cpu id='73' socket_id='1' core_id='1' siblings='25,73'/>
            <cpu id='74' socket_id='1' core_id='2' siblings='26,74'/>
            <cpu id='75' socket_id='1' core_id='3' siblings='27,75'/>
            <cpu id='76' socket_id='1' core_id='4' siblings='28,76'/>
            <cpu id='77' socket_id='1' core_id='5' siblings='29,77'/>
            <cpu id='78' socket_id='1' core_id='6' siblings='30,78'/>
            <cpu id='79' socket_id='1' core_id='8' siblings='31,79'/>
            <cpu id='80' socket_id='1' core_id='9' siblings='32,80'/>
            <cpu id='81' socket_id='1' core_id='10' siblings='33,81'/>
            <cpu id='82' socket_id='1' core_id='11' siblings='34,82'/>
            <cpu id='83' socket_id='1' core_id='12' siblings='35,83'/>
            <cpu id='84' socket_id='1' core_id='13' siblings='36,84'/>
            <cpu id='85' socket_id='1' core_id='16' siblings='37,85'/>
            <cpu id='86' socket_id='1' core_id='17' siblings='38,86'/>
            <cpu id='87' socket_id='1' core_id='18' siblings='39,87'/>
            <cpu id='88' socket_id='1' core_id='19' siblings='40,88'/>
            <cpu id='89' socket_id='1' core_id='20' siblings='41,89'/>
            <cpu id='90' socket_id='1' core_id='21' siblings='42,90'/>
            <cpu id='91' socket_id='1' core_id='25' siblings='43,91'/>
            <cpu id='92' socket_id='1' core_id='26' siblings='44,92'/>
            <cpu id='93' socket_id='1' core_id='27' siblings='45,93'/>
            <cpu id='94' socket_id='1' core_id='28' siblings='46,94'/>
            <cpu id='95' socket_id='1' core_id='29' siblings='47,95'/>
          </cpus>
        </cell>
      </cells>
    </topology>
    <cache>
      <bank id='0' level='3' type='both' size='36608' unit='KiB' cpus='0-23,48-71'/>
      <bank id='1' level='3' type='both' size='36608' unit='KiB' cpus='24-47,72-95'/>
    </cache>
  </host>
</capabilities>
"""


def test_host_topology():
    """
    test the virt.host_topology() function
    """
    libvirt_mock = MagicMock()
    libvirt_mock.open.return_value.getCapabilities.return_value = CAPS
    virt_tuner.virt.libvirt = libvirt_mock

    topology = virt_tuner.virt.host_topology()
    assert len(topology) == 2
    assert len(topology[0].cpus) == 48
    assert topology[0].id == 0
    assert topology[0].cpus[0] == {
        "id": "0",
        "socket_id": "0",
        "core_id": "0",
        "siblings": "0,48",
    }
    assert topology[1].memory == "32982940 KiB"
    assert topology[0].distances == {0: 10, 1: 21}
    assert topology[0].pages == [
        {"size": "4 KiB", "count": 8161648},
        {"size": "2048 KiB", "count": 0},
        {"size": "1048576 KiB", "count": 0},
    ]


def test_host_memory():
    """
    test the virt.host_memory() function
    """
    libvirt_mock = MagicMock()
    libvirt_mock.open.return_value.getInfo.return_value = [
        "x86_64",
        31944,
        8,
        2700,
        1,
        1,
        4,
        2,
    ]
    virt_tuner.virt.libvirt = libvirt_mock
    assert virt_tuner.virt.host_memory() == 31944
