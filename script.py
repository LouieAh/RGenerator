import overpy
import requests
import sys
import xml.etree.ElementTree as ET

api = overpy.Overpass()
# openrouteservice Personal api key
ors_api_key = "5b3ce3597851110001cf6248d3d35cb32ca94583a5de11210978d5ac"

# Speed trace hardcoded list for prototype
turn_distances = [150, 2010, 3067, 3456]

# Nodes comprising of route taken
route_nodes = []

def ways_from_xml(xml_string):
    ways = []
    xml_root = ET.fromstring(xml_string)
    # Iterate over children
    for x in xml_root:
        if x.tag == 'way':
            ways.append(x)
    return ways

# Get way(s) of starting node
def ways_of_node(node_id):
    # query = """
    #     node({0});
    #     way(bn);
    #     out body;
    # """
    # #print(query.format(id))
    # formatted_query = query.format(node_id)
    # result = api.query(formatted_query)
    # return result.ways
    url = 'http://overpass-api.de/api/interpreter'
    query_template = 'node({0});way(bn);out;'
    query = query_template.format(node_id)
    response = requests.post(url, data = query)
    return ways_from_xml(response.text)

def nodes_from_xml(xml_string):
    nodes = []
    xml_root = ET.fromstring(xml_string)
    # Iterate over children
    for x in xml_root:
        if x.tag == 'way':
            # Iterate over way tag
            for y in x:
                if y.tag == 'nd':
                    nodes.append(y)
    return nodes

# Get nodes within a way
def nodes_of_way(way_id):
    # query = """
    #     way({0});
    #     (._;>;);
    #     out body;
    # """
    # formatted_query = query.format(way_id)
    # way_obj = api.query(formatted_query)
    # return way_obj.nodes
    url = 'http://overpass-api.de/api/interpreter'
    query_template = 'way({0});(._;>;);out;'
    query = query_template.format(way_id)
    response = requests.post(url, data = query)
    return nodes_from_xml(response.text)

# ways = getWaysFromNodeId(2387213896)
#
# # For each way
# for way in ways:
#
#     # Get nodes in way
#     way_id = way.id
#     way_nodes = getNodesWithinWay(way_id)
#
#     # For each node in way
#     for node in way_nodes:
#
#         # if node is part of 3 or more ways
#         if (len(getWaysFromNodeId(node.id)) > 1):
#
#             # Get lat,long of that node
#             # Convert to float to be of same type as start lat and long
#             lat = float(node.lat)
#             long = float(node.lon)
#
#             if (lat != start_lat and long != start_long):
#
#                 # Get route distance between that node and starting node
#                 api_call = """\
#                 https://api.openrouteservice.org\
#                 /v2/directions/driving-hgv\
#                 ?api_key={0}\
#                 &start={1},{2}&end={3},{4}\
#                 """
#                 formatted_api_call =\
#                     api_call.format(ors_api_key, start_long, start_lat, long, lat)
#
#                 # Remove spaces
#                 formatted_api_call = formatted_api_call.replace(" ","")
#
#                 #print(formatted_api_call)
#                 response = requests.get(formatted_api_call)
#
#                 #print(response)
#                 response_json = response.json()
#
#                 distance = response_json["features"][0]["properties"]["summary"]["distance"]
#                 print(distance)
#     print("----")
#     break

def node_ids_from_nodes(nodes):
    node_ids = []
    for node in nodes:
        node_ids.append(int(node.attrib['ref']))
    return node_ids

def local_neighbour_nodes(node_id, way_id):
    way_neighbour_nodes = []

    way_nodes = nodes_of_way(way_id)
    way_node_ids = node_ids_from_nodes(way_nodes)

    # Get index of node_id within way_node_ids
    index = way_node_ids.index(node_id)
    node_list_size = len(way_node_ids)

    # If node is only node in way
    if (len(way_nodes) == 1):
        # Return empty list
        return way_neighbour_nodes
    # If only one other node in way
    elif (len(way_nodes) == 2):
        # Return node at index XOR to node
        xor_index = 1 - index
        other = way_node_ids[xor_index]
        way_neighbour_nodes.append(other)
    else:
        # If node is first in way
        if (index == 0):
            # Return only node after
            after = way_node_ids[index + 1]
            way_neighbour_nodes.append(after)
        # If node is last in way
        elif (index == node_list_size - 1):
            # Return only node before
            before = way_node_ids[index - 1]
            way_neighbour_nodes.append(before)
        else:
            before = way_node_ids[index - 1]
            after = way_node_ids[index + 1]
            way_neighbour_nodes.append(before)
            way_neighbour_nodes.append(after)
    return way_neighbour_nodes

def way_id(way):
    way_id = int(way.attrib["id"])
    return way_id

def global_neighbour_nodes(node_id):
    neighbour_nodes = []
    # Get ways
    ways = ways_of_node(node_id)

    for way in ways:
        # Merge the returned list with nodes[] list
        neighbour_nodes += local_neighbour_nodes(node_id, way_id(way))
    print(neighbour_nodes)
    sys.exit()

def next_node(start_node_id):
    # Get all neighbour nodes
    nodes = global_neighbour_nodes(start_node_id)

def route(start_node_id):
    # Clear any nodes already in route_nodes[] list
    route_nodes.clear()
    # Get next node
    route_nodes.append(next_node(start_node_id))

def start():
    #node = start_node(lat, long)
    #route(node)
    route(8336028505)

start()
