import xml.etree.ElementTree as ET
tree = ET.parse('dbpedia_2016-10.owl')
root = tree.getroot()


datatype_properties = []
object_properties = []

for child in root.getchildren():
    prop = child.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'] + '\n'
    if 'datatypeproperty' in child.tag.lower():
        datatype_properties.append(prop)  
    elif 'objectproperty' in child.tag.lower():
        object_properties.append(prop)

with open('dp.csv', 'w+') as dpf:
    dpf.writelines(datatype_properties)
with open('op.csv', 'w+') as opf:
    opf.writelines(object_properties)

pass
