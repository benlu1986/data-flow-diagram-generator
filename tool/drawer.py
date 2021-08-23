import graphviz
from utils import key_with_suffix
from node import Node
from node import NodeType

def __build_node_graph(dot, node_iter):
  for node in node_iter:
    if node.nodeType == NodeType.SERVICE:
      dot.node(key_with_suffix(node.nodeType, node.name), node.name, shape='component')
    else:
      dot.node(key_with_suffix(node.nodeType, node.name), node.name, shape='diamond')

def __render(dot, queue, visited_set, upstreamOrDownstream, l=-1, ignore_node_set=set()): 
  # upstreamOrDownstream: 1: upstream; 2: downstream
  #
  #
  temp_q = []
  while len(queue) > 0:
    root = queue.pop(0)
    if root not in visited_set:
      related_node_set = set()
      if upstreamOrDownstream == 1:
        related_node_set.update(root.parent)
      else:
        related_node_set.update(root.child)
      for node in related_node_set:
        if node not in ignore_node_set and l != 0:
          temp_q.append(node)
          if upstreamOrDownstream == 1:
            dot.edge(key_with_suffix(node.nodeType, node.name), key_with_suffix(root.nodeType, root.name))
          else:
            dot.edge(key_with_suffix(root.nodeType, root.name), key_with_suffix(node.nodeType, node.name))
      visited_set.add(root)
  
  queue.extend(temp_q)
  if len(queue) > 0:
    __render(dot, queue, visited_set, upstreamOrDownstream, l-1 , ignore_node_set)

def render_flows(target_node_set, option, l, ignore_names):
  dot = graphviz.Digraph(comment='Flow')
  if option == 2 or option == 0 :
    children_visited_set = set()
    for header in target_node_set:
      __render(dot, [header], children_visited_set, 2, l, ignore_names)
    __build_node_graph(dot, children_visited_set)
  if option == 1 or option == 0 :
    parent_visited_set = set()
    for header in target_node_set:
      __render(dot, [header], parent_visited_set, 1, l, ignore_names)
    __build_node_graph(dot, parent_visited_set)

  dot.render('test-output/flow.gv', view=True)


def render_all_flows(topic_node_dict, service_node_dict, header_service_node_set, header_topic_node_set):

  dot = graphviz.Digraph(comment='Flow')

  __build_node_graph(dot, service_node_dict.values())
  __build_node_graph(dot, topic_node_dict.values())

  visited_set = set()
  for header in header_service_node_set:
    __render(dot, [header], visited_set, 0)
  for header in header_topic_node_set:
    __render(dot, [header], visited_set, 0)
  dot.render('test-output/flow.gv', view=True)