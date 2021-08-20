# data-flow-diagram-generator
The tool targets to generate a data flow diagram of au system.

### File Structure
- tool: main logic to generate the diagram
  - bash.sh: help to grep topic and consumer-group by kafka cli

### Usage
python main.py [-s <service_names>] [-t <topic_names>] [-u] [-d] [-l <level>] [-i <ignore_names>]

-s <service_names>: diagram would show the diagram containing the name of the service the data passes through 

-t <topic_names>: diagram would show the diagram containing the name of the topic the data passes through

-u: only show the up-streams

-d: only show the down-streams 

-l <level>: show the tree only within the assigned level

-i <ignore_names>: assigned service or topic names would be ignored in generating




# Known Issue
