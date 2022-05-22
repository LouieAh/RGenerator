import requests
import sys

# Speed trace hardcoded list for prototype
turn_distances = [150, 2010, 3067, 3456]

# Nodes comprising of route taken
route_nodes = []

def get_node_id(node):
    return node["id"]

# Parse the JSON response to the API call made within the ways_of_node()
# function for the way objects
def ways_of_node_parser(response):
    ways = []
    for element in response["elements"]:
        if (element["type"] == "way"):
            ways.append(element)
    return ways

# Given a node, return the ways that that node is part of by using the
# Overpass API
def ways_of_node(node):
    url = 'http://overpass-api.de/api/interpreter'
    # Query the Overpass API to return all ways that node is part of
    query_template = '[out:json];node({0});way(bn);out;'
    # Substitute {0} for the ID of node
    query = query_template.format(get_node_id(node))
    # Make a POST request to the API, with query as the POST data
    response = requests.post(url, data = query)
    return ways_of_node_parser(response.json())

# Take the JSON object response to the nodes_of_way request and parses it
# to return the an ordered list of the nodes
def nodes_of_way_parser(json):
    nodes = []
    ordered_node_ids = []
    nodeId_node_dict = {}
    # For each element within json
    for element in json["elements"]:
        # If the element is a node element
        if (element["type"] == "node"):
            # Create a new entry to node_dict in the form of
            # <node id> : <node object>
            nodeId_node_dict[element['id']] = element
        # If the element is a way element
        elif (element['type'] == 'way'):
            # Add the node ids from json to ordered_node_ids[]
            ordered_node_ids += element['nodes']

    # For each node ID in ordered_node_ids[], do a lookup in nodeId_node_dict{}
    # for the corresponding node and append that node to nodes[]
    for id in ordered_node_ids:
        nodes.append(nodeId_node_dict[id])

    return nodes

def get_way_id(way):
    return way["id"]

# Get nodes within a way
def nodes_of_way(way):
    url = 'http://overpass-api.de/api/interpreter'
    #query_template_xml = 'way({0});(._;>;);out;'
    query_template = '[out:json];way({0});(._;>;);out;'
    query = query_template.format(get_way_id(way))
    response = requests.post(url, data = query)
    #return nodes_from_xml(response.text)
    return nodes_of_way_parser(response.json())

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

# Given a node and the way its part of, return the neighbour nodes
def local_neighbour_nodes(node, way):
    # The list of nodes that will be returned
    way_neighbour_nodes = []
    # Get the nodes of way
    way_nodes = nodes_of_way(way)
    # Create a new list by replacing each node in way_nodes with the node's ID
    way_node_ids = []
    for nd in way_nodes:
        way_node_ids.append(get_node_id(nd))

    # Retrieve the index of node from the way_node_ids[] list
    node_index = way_node_ids.index(get_node_id(node))

    way_nodes_size = len(way_nodes)

    # Given the node_index and how many nodes are within way_nodes, add the
    # neighbour nodes to way_neighbour_nodes[].
    # If node is the only node in way
    if (way_nodes_size == 1):
        # Return an empty list as node has no neighbours
        return way_neighbour_nodes
    # If there are only two nodes in way
    elif (way_nodes_size == 2):
        # Add the node that has index 0 if node_index is 1, or index 1 if
        # node_index is 0
        way_neighbour_nodes.append(way_node_ids[1 - node_index])
    else:
        # When there are 3 or more nodes in the way and...
        # Node is at index 0
        if (node_index == 0):
            # Add the second node
            way_neighbour_nodes.append(way_node_ids[node_index + 1])
        # Node is at the last index
        elif (node_index == way_nodes_size - 1):
            # Add the node before
            way_neighbour_nodes.append(way_node_ids[node_index - 1])
        # Node is sandwiched between two other nodes
        else:
            # Add the nodes immediately before and after
            way_neighbour_nodes.append(way_node_ids[node_index - 1])
            way_neighbour_nodes.append(way_node_ids[node_index + 1])
    return way_neighbour_nodes

# Given a list of ways, return only the ways with a key of highway
def get_highway_ways(ways):
    # The 'highway' key values for ways a vehicle can travel along
    # Source: https://wiki.openstreetmap.org/wiki/Key:highway
    suitable_ways = [
        'motorway', 'trunk', 'primary', 'seconday', 'tertiary',
        'unclassified', 'residential', 'motorway_link', 'trunk_link',
        'primary_link', 'secondary_link', 'tertiary_link', 'service',
        'pedestrian', 'track', 'escape', 'road', 'rest_area', 'services'
    ]
    returned_ways = []
    for way in ways:
        if (way['tags']['highway'] in suitable_ways):
            returned_ways.append(way)
    return returned_ways

# Return all neighbour nodes from each way that node is part of
def global_neighbour_nodes(node):
    # A list of the neighbour nodes from each way that node is part of
    neighbour_nodes = []
    # Get all ways that node is part of
    ways = ways_of_node(node)
    highway_ways = get_highway_ways(ways)
    # For each way that node is part of, append each neighbour node to
    # the neighbour_nodes[] list
    for way in ways:
        neighbour_nodes += local_neighbour_nodes(node, way)

    return neighbour_nodes

# This function will evaluate what the best fitting next node is based on
# the distance to the turn based on the speed trace data
def get_next_node(node):
    # Get all neighbour nodes
    nodes = global_neighbour_nodes(node)
    # for each node in nodes calculate route distance
    # and compare with distance to next speed drop
    return

def route(node):
    # Clear any nodes already in route_nodes[] list
    route_nodes.clear()
    # Get next node
    next_node = get_next_node(node)

def start():
    #node = start_node(lat, long)
    #route(node)
    # test_node = {
    #     "type": "node",
    #     "id": 8336028505,
    #     "lat": 51.5134746,
    #     "lon": -0.0999181
    #     }
    # test_node = {
    #     "type": "node",
    #     "id": 107685,
    #     "lat": 51.5139944,
    #     "lon": -0.1025298
    # }
    test_node = {
        "type": "node",
        "id": 1726730165,
        "lat": 51.5134571,
        "lon": -0.0998721,
        "tags": {
            "crossing": "unmarked",
            "highway": "crossing"
        }
    }
    route(test_node)

start()
