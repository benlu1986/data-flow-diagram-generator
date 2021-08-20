import sys, getopt
import yaml
import csv
import re
from node import Node
from node import NodeType
from node import convert
from draw import render_all_flows, render_flows
import json

def main(argv):
  topic_names = set()
  service_names = set()
  ignore_names = set()
  option = 0 # 0:all 1: only_upstream 2: only_downstream
  l = 0 # tree depth
  try:
     opts, args = getopt.getopt(argv,"udhas:t:i:l:",["service_names=","topic_names=","ignore_names=","level="])
  except getopt.GetoptError:
     print('main.py [-s <service_names>] [-t <topic_names>] [-u] [-d] [-l <level>] [-i <ignore_names>]')
     sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print('main.py [-s <service_names>] [-t <topic_names>] [-u] [-d] [-l <level>] [-i <ignore_names>]')
      sys.exit()
    elif opt == '-u':
      option = 1
    elif opt == '-d':
      option = 2
    elif opt in ("-l", "--level"):
      l = int(arg)
    elif opt in ("-s", "--service_names"):
      service_names.update(set(arg.split()))
    elif opt in ("-t", "--topic_names"):
      topic_names.update(set(arg.split()))
    elif opt in ("-i", "--ignore_names"):
      ignore_names.update(set(arg.split()))
    
  
  execute(service_names, topic_names, option, l, ignore_names)

def execute(service_names, topic_names, option, l, ignore_names):
  topics_set = __read_topics('../cnp0/all_kafka_topic.csv')
  topic_consumer_dict = __read_topic_consumer('../cnp0/all_kafka_info.csv')
  deployment_env_dict = __read_env('../cnp0/all-deployment.yaml')
  statefulset_env_dict = __read_env('../cnp0/all-statefulset.yaml')
  app_env_dict = {**deployment_env_dict, **statefulset_env_dict}
  app_application_yaml_dict = __replace_placeholder(__read_app_application_yaml('../cnp0/all-cm.yaml'), app_env_dict)
  topic_node_dict, service_node_dict, header_service_node_set, header_topic_node_set = __build_tree(topics_set, topic_consumer_dict, app_application_yaml_dict)

  # node_list = list(topic_node_dict.values())
  # node_list.extend(list(service_node_dict.values()))
  # __output_data_structure(node_list)

  if len(service_names) > 0 or len(topic_names) > 0 :
    target_node_set = __get_target_node(service_names, service_node_dict)
    target_node_set.update(__get_target_node(topic_names, topic_node_dict))
    ignore_node_set = __get_target_node(ignore_names, service_node_dict)
    ignore_node_set.update(__get_target_node(ignore_names, topic_node_dict))
    render_flows(target_node_set, option, l, ignore_node_set)
  else:
    render_all_flows(topic_node_dict, service_node_dict, header_service_node_set, header_topic_node_set)

def __get_target_node(names, dict):
  result = set()
  for name in names:
    if name in dict.keys():
      result.add(dict[name])
    else:
      print('%s cannot be found!', name)
  return result

