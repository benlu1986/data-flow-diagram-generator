from node import NodeType

def key_with_suffix(nodeType, name):
  if nodeType == NodeType.SERVICE:
    return name + '-s'
  else:
    return name + '-t'