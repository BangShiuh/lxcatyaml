import xml.etree.ElementTree as et
import os

try:
    import ruamel_yaml as yaml  # type: ignore
except ImportError:
    from ruamel import yaml

root = et.parse(os.getcwd()+"/mycs.xml").getroot()
database = root[0]

# Get rid of namespace
for child in database:
    prefix, has_namespace, postfix = child.tag.partition('}')
    if has_namespace:
        child.tag = postfix
    print(child.tag)