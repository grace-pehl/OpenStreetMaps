# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 14:42:06 2015
@author: Grace Pehl, PhD

Make a text file of the unique keys in the data.
"""
import xml.etree.cElementTree as ET

def key_types(filename):
    keys = set()
    for _, element in ET.iterparse(filename):
        if element.tag == 'tag':
            keys.add(element.attrib['k'])
    
    print len(keys)
    
    with open("keys.txt", "wb") as cfile:
        for key in keys:
            k= key + "," + "\n"
            cfile.write(k)

if __name__ == "__main__":
    key_types("Project.osm")