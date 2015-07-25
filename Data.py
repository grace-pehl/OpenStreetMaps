#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import codecs
import json
from pymongo import MongoClient

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
expected_street_types = ["Street", "Avenue", "Boulevard", "Drive", "Court", 
                         "Place", "Way", "Square", "Lane", "Road", "Trail", 
                         "Parkway", "Commons", "Terrace", "Highway", "Circle", 
                         "Southeast", "Southwest"]

def update_street(name, street_type):
    mapping = { "St": "Street", "St.": "Street", "Ave": "Avenue", "ave": "Avenue",
                "Rd.": "Road", "Pl": "Place", "Ct": "Court", "Dr.": "Drive",
                "Dr": "Drive", "Blvd": "Boulevard", "BLVD": "Boulevard",
                "SE": "Southeast"}
    if street_type in mapping:
        better_street_type = mapping[street_type]
        street_name = name[:-len(street_type)]
        name = street_name + better_street_type
    return name
    
def clean_addr(key, value):
    # clean the street type
    if key == "addr:street":
        street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
        m = street_type_re.search(value)
        if m:
            street_type = m.group()
            if street_type not in expected_street_types:
                value = update_street(value, street_type)
    # programmatically clean the state value
    if key == "addr:state" & value == "Florida":
        value = "FL"
    if key == "addr:city" & value == "Hobe Sound, FL":
        value = "Hobe Sound"
    return value

def shape_element(element):
    node = {}
    pos = [0.0, 0.0]
    cr = {}
    address = {}
    node_refs = []
    # you should process only 2 types of top level tags: "node" and "way"
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        for atr in element.attrib:
            key = atr
            value = element.get(key)
            # attributes in the CREATED array should be added under a key "created"
            if key in CREATED:
                cr[key] = value
            # attributes for latitude and longitude should be added to a "pos" array,
            # for use in geospacial indexing. Make sure the values inside "pos" 
            # array are floats and not strings.
            elif key == "lat":
                pos[0] = float(value)
            elif key == "lon":
                pos[1] = float(value)
            # all attributes of "node" and "way" should be turned into regular key/value pairs,
            else:
                node[key] = value
        for child in element:
            # for "way" specifically, add 'ref' to list node_refs
            if child.tag == "nd":
                node_refs.append(child.get('ref'))
            if child.tag == "tag":
                # if second level tag "k" value contains problematic characters, ignore it
                try:
                    key = child.get('k')
                    value = child.get('v')
                    # if "k" value starts with "addr:", it should be added to a dictionary "address"
                    if key.startswith("addr:"):
                        # do some cleaning on the address
                        value = clean_addr(key, value)
                        # remove "addr:" from the key
                        key = key[5:]
                        # if there is a second ":" that separates the type/direction of a street, the tag should be ignored
                        if ':' in key:
                            pass
                        else:
                            address[key] = value
                    # if second level tag "k" value does not start with "addr:",
                    # but contains ":", you can process it same as any other tag.
                    else:
                        node[key] = value
                except:
                    pass
        if address != {}:
            node['address'] = address
        if pos != [0.0, 0.0]:
            node['pos'] = pos
        if node_refs != []:
            node['node_refs'] = node_refs
        if cr != {}:
            node['created'] = cr
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option 
    # adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('Project.osm', False)
    client = MongoClient("mongodb://localhost:27017")
    db = client.pehl
    db.osm.insert(data)
    print db.osm.find_one()

if __name__ == "__main__":
    test()