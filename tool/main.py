import sys, getopt
from loader import load_node_from_json
from node import NodeType
from drawer import render_flows
from utils import key_with_suffix

def main(argv):
  target_name = None
  target_nodeType = None
  ignore_service_names = set()
  node_json_file = ''
  option = 0 # 0:all 1: only_upstream 2: only_downstream
  l = -1 # tree depth
  try:
     opts, args = getopt.getopt(argv,"udhas:t:i:l:f:",["service_name=","topic_name=","ignore_names=","level="])
  except getopt.GetoptError:
     __command_hint()
     sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      __command_hint()
      sys.exit()
    elif opt == '-u':
      option = 1
    elif opt == '-d':
      option = 2
    elif opt in ("-l", "--level"):
      l = int(arg)
    elif opt in ("-s", "--service_name"):
      target_name = arg
      target_nodeType = NodeType.SERVICE
    elif opt in ("-t", "--topic_name"):
      if target_name != None:
        print('only focus on target topic: %s!', arg)
      target_name = arg
      target_nodeType = NodeType.TOPIC
    elif opt in ("-i", "--ignore_service_names"):
      ignore_service_names.update(set(arg.split()))
    elif opt == '-f':
      node_json_file = arg
    
  if node_json_file == '':
    print('node file need to be assigned!!!')
    __command_hint()
    return
  
  execute(target_name, target_nodeType, option, l, ignore_service_names, node_json_file)

def execute(target_name, target_nodeType, option, l, ignore_service_names, node_json_file):
  node_dict = load_node_from_json(node_json_file)
  target_node = node_dict[key_with_suffix(target_nodeType, target_name)]
  ignore_nodes = set(filter(
    lambda x: x is not None, 
    map(
      lambda x: node_dict[key_with_suffix(NodeType.SERVICE, x)] if key_with_suffix(NodeType.SERVICE, x) in node_dict else None, 
      ignore_service_names)))

  render_flows(set([target_node]), option, l, ignore_nodes)
  # topic_node_dict, service_node_dict, header_service_node_set, header_topic_node_set = \
  #   build('../cnp0/all_kafka_topic.csv','../cnp0/all_kafka_info.csv','../cnp0/all-deployment.yaml','../cnp0/all-statefulset.yaml','../cnp0/all-cm.yaml')


  # if len(service_names) > 0 or len(topic_names) > 0 :
  #   target_node_set = __get_target_node(service_names, service_node_dict)
  #   target_node_set.update(__get_target_node(topic_names, topic_node_dict))
  #   ignore_node_set = __get_target_node(ignore_names, service_node_dict)
  #   ignore_node_set.update(__get_target_node(ignore_names, topic_node_dict))
  # else:
  #   render_all_flows(topic_node_dict, service_node_dict, header_service_node_set, header_topic_node_set)

def __command_hint():
  print('main.py [-s <service_name>] [-t <topic_name>] [-f <node_json_file>] [-u] [-d] [-l <level>] [-i <ignore_service_names>]')

if __name__ == "__main__":
   main(sys.argv[1:])