def __read_topics(csvFile):
  # read from file containing topics info and output topics in set
  with open(csvFile, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    mapper = lambda l: "".join(l)
    non_business_topic_filter = lambda topic: topic != 'NO_OP_TOPIC' and not topic.startswith('__')
    return set(filter(non_business_topic_filter, map(mapper, spamreader)))

def __read_topic_consumer(csvFile):
  # output a dictionary in which topic is as key and consumer groups are as value.
  with open(csvFile, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    topic_consumer_dict = {}
    next(spamreader)
    for row in spamreader:
      if row[1] not in topic_consumer_dict:
        topic_consumer_dict[row[1]] = set()
      topic_consumer_dict[row[1]].add(row[0])
    return topic_consumer_dict

def __parse_deployment_and_statefulset(deployment):
  name = ""
  if "app" in deployment["metadata"]["labels"]:
    name = deployment["metadata"]["labels"]["app"] 
  elif "name" in deployment["metadata"]["labels"]:
    name = deployment["metadata"]["labels"]["name"] 
  elif "name" in deployment["metadata"]:
    name = deployment["metadata"]["name"] 
  else:
    return None
  containers = deployment["spec"]["template"]["spec"]["containers"]
  if len(containers) != 1:
    # it seems there would be no business related service of which size is greater than 1
    return None
  else:
    if "env" in containers[0]:
      env_dict = {}
      for env in containers[0]["env"]:
        if "value" in env:
          env_dict[env["name"]] = env["value"]
      return (name, env_dict)
    else:
      return (name, {})

def __read_env(statefuleset_or_deployment_yaml):
  # read env parameters from statefulsets and deployments for the usage of {app-name:topics} dictionary
  with open(statefuleset_or_deployment_yaml, 'r') as stream:
    try:
      deployments_info_dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
    deployments = deployments_info_dict["items"]

    return dict(filter(lambda x: x != None, map(__parse_deployment_and_statefulset, deployments)))

def __read_app_application_yaml(config_map_yaml):
  # configmap can be ignored in which there is no data
  def __filter_config_map_having_application_yaml(config_map):
    return "data" in config_map and "application.yaml" in config_map["data"]

  def __mapper_application_yaml(config_map):
      # get app name
    name = ""
    if "labels" in config_map["metadata"] and "app" in config_map["metadata"]["labels"]:
      name = config_map["metadata"]["labels"]["app"] 
    else:
      name = config_map["metadata"]["name"]
    return (name, config_map["data"]["application.yaml"].replace(':}','}'))

  with open(config_map_yaml) as stream:
    try:
      config_map_info_dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
      print(exc)
    config_maps = config_map_info_dict["items"]
    config_maps_having_application_yaml = list(filter(__filter_config_map_having_application_yaml, config_maps))
    return dict(map(__mapper_application_yaml, config_maps_having_application_yaml))

def __replace_placeholder(app_application_yaml_dict, app_env_dict):
  for app,yaml_str in app_application_yaml_dict.items():
    for match in re.finditer('\$\{(\S*)\}', yaml_str, re.IGNORECASE):
      key = match.group(1)
      if app in app_env_dict and key in app_env_dict[app]:
        yaml_str = re.sub('\$\{' + key + '\}', app_env_dict[app][key], yaml_str)
    app_application_yaml_dict[app] = yaml_str
  return app_application_yaml_dict

def __build_tree(topics_set, topic_consumer_dict, app_application_yaml_dict):

  # header_topics would be initialized by all topics and kick out non-header topic
  topic_node_dict = dict(map(lambda topic: (topic, Node(NodeType.TOPIC, topic)),topics_set))
  service_node_dict = dict(map(lambda app: (app, Node(NodeType.SERVICE, app)),app_application_yaml_dict.keys()))
  header_topic_node_set = set(map(lambda v: v, topic_node_dict.values()))
  header_service_node_set = set()

  for app,application_yaml in app_application_yaml_dict.items():
    app_node = service_node_dict[app]
    is_consume_any_topic = False
    for topic in topics_set:
      topic_node = topic_node_dict[topic]
      # if re.search(rf'\b{topic}\b', application_yaml, re.IGNORECASE):
      if re.search(rf'(?<![-]){topic}(?![-])', application_yaml, re.IGNORECASE):
        is_topic_consumer = False 
        # is_multiple_match = len(re.findall(rf'\b{topic}\b', application_yaml, re.IGNORECASE)) > 1
        is_multiple_match = len(re.findall(rf'(?<![-]){topic}(?![-])', application_yaml, re.IGNORECASE)) > 1
        if topic in topic_consumer_dict:
          for consumer_group in topic_consumer_dict[topic]:
            # if re.search(rf'\b{consumer_group}\b', application_yaml, re.IGNORECASE):
            if re.search(rf'(?<![-]){consumer_group}(?![-])', application_yaml, re.IGNORECASE):
              is_topic_consumer = True
              is_consume_any_topic = True
        if is_topic_consumer:
          topic_node.child.add(app_node)
          app_node.parent.add(topic_node)
          if is_multiple_match:
            app_node.child.add(topic_node)
            topic_node.parent.add(app_node)
            header_topic_node_set.discard(topic_node)
        else:
          app_node.child.add(topic_node)
          topic_node.parent.add(app_node)
          header_topic_node_set.discard(topic_node)
    if not is_consume_any_topic:
      header_service_node_set.add(app_node)
  
  # start to discard header having no children
  for v in header_topic_node_set.copy():
    if len(v.child) == 0:
      header_topic_node_set.discard(v)

  for v in header_service_node_set.copy():
    if len(v.child) == 0:
      header_service_node_set.discard(v)
  return topic_node_dict, service_node_dict, header_service_node_set,header_topic_node_set

def __output_data_structure(node_list):
  with open('output.json', 'w') as f:
    json.dump(node_list, f, default=convert, indent=2)




if __name__ == "__main__":
   main(sys.argv[1:])
