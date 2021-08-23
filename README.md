# data-flow-diagram-generator
The tool targets to generate a data flow diagram of au system.

---
### File Structure
- tool: main logic to generate the diagram
  - main.py: main entry to generate an image of data flow 
  - build.py: provide a way to generate nodes data structure in json by k8s and kafka configurations. 'nodes_output.json' would be output.
  - loader.py: load nodes data structure in json into a linked list structure
  - drawer.py: use graphviz to draw the diagram
  - bash.sh: help to grep topic and consumer-group by kafka cli

---
## Usage
### Draw Diagram
python main.py -s|-t <name> -f <node_json_file> [-u] [-d] [-l <level>] [-i <ignore_service_names>]

-s <service_name>: diagram would show the diagram containing the name of the service the data passes through 

-t <topic_name>: diagram would show the diagram containing the name of the topic the data passes through

-u: only show the up-streams

-d: only show the down-streams 

-l <level>: show the tree only within the assigned level

-i <ignore_service_names>: assigned service names would be ignored in generating

-f <node_json_file>: assign the file containing node data structure by json

---
### Generate Nodes Data
python build.py -h \\  
&ensp;&ensp;&ensp;&ensp;--topic_csv_file=<topic_csv_file_path> \\  
&ensp;&ensp;&ensp;&ensp;--kafka_consumer_group_csv_file=<kafka_consumer_group_csv_file_path> \\  
&ensp;&ensp;&ensp;&ensp;--deployment_yaml_file=<deployment_yaml_file> \\  
&ensp;&ensp;&ensp;&ensp;--stateful_yaml_file=<stateful_yaml_file> \\  
&ensp;&ensp;&ensp;&ensp;--configmap_yaml_file=<configmap_yaml_file>

#### sample files are in ../env_sample/ 

---

# Known Issue
