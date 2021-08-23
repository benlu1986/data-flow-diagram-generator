from enum import Enum
class NodeType(Enum):
  SERVICE = 1
  TOPIC = 2

class Node:
  def __init__(self, nodeType, name):
    self.nodeType = nodeType
    self.child = set()
    self.parent = set()
    self.name = name

def convert(obj):
  if type(obj) == Node:
    return obj.__dict__
  if type(obj) == NodeType:
    return obj.name
  elif type(obj) == set:
    return ','.join(map(lambda node: node.name, obj))
  else:
    return ''