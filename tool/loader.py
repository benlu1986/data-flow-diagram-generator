from utils import key_with_suffix
from node import convert
import json
from node import Node
from node import NodeType

def load_node_from_json(node_json_file):
  with open(node_json_file, 'r') as f:
    node_json_dict_list = json.load(f)

  node_dict = {}
  for node_json_dict in node_json_dict_list:
    current_node_name = node_json_dict['name']
    current_node_nodeType = NodeType[node_json_dict['nodeType']]
    parent_or_child_nodeType = NodeType.SERVICE if current_node_nodeType == NodeType.TOPIC else NodeType.TOPIC
    current_node_key = key_with_suffix(current_node_nodeType, current_node_name)
    current_node = None
    if current_node_key not in node_dict:
      current_node = Node(current_node_nodeType ,current_node_name)
      node_dict[current_node_key] = current_node
    else:
      current_node = node_dict[current_node_key]
    __build_related_node_from_json(node_json_dict['parent'], current_node.parent, parent_or_child_nodeType, node_dict)
    __build_related_node_from_json(node_json_dict['child'], current_node.child, parent_or_child_nodeType, node_dict)
  return node_dict

def __build_related_node_from_json(node_set_str, node_set, nodeType, node_dict):
  for node_name in node_set_str.split(','):
    if node_name == '':
      return
    temp_node_key = key_with_suffix(nodeType, node_name)
    if temp_node_key not in node_dict:
      node = Node(nodeType, node_name)
      node_dict[temp_node_key] = node
    else:
      node = node_dict[temp_node_key]
    node_set.add(node)