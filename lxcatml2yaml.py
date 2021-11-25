from pathlib import Path
import xml.etree.ElementTree as etree
import os
import re
import sys
try:
    import ruamel_yaml as yaml
except ImportError:
    from ruamel import yaml

BlockMap = yaml.comments.CommentedMap

# A class of yaml data for collision of a target species
class Process:
    def __init__(self, kind, equation, threshold, data_x, data_y):
        self.attribs = BlockMap({})
        self.attribs["kind"] = kind
        self.attribs["equation"] = equation
        self.attribs["threshold"] = threshold
        self.attribs["electron-energy-data"] = data_x
        self.attribs["cross-section-data"] = data_y

    @classmethod
    def to_yaml(cls, representer, data):
        """Serialize the class instance to YAML format suitable for ruamel.yaml.

        :param representer:
            An instance of a ruamel.yaml representer type.
        :param data:
            An instance of this class that will be serialized.

        The class instance should have an instance attribute called ``attribs`` which
        is a dictionary representing the information about the instance. The dictionary
        is serialized using the ``represent_dict`` method of the ``representer``.
        """
        return representer.represent_dict(data.attribs)

# Return indices of a child name
def get_children(parent, child_name):
    indices = []
    for i, child in enumerate(parent):
        if child.tag.find(child_name) != -1:
            indices.append(i)
    return [parent[x] for x in indices]

def FlowList(*args, **kwargs):
    """A YAML sequence that flows onto one line."""
    lst = yaml.comments.CommentedSeq(*args, **kwargs)
    lst.fa.set_flow_style()
    return lst

def main():
    # Define yaml emitter
    emitter = yaml.YAML()
    emitter.register_class(Process)

    root = etree.parse(os.getcwd()+"/mycs.xml").getroot()
    database = root[0]

    # Get groups node
    groups_node = get_children(database, "groups")[0]

    process_list = []
    for group in groups_node:   
        for process in get_children(group, "processes")[0]:
            # Target
            target = group.attrib["id"]

            # Collision type
            kind=process.attrib["collisionType"]
            if process.attrib["collisionType"] == "inelastic":
                kind = process.attrib["inelasticType"]

            # Threshold
            threshold = 0.0
            parameters_node = get_children(process, "parameters")[0]
            if len(get_children(parameters_node, "parameter")) == 1:
                parameter = get_children(parameters_node, "parameter")[0]
                if parameter.attrib["name"] == 'E':
                    threshold = "{0:.4f}".format(float(parameter.text))
                    threshold = str(threshold) + " " + parameter.attrib["units"]

            # Equation
            product_array=[]
            for product_node in get_children(process, "products")[0]:
                if product_node.tag.find("electron") != -1:
                    product_array.append("e")
                if product_node.tag.find("molecule") != -1:
                    product_name = product_node.text
                    if "state" in product_node.attrib:
                        state = product_node.attrib["state"]
                        product_name += f"({state})"
                    if "charge" in product_node.attrib:
                        charge = int(product_node.attrib["charge"])
                        if charge > 0:
                            product_name += charge*"+"
                        else:
                            product_name += -charge*"-"
                    product_array.append(product_name)

            products = " + ".join(product_array)
            equation = f"{target} + e => {products}"

            # Data
            data_x = str(get_children(process, "data_x")[0].text)
            data_x = data_x.split(" ")
            data_x = FlowList(map(float, data_x))

            data_y = str(get_children(process, "data_y")[0].text)
            data_y = data_y.split(" ")
            data_y = FlowList(map(float, data_y))

            # Save process
            process_list.append(Process(kind=kind,
                                        equation=equation,
                                        threshold=threshold,
                                        data_x=data_x,
                                        data_y=data_y))

    # Put process list in collision node
    collision_node = {"electron-collisions": process_list}

    # Add unit
    units_node = {"units": FlowList([{"length": "m"}, {"electron-energy": "eV"}])}

    with Path("mycs.yaml").open("w") as output_file:
        emitter.dump(units_node, output_file)
        emitter.dump(collision_node, output_file)

if __name__ == "__main__":
    main()
