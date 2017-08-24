# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 07:18:40 2017

@author: Subash Bharadwaj
"""


import xml.etree.cElementTree as ET # Iterative Parsing
import pprint # Printing output in a readable format
from collections import defaultdict # dictionary format
import re # For regular expressions
import schema # To validate against a schema
import csv # to write to CSV files
import codecs # CSV writer
import cerberus # Validation against a schema
import sqlite3 # SQL commands in Python

# Sample File
filename = "C:/Users/Subash Bharadwaj/Desktop/sample2.osm"

# Full data file
#filename = "C:/Users/Subash Bharadwaj/Desktop/boston_ma/boston_massachusetts.osm"

# Regular Expressions:
# Pin Code has to be all numbers and some pin codes can be zip+4 format with a hyphen
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
pin_code_type_re = re.compile(r'\d+\-?\d*$', re.IGNORECASE)
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

NODES_PATH = "C:/Users/Subash Bharadwaj/Desktop/nodes.csv"
NODE_TAGS_PATH = "C:/Users/Subash Bharadwaj/Desktop/nodes_tags.csv"
WAYS_PATH = "C:/Users/Subash Bharadwaj/Desktop/ways.csv"
WAY_NODES_PATH = "C:/Users/Subash Bharadwaj/Desktop/ways_nodes.csv"
WAY_TAGS_PATH = "C:/Users/Subash Bharadwaj/Desktop/ways_tags.csv"

schema = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

mapping = {'Ave': 'Avenue',
           'Ave.': 'Avenue',
           'Ct': 'Court',
           'Dr': 'Driveway',
           'Drive': 'Driveway',
           'floor': 'Floor',
           'H': 'Hall',
           'Hwy': 'Highway',
           'Hwy.': 'Highway',
           'HIghway': 'Highway',
           'Park': 'Parkway',
           'Pkwy': 'Parkway',
           'Pkwy.': 'Parkway',
           'Pl': 'Place',
           'place': 'Place',
           'Rd': 'Road',
           'Rd.': 'Road',
           'rd.': 'Road',
           'Sq.': 'Square',
           'St': 'Street',
           'St.': 'Street',
           'ST': 'Street',
           'St,': 'Street',
           'st': 'Street',
           'street': 'Street',
           'Street.': 'Street',
           'Winsor': 'Windsor'
           }

###### This section contains all the functions used in this program

# To display the dictionary in a visually clear sorted format
def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print '%s : %d' %(k, v)

# To adjust the street names and make them aligned across the dataset
def update_name(street_name, mapping):
# Split the stret name into parts and replace the last part based on the mapping
    x = street_name.split(" ")
    old = x[len(x)-1]
    try:
        street_name = street_name.replace(old, mapping[old])
        return street_name
# The below case is used to fix errors in street names
# where they're of the form ABC Street #501 or ABC Street,501
    except KeyError:
        y = re.split(',|#', street_name)
        return y[0]

# To adjust the postal code into standard 5 digit format
def update_postal_code(postal_code):
    postal_code = postal_code.split("-")[0]
    return postal_code

# To map the data from the dataset into a format convenient for saving as CSV
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
# Secondary Tags
    tags = []  

    if element.tag == 'node':
        for attribs in element.attrib:
            node_attribs[attribs] = element.attrib[attribs]
        
        for tag in element.iter('tag'):
            if re.search(LOWER_COLON, tag.attrib['k']):
# If the attribute has multiple : operators, then split at the first one
                x = tag.attrib['k'].split(':', 1)
                tags1 = {}
                tags1['id'] = element.attrib['id']
                tags1['key'] = x[1]
# If the street name needs some correction, adjust it based on the mapping
                if tag.attrib['k'] == 'addr:street':
                    tags1['value'] = update_name(tag.attrib['v'], mapping)
# If the postal code is not in Zip/Zip+4 format ignore the entry, else modify it
                elif tag.attrib['k'] == 'addr:postcode':
                    if tag.attrib['v'] not in postal_types:
                        continue
                    else:
                        tags1['value'] = update_postal_code(tag.attrib['v'])
                else:
                    tags1['value'] = tag.attrib['v']
                
                tags1['type'] = x[0]
                tags.append(tags1)
# If the attribute has problematic characters, then ignore it
            elif re.search(PROBLEMCHARS, tag.attrib['k']):
                pass
            else:
                tags1 = {}
                tags1['id'] = element.attrib['id']
                tags1['key'] = tag.attrib['k']
# If the postal code is not in Zip/Zip+4 format ignore the entry, else modify it
                if tag.attrib['k'] == 'postal_code': 
                    if tag.attrib['v'] not in postal_types:
                        continue
                    else:
                        tags1['value'] = update_postal_code(tag.attrib['v'])
                else:
                    tags1['value'] = tag.attrib['v']
                tags1['type'] = 'regular'
                tags.append(tags1)
    elif element.tag == 'way':
        for attribs in element.attrib:
            way_attribs[attribs] = element.attrib[attribs]
        
        for tag in element.iter('tag'):
            if re.search(LOWER_COLON, tag.attrib['k']):
# If the attribute has multiple : operators, then split at the first one
                x = tag.attrib['k'].split(':', 1)
                tags1 = {}
                tags1['id'] = element.attrib['id']
                tags1['key'] = x[1]
                if tag.attrib['k'] == 'addr:street':
                    tags1['value'] = update_name(tag.attrib['v'], mapping)
# If the postal code is not in Zip/Zip+4 format ignore the entry, else modify it
                elif tag.attrib['k'] == 'addr:postcode':
                    if tag.attrib['v'] not in postal_types:
                        continue
                    else:
                        tags1['value'] = update_postal_code(tag.attrib['v'])
                else:
                    tags1['value'] = tag.attrib['v']
                tags1['type'] = x[0]
                tags.append(tags1)
            elif re.search(PROBLEMCHARS, tag.attrib['k']):
                pass
            else:
                tags1 = {}
                tags1['id'] = element.attrib['id']
                tags1['key'] = tag.attrib['k']
# If the postal code is not in Zip/Zip+4 format ignore the entry, else modify it
                if tag.attrib['k'] == 'postal_code': 
                    if tag.attrib['v'] not in postal_types:
                        continue
                    else:
                        tags1['value'] = update_postal_code(tag.attrib['v'])
                else:
                    tags1['value'] = tag.attrib['v']
                tags1['type'] = 'regular'
                tags.append(tags1)
        counter = 0
        for tag in element.iter('nd'):
            tags1 = {}
            tags1['id'] = element.attrib['id']
            tags1['node_id'] = tag.attrib['ref']
            tags1['position'] = counter
# To capture the position of the node
            counter += 1
            way_nodes.append(tags1)
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    
# To validate the dictionary structure against the schema
def validate_element(element, validator, schema=schema):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

tagdict = defaultdict(int)        
street_types = defaultdict(int)
postal_types = defaultdict(int)
validator = cerberus.Validator()

for event, elem in ET.iterparse(filename):
# List of highest level tags in the xml file
    tagdict[elem.tag] += 1
# List of street type names such as: Street, Way, Driveway, Place etc.
    if elem.tag == 'tag' and elem.attrib['k'] == 'addr:street':
        m = street_type_re.search(elem.attrib['v'])
        if m:
            street_type = m.group()
            street_types[street_type] += 1
# List of Postal Codes (5 digit zip codes and zip+4 codes)    
    if elem.tag == 'tag' and (elem.attrib['k'] == 'postal_code' or elem.attrib['k'] == 'addr:postcode'):
        m = pin_code_type_re.search(elem.attrib['v'])
        if m:
            postal_type = m.group()
            postal_types[postal_type] += 1
    
# Print out the tag types, street types and postal code types             
print_sorted_dict(tagdict)
print_sorted_dict(street_types)
print_sorted_dict(postal_types)
#Set equal to True to validate the CSV file structure against the schema
validate = False

# Open CSV Files
with codecs.open(NODES_PATH, 'w') as nodes_file, \
     codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
     codecs.open(WAYS_PATH, 'w') as ways_file, \
     codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
     codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

# To handle Unicode input
    nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
    node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
    ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
    way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
    way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

#Commented out because SQL command to store data in table cannot account
#for header information in the csv file and throws an error for the first row

    #nodes_writer.writeheader()
    #node_tags_writer.writeheader()
    #ways_writer.writeheader()
    #way_nodes_writer.writeheader()
    #way_tags_writer.writeheader()

    for event, elem in ET.iterparse(filename, events = ('start', 'end')):
        if event == 'end' and elem.tag in ('node', 'way'):
            el = shape_element(elem)
            if el:
                if validate is True:
                    validate_element(el, validator)
# Write down to CSV file
            if elem.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
            elif elem.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
    
# SQL Table creation
db = sqlite3.connect('osmproject.db')
c = db.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY NOT NULL,
    lat REAL,
    lon REAL,
    user TEXT,
    uid INTEGER,
    version INTEGER,
    changeset INTEGER,
    timestamp TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS nodes_tags (
    id INTEGER,
    key TEXT,
    value TEXT,
    type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS ways (
    id INTEGER PRIMARY KEY NOT NULL,
    user TEXT,
    uid INTEGER,
    version TEXT,
    changeset INTEGER,
    timestamp TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS ways_tags (
    id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS ways_nodes (
    id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id))''')

db.commit()