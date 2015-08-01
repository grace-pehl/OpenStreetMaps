import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


### can use this function to look through data
OSMFILE = "Project.osm"
search_key = "religion"     

def audit(osmfile):
    osm_file = open(osmfile, "r")
    key_values = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == search_key:
                    key_values[search_key].add(tag.attrib['v'])

    return key_values


def test():
    key_values = audit(OSMFILE)
#    assert len(st_types) == 3
    pprint.pprint(dict(key_values))


if __name__ == '__main__':
    test()