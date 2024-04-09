
import argparse
from pathlib import Path
import re
from collections import deque, defaultdict
import random

class Node:
    def __init__(self, gate_type, gate_number):
        self.gate_type = gate_type
        self.gate_number = gate_number
        self.inputs = []
        self.outputs = []
        self.load_capacitance = 0.0 #declaring the new sta attributes to be used in different functions
        self.input_slew = 0.0       
        self.delay = 0.0            
        self.output_slew = 0.0      
        self.required_time = float('inf')
        self.node_delays=[]
        self.inp_delays=[]
        self.slack=None

    def __repr__(self):
        return f'{self.gate_type}-{self.gate_number}'    #used to connect gate type and gate number

class parsingn1dmlib:                              #class to parse the lib file for nldm types like delays and slews
    def __init__(self, pathof1ib):
        self.pathof1ib = pathof1ib
        self.lib_data = {}

    def parsing1ib(self, parsetyperequested):
        with open(self.pathof1ib, 'r') as file:
            fi1edatastored = file.read()

        if parsetyperequested == 'delays':
            stringmatching = re.compile(
                r'cell\s+\((?P<cell_name>[^\)]+)\).*?'
                r'capacitance\s*:\s*(?P<capacitance>[^;]+);.*?'
                r'cell_delay.*?'
                r'index_1\s*\((?P<input_slews>[^\)]+)\).*?'
                r'index_2\s*\((?P<load_cap>[^\)]+)\).*?'
                r'values\s*\((?P<values>.*?)\);',
                re.DOTALL
            )
        elif parsetyperequested == 'slews':
            stringmatching = re.compile(
                r'cell\s+\((?P<cell_name>[^\)]+)\).*?'
                r'capacitance\s*:\s*(?P<capacitance>[^;]+);.*?'
                r'output_slew.*?'
                r'index_1\s*\((?P<input_slews>[^\)]+)\).*?'
                r'index_2\s*\((?P<load_cap>[^\)]+)\).*?'
                r'values\s*\((?P<values>.*?)\);',
                re.DOTALL
            )
        else:
            raise ValueError("Invalid parsetyperequested. Choose between the options 'delays' or 'slews'.")

        outputresult = []
        for samevalue in stringmatching.finditer(fi1edatastored):
            cell_name = samevalue.group('cell_name').strip()
            capacitance = samevalue.group('capacitance').strip()
            input_slews = ' '.join(samevalue.group('input_slews').split())
            load_cap = ' '.join(samevalue.group('load_cap').split())
            values = ' '.join(samevalue.group('values').replace("\\", "").split())
            outputresult.append((cell_name, capacitance, input_slews, load_cap, values))

        #print(outputresult)
        return outputresult

class STAEngine:
    def __init__(self, delaysparsed, slewsparsed):
        self.delaysparsed = delaysparsed
        self.slewsparsed = slewsparsed
        self.nodes = {}
        self.gates = {}
        self.lib_data = {}  # To store the parsed library data in an organized manner
        self.modified_gate_capacitance = {}

    def extract_nldmstaengine(self):
        for cell_name, capacitance, input_slews, load_cap, values in self.delaysparsed:
            input_slews = input_slews.replace('"', '')
            load_cap = load_cap.replace('"', '')
            values = values.replace('"', '').replace("\\", "").strip()# we clean and process the values string

            if cell_name not in self.lib_data:
                self.lib_data[cell_name] = {'capacitance': float(capacitance)}

            
            self.lib_data[cell_name]['delays'] = { # Converting to float, we are skipping the empty strings
                'input_slews': [float(slew) for slew in input_slews.split(',') if slew],
                'load_caps': [float(cap) for cap in load_cap.split(',') if cap],
                'values': [[float(val) for val in row.split(',') if val] for row in values.split()]
            }

        
        for cell_name, _, input_slews, load_cap, values in self.slewsparsed:# Similarly we are processing slew information
            input_slews = input_slews.replace('"', '')
            load_cap = load_cap.replace('"', '')
            values = values.replace('"', '').replace("\\", "").strip()
            
            if cell_name not in self.lib_data:
                continue

            
            self.lib_data[cell_name]['slews'] = {
                'input_slews': [float(slew) for slew in input_slews.split(',') if slew],# Converting to float and skipping the empty strings
                'load_caps': [float(cap) for cap in load_cap.split(',') if cap],
                'values': [[float(val) for val in row.split(',') if val] for row in values.split()]
            }
            
        gate_capacitance = {}
        modified_gate_capacitance = {}

        
        if not self.lib_data:
            print("Warning: lib_data is empty. Ensure that it's correctly populated.")# Checking if self.lib_data is populated
            return

        
        for gate_name, gate_info in self.lib_data.items():
            gate_capacitance[gate_name] = gate_info['capacitance']# Extracting the gate names and capacitance

        for gate_name, capacitance in gate_capacitance.items():        # Modifying gate names to remove '2_X1' and '_X1' from the input data
            if "2_X1" in gate_name:
                new_gate_name = gate_name.replace("2_X1", "")
            elif "_X1" in gate_name:
                new_gate_name = gate_name.replace("_X1", "")
            else:
                new_gate_name = gate_name  # updating the gate name
            self.modified_gate_capacitance[new_gate_name] = capacitance

        #print("Original Gate Capacitance:", gate_capacitance)
        
        keys_to_add = []
        
        for gate_name, capacitance in modified_gate_capacitance.items():# Checking for "INV" and "BUF" entries and preparing to add "NOT" and "BUFF" respectively
            if gate_name == "INV":
                keys_to_add.append(("NOT", capacitance))
            elif gate_name == "BUF":
                keys_to_add.append(("BUFF", capacitance))

        
        for new_gate_name, capacitance in keys_to_add:# Adding the prepared keys and values to the dictionary delcared
            modified_gate_capacitance[new_gate_name] = capacitance

        #print("Final Modified Gate Capacitance:", self.modified_gate_capacitance)
    
    def read_circuit_file(self, file_path):
        
        nodes = {}# Initializing the dictionaries and sets for nodes, gates, and primary inputs/outputs
        gates = {}
        primary_inputs = set()
        primary_outputs = set()

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                elif line.startswith('INPUT'):
                    input_name = re.search(r'\((.*?)\)', line).group(1)
                    nodes[input_name] = Node('INP', input_name)
                    primary_inputs.add(input_name)
                elif line.startswith('OUTPUT'):
                    output_name = re.search(r'\((.*?)\)', line).group(1)
                    nodes[output_name] = Node('OUTP', output_name)
                    primary_outputs.add(output_name)
                else:
                    gate_num, gate_def = line.split('=', 1)
                    gate_num = gate_num.strip()
                    gate_type, inputs_str = gate_def.split('(', 1)
                    gate_type = gate_type.strip()
                    inputs_nums = [x.strip() for x in inputs_str[:-1].split(',')]

                    node = Node(gate_type, gate_num)
                    for inp_num in inputs_nums:
                        inp_node = nodes.get(inp_num, None)
                        if inp_node:
                            inp_node.outputs.append(node)
                            node.inputs.append(inp_node)

                    nodes[gate_num] = node
                    gates[gate_num] = node

        self.nodes = nodes
        self.gates = gates
        self.primary_inputs = primary_inputs
        self.primary_outputs = primary_outputs  
        
        #print("Node inputs:")
        for node_id, node in nodes.items():
            input_ids = [inp.gate_number for inp in node.inputs]
            #print(f"{node_id} inputs: {input_ids}")
    
        
        #print("Node outputs with Gate Names:")# Printing the outputs for each node, including gate names
        for node_id, node in nodes.items():
            output_info = [(out.gate_number, out.gate_type) for out in node.outputs]
            #print(f"{node_id} outputs: {output_info}")
            
    def assign_load_capacitances(self):
        final_load_capacitances = {}

        
        
        default_inv_capacitance = self.modified_gate_capacitance.get("INV", 0.0) * 4  # Fetching the capacitance value for the "INV" gate type, to use as a default if necessary

        for node_id, node in self.nodes.items():# Ensuring there's a fallback value in case "INV" isn't found
            total_capacitance = 0.0

            
            for output_node in node.outputs:# Iterating over the outputs of the current node
                gate_type = output_node.gate_type
                
                if gate_type == 'NOT':
                    gate_type = 'INV'
                elif gate_type == 'BUFF':
                    gate_type = 'BUF'
                
                if gate_type in self.modified_gate_capacitance:
                    capacitance = self.modified_gate_capacitance[gate_type]
                    total_capacitance += capacitance
                else:
                    print(f"Warning: Gate type {gate_type} not found in modified_gate_capacitance.")

            
            if total_capacitance == 0.0:# If total capacitance is 0.0, we use four times the capacitance of an "INV" gate
                
                if node_id in self.primary_outputs:
                    total_capacitance = default_inv_capacitance# we are checking is particularly relevant for output nodes

            node.load_capacitance = total_capacitance
            final_load_capacitances[node_id] = total_capacitance

        return final_load_capacitances
           
    def interpolate_nldm(self, gate_name, input_slew, load_cap):
        #print(self.lib_data)
        if gate_name=='NOT':
            gate_name='INV'
        if gate_name=='BUFF':
            gate_name='BUF'
        for gate_named, gate_infod in self.lib_data.items():
            #print(f'gate name {gate_named}')
            #print(f'gate info {gate_infod}')
            if re.sub(r'\b(\w+?)(2_X1|_X1)\b', r'\1', gate_named) == gate_name:
                gate_data = gate_infod
                
        #print(gate_data)

        if not gate_data:        # Validating that gate_data was found
            raise ValueError(f"Gate '{gate_name}' not found in lib_data.")

        #print(type(gate_data['delays']['input_slews']))
        input_slew_indices = [i for i, v in enumerate(gate_data['delays']['input_slews']) if v <= input_slew]        # Finding the indices in the input_slews and load_caps that will cover the input slew and load capacitance

        load_cap_indices = [i for i, v in enumerate(gate_data['delays']['load_caps']) if v <= load_cap]
        
        #print(f'input slew indices: {input_slew_indices}')

        tau1_index = max(input_slew_indices) if input_slew_indices else 0        # Ensuring that we have bracketing values

        tau2_index = min(tau1_index + 1, len(gate_data['delays']['input_slews']) - 1)
        C1_index = max(load_cap_indices) if load_cap_indices else 0
        C2_index = min(C1_index + 1, len(gate_data['delays']['load_caps']) - 1)
        
        if tau1_index==6:
            tau1_index=5
            tau2_index=6
        if C1_index==6:
            C1_index=5
            C2_index=6
            

        v11 = gate_data['delays']['values'][tau1_index][C1_index]        # Extracting the corner points for interpolation

        v12 = gate_data['delays']['values'][tau1_index][C2_index]
        v21 = gate_data['delays']['values'][tau2_index][C1_index]
        v22 = gate_data['delays']['values'][tau2_index][C2_index]

        tau1 = gate_data['delays']['input_slews'][tau1_index]        # Performing the bilinear interpolation

        tau2 = gate_data['delays']['input_slews'][tau2_index]
        C1 = gate_data['delays']['load_caps'][C1_index]
        C2 = gate_data['delays']['load_caps'][C2_index]

        delay = (
            v11 * (C2 - load_cap) * (tau2 - input_slew) +           # method to execute the interpolation formula

            v12 * (load_cap - C1) * (tau2 - input_slew) +
            v21 * (C2 - load_cap) * (input_slew - tau1) +
            v22 * (load_cap - C1) * (input_slew - tau1)
        ) / ((C2 - C1) * (tau2 - tau1))

        return delay        # Returning  the calculated delay

        
    def interpolate_slew(self, gate_name, input_slew, load_cap):
        if gate_name == 'NOT':
            gate_name = 'INV'
        if gate_name == 'BUFF':
            gate_name = 'BUF'

        gate_data = None
        for gate_named, gate_infod in self.lib_data.items():        # Finding the appropriate gate data

            if re.sub(r'\b(\w+?)(2_X1|_X1)\b', r'\1', gate_named) == gate_name:
                gate_data = gate_infod

        if not gate_data:
            raise ValueError(f"Gate '{gate_name}' not found in lib_data.")

        input_slew_indices = [i for i, v in enumerate(gate_data['slews']['input_slews']) if v <= input_slew]         # Finding the bracketing indices for input slew and load capacitance

        load_cap_indices = [i for i, v in enumerate(gate_data['slews']['load_caps']) if v <= load_cap]

        tau1_index = max(input_slew_indices) if input_slew_indices else 0
        tau2_index = min(tau1_index + 1, len(gate_data['slews']['input_slews']) - 1)
        C1_index = max(load_cap_indices) if load_cap_indices else 0
        C2_index = min(C1_index + 1, len(gate_data['slews']['load_caps']) - 1)

        if tau1_index == 6:        # Adjusting the boundary conditions

            tau1_index = 5
            tau2_index = 6
        if C1_index == 6:
            C1_index = 5
            C2_index = 6

        v11 = gate_data['slews']['values'][tau1_index][C1_index]        # Extracting the corner points for interpolation

        v12 = gate_data['slews']['values'][tau1_index][C2_index]
        v21 = gate_data['slews']['values'][tau2_index][C1_index]
        v22 = gate_data['slews']['values'][tau2_index][C2_index]

        tau1 = gate_data['slews']['input_slews'][tau1_index]        # Performing the bilinear interpolation

        tau2 = gate_data['slews']['input_slews'][tau2_index]
        C1 = gate_data['slews']['load_caps'][C1_index]
        C2 = gate_data['slews']['load_caps'][C2_index]

        slew = (
            v11 * (C2 - load_cap) * (tau2 - input_slew) +
            v12 * (load_cap - C1) * (tau2 - input_slew) +
            v21 * (C2 - load_cap) * (input_slew - tau1) +
            v22 * (load_cap - C1) * (input_slew - tau1)
        ) / ((C2 - C1) * (tau2 - tau1))

        return slew
    
    # def calculate_delays_and_slews(self):
        # queue = deque(self.primary_inputs)  # Initializing the queue with primary inputs

        # for node_id in self.primary_inputs:  # Initializing delays and slews for primary inputs
            # node = self.nodes[node_id]
            # node.delay = 0.00  # Assuming primary inputs have no delay
            # node.output_slew = 0.002  # Assuming a default slew for primary inputs

        # while queue:
            # current_node_id = queue.popleft()  # Processing the queue
            # current_node = self.nodes[current_node_id]

            # # Continue processing only if current node is not a primary input
            # # and all its input slews have been computed
            # if current_node_id not in self.primary_inputs:
                # if all(hasattr(inp, 'output_slew') and inp.output_slew != 0.0 for inp in current_node.inputs):
                    # input_delays = [inp.delay for inp in current_node.inputs]
                    # input_slews = [inp.output_slew for inp in current_node.inputs]

                    # gate_type = current_node.gate_type
                    # load_cap = current_node.load_capacitance

                    # # Calculating interpolated delay and slew for each input
                    # delays = [self.interpolate_nldm(gate_type, slew, load_cap) for slew in input_slews]
                    # slews = [self.interpolate_slew(gate_type, slew, load_cap) for slew in input_slews]

                    # # Adjusting delay and slew calculations for nodes with more than 2 inputs
                    # if len(current_node.inputs) > 2:
                        # delays = [x * len(current_node.inputs) / 2 for x in delays]
                        # slews = [x * len(current_node.inputs) / 2 for x in slews]

                    # node_delays = [x + y for x, y in zip(input_delays, delays)]
                    # current_node.delay = max(node_delays)
                    # index = node_delays.index(current_node.delay)

                    # current_node.output_slew = slews[index]
                    # current_node.node_delays = node_delays
                    # current_node.inp_delays = input_delays
                # else:
                    # queue.append(current_node_id)  # Re-adding the current node to the queue if needed

            # # Adding the fanouts to the queue if not already processed
            # for out_node in current_node.outputs:
                # if hasattr(out_node, 'gate_number') and out_node.gate_number not in queue:
                    # if hasattr(out_node, 'output_slew') and out_node.output_slew == 0.0:
                        # queue.append(out_node.gate_number)
                        
    def calculate_delays_and_slews(self):
        queue = deque(self.primary_inputs)  # Initializing the queue with primary inputs
        processed_nodes = set()  # To track nodes that have been fully processed
        loop_detector = defaultdict(int)  # To detect potential infinite loops
        
        max_iterations_without_progress = len(self.nodes) * 2
        iterations_without_progress = 0

        for node_id in self.primary_inputs:  # Initializing delays and slews for primary inputs
            node = self.nodes[node_id]
            node.delay = 0.00  # Assuming primary inputs have no delay
            node.output_slew = 0.002  # Assuming a default slew for primary inputs

        while queue:
            current_node_id = queue.popleft()

            # Increase loop detector counter each time a node is processed
            loop_detector[current_node_id] += 1
            if loop_detector[current_node_id] > max_iterations_without_progress:
                print(f"Potential infinite loop detected with node {current_node_id}. Breaking out of the loop.")
                break

            current_node = self.nodes[current_node_id]
            if current_node_id not in processed_nodes:
                processed_nodes.add(current_node_id)
                iterations_without_progress = 0  # Reset counter when making progress
            else:
                iterations_without_progress += 1
                if iterations_without_progress > max_iterations_without_progress:
                    print("No progress detected. Breaking out of the loop.")
                    break

            if current_node_id not in self.primary_inputs:
                if all(hasattr(inp, 'output_slew') and inp.output_slew != 0.0 for inp in current_node.inputs):
                    input_delays = [inp.delay for inp in current_node.inputs]
                    input_slews = [inp.output_slew for inp in current_node.inputs]

                    gate_type = current_node.gate_type
                    load_cap = current_node.load_capacitance

                    delays = [self.interpolate_nldm(gate_type, slew, load_cap) for slew in input_slews]
                    slews = [self.interpolate_slew(gate_type, slew, load_cap) for slew in input_slews]

                    if len(current_node.inputs) > 2:
                        delays = [x * len(current_node.inputs) / 2 for x in delays]
                        slews = [x * len(current_node.inputs) / 2 for x in slews]

                    node_delays = [x + y for x, y in zip(input_delays, delays)]
                    current_node.delay = max(node_delays)
                    index = node_delays.index(current_node.delay)

                    current_node.output_slew = slews[index]
                    current_node.node_delays = node_delays
                    current_node.inp_delays = input_delays
                else:
                    # Re-adding the current node to the queue if needed
                    queue.append(current_node_id)

            # Adding the fanouts to the queue if not already processed
            for out_node in current_node.outputs:
                if hasattr(out_node, 'gate_number') and out_node.gate_number not in queue:
                    if hasattr(out_node, 'output_slew') and out_node.output_slew == 0.0:
                        queue.append(out_node.gate_number)
                    
    # def calculate_output_slews(self):#function to calculate the output slews
        # queue = deque(self.primary_outputs)
        # RAT=0.00
        # visited = {}
        # for node_id in self.primary_outputs:
            # node = self.nodes[node_id]
            # RAT = max(RAT,1.1*node.delay)
            
        # for node_id,node in self.nodes.items():
            # node.required_time=RAT
            # visited[node_id]=0
        
        
        # while queue:
            # current_node_id = queue.popleft()
            # current_node = self.nodes[current_node_id]
            # traverse = 1
            
            # for current_node_id_outputs in self.nodes[current_node_id].outputs:
                # if visited[current_node_id_outputs.gate_number]==0:
                    # traverse=0
                    # break
            
            # if traverse==1:
                # delay=0.00
                # count=0
                # for input_node_id in (self.nodes[current_node_id].inputs):
                    # delay = self.nodes[current_node_id].node_delays[count]-self.nodes[current_node_id].inp_delays[count]
                    # self.nodes[input_node_id.gate_number].required_time = min(self.nodes[input_node_id.gate_number].required_time, self.nodes[current_node_id].required_time - delay)
                    # #print(current_node_id," ",input_node_id.gate_number," ",self.nodes[input_node_id.gate_number].required_time)
                    # count=count+1
                    # if input_node_id.gate_number not in queue:
                        # queue.append(input_node_id.gate_number)
                # visited[current_node_id]=1
                
    def calculate_output_slews(self):  # Function to calculate the output slews
        queue = deque(self.primary_outputs)
        RAT = 0.00
        visited = {}

        # Initialize RAT based on the delays of primary outputs
        for node_id in self.primary_outputs:
            node = self.nodes[node_id]
            RAT = max(RAT, 1.1 * node.delay)

        # Set initial required time for all nodes and mark them as not visited
        for node_id, node in self.nodes.items():
            node.required_time = RAT
            visited[node_id] = 0

        while queue:
            current_node_id = queue.popleft()
            current_node = self.nodes[current_node_id]
            traverse = 1
            
            # Check if all outputs have been visited
            for output_node in current_node.outputs:
                if visited[output_node.gate_number] == 0:
                    traverse = 0
                    break

            # If all outputs of the current node have been visited, calculate required times for inputs
            if traverse == 1:
                for count, input_node in enumerate(current_node.inputs):
                    # Check if index is within bounds for both 'node_delays' and 'inp_delays'
                    if count < len(current_node.node_delays) and count < len(current_node.inp_delays):
                        delay_diff = current_node.node_delays[count] - current_node.inp_delays[count]
                        input_node.required_time = min(input_node.required_time, current_node.required_time - delay_diff)
                    else:
                        print(f"Warning: Index out of range for node {current_node_id}.")
                        # Consider breaking or continuing based on the application's needs
                    
                    # Mark the current node as visited and add its inputs to the queue if they haven't been added already
                    visited[current_node_id] = 1
                    if input_node.gate_number not in queue:
                        queue.append(input_node.gate_number)

    def calculate_slack(self):
        for node_id, node in self.nodes.items():
            node.slack = node.required_time - node.delay            # we are printing the slack for each node here

            #print(f"Node {node_id}: Slack = {node.slack}")
            
    def find_critical_path(self):
        min_slack_node = None        # Finding the starting node (with minimum slack)

        for node_id, node in self.nodes.items():
            if min_slack_node is None or node.slack < self.nodes[min_slack_node].slack:
                min_slack_node = node_id
                
        critical_path = [min_slack_node]        # Initializing the critical path list with the starting node

        
        current_node_id = min_slack_node
        while self.nodes[current_node_id].gate_type != 'INP':        # Traversing backwards to find the critical path

            current_node = self.nodes[current_node_id]
            min_slack = float('inf')
            next_node_id = None
            for inp in current_node.inputs:
                inp_id = inp.gate_number
                if self.nodes[inp_id].slack < min_slack or (self.nodes[inp_id].slack == min_slack and self.nodes[inp_id].delay > self.nodes[next_node_id].delay if next_node_id else True):
                    min_slack = self.nodes[inp_id].slack
                    next_node_id = inp_id
            critical_path.append(next_node_id)
            current_node_id = next_node_id
        
        critical_path = critical_path[::-1]        # Reversing the critical path list to start with the input and end with the output

        
        formatted_path = []        # Formatting the critical path for output

        for node_id in critical_path:
            node = self.nodes[node_id]
            formatted_path.append(node.gate_type + '-' + node_id.split('-')[-1])
        
        last_node_id = critical_path[-1]        # Appending "OUTPUT-" with the last node's gate number if it's not already labeled as OUTPUT

        last_node = self.nodes[last_node_id]
        if last_node.gate_type != 'OUTP':
            formatted_path.append('OUTPUT-' + last_node_id.split('-')[-1])

        return ','.join(formatted_path)

        
def read_circuit_file(file_path):
    nodes = {}
    gates = {}  # Dictionary to specifically track gates
    primaryinps = set()
    primaryoups = set()

    with open(file_path, 'r') as file:    # First pass to register all nodes in the first complete iteration

        for line in file:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            elif line.startswith('INPUT'):
                input_name = re.search(r'\((.*?)\)', line).group(1)
                nodes[input_name] = Node('INP', input_name)
                primaryinps.add(input_name)
            elif line.startswith('OUTPUT'):
                output_name = re.search(r'\((.*?)\)', line).group(1)
                nodes[output_name] = Node('OUTP', output_name)
                primaryoups.add(output_name)
            else:
                gate_num = line.split('=')[0].strip()
                nodes[gate_num] = Node('UNKNOWN', gate_num)  # we are initially marking as unknown
                gates[gate_num] = nodes[gate_num]  # adding the gate num nodes to the gates dictionary

    with open(file_path, 'r') as file:    # we are iterating the second iteration to establish connections

        for line in file:
            line = line.strip()
            if line.startswith('#') or not line or line.startswith('INPUT') or line.startswith('OUTPUT'):
                continue
            gate_num, gate_def = line.split('=', 1)
            gate_num = gate_num.strip()
            gate_type, inputs_str = gate_def.split('(', 1)
            gate_type = gate_type.strip()
            inputs_nums = [x.strip() for x in inputs_str[:-1].split(',')]

            node = nodes[gate_num]
            node.gate_type = gate_type  # we are correcting the gate type from the unknown
            for inp_num in inputs_nums:
                inp_node = nodes[inp_num]
                inp_node.outputs.append(node)
                node.inputs.append(inp_node)

    return nodes, gates, primaryinps, primaryoups  #we are returning the outputs

def exportinggateinfo(gates, output_file):    #function definition to export gates into output file
    gate_count = len(gates)                   
    with open(output_file, 'a') as file:      #we are counting the gates individually
        countgatetypes = {}
        for gate in gates.values():
            gate_type = gate.gate_type             #declaring and counting gate types
            countgatetypes[gate_type] = countgatetypes.get(gate_type, 0) + 1

        for gate_type, count in countgatetypes.items(): #for every gate type and count we are writing the respective information into file
            file.write(f'{count} {gate_type} gates\n')

def exportingprimaryinfo(inputs, outputs, output_file):
    with open(output_file, 'a') as file:
        file.write(f'{len(inputs)} primary inputs\n')  # exporting out the input details
        file.write(f'{len(outputs)} primary outputs\n')  # exporting out the output details

def exportfanoutinfo(nodes, primaryoups, output_file):
    with open(output_file, 'a') as file:
        file.write('Fanout...\n')
        for gate_number, node in nodes.items():
            fanout_info = []
            for out in node.outputs:
                prefix = "INPUT" if out.gate_type == "INP" else "OUTPUT" if out.gate_type == "OUTP" else out.gate_type                # Conditional logic to use correct labels "INPUT" or "OUTPUT", else use gate type as is.

                fanout_info.append(f"{prefix}-{out.gate_number}")

            if gate_number in primaryoups:            # Appending the "OUTPUT-{gate_number}" if the gate itself serves as an output. 

                fanout_info.append(f"OUTPUT-{gate_number}")            # This ensures gates that are also outputs are correctly identified in the fanout section.


            file.write(f'{node.gate_type}-{gate_number}: {", ".join(fanout_info)}\n')            # Write the fanout information to the file.


def exportfanininfo(nodes, output_file):
    with open(output_file, 'a') as file:
        file.write('Fanin...\n')
        for gate_number, node in nodes.items():
            fanin_info = []
            for inp in node.inputs:
                prefix = "INPUT" if inp.gate_type == "INP" else "OUTPUT" if inp.gate_type == "OUTP" else inp.gate_type                # Using correct labels for input and output gate types

                fanin_info.append(f"{prefix}-{inp.gate_number}")
            file.write(f'{node.gate_type}-{gate_number}: {", ".join(fanin_info)}\n')

def main():
    parser = argparse.ArgumentParser(description='Parse circuit file and print information.') 
    parser.add_argument('--read_ckt', type=str, help='Path to the circuit file')              
    parser.add_argument('--delays', action='store_true', help="Flag to extract cell delays")  
    parser.add_argument('--slews', action='store_true', help="Flag to extract output slews")  
    parser.add_argument('--read_nldm', type=str, help="Path to the NLDM liberty file")        
    args = parser.parse_args()

    if args.read_ckt and args.read_nldm:
        pathreadforcktfile = Path(args.read_ckt)
        pathof1ib = Path(args.read_nldm)
        
        if not pathreadforcktfile.is_file() or not pathof1ib.is_file():
            print(f"Error: Circuit file or NLDM liberty file not found.")
            return
            
        output_file = "circuitanalysis.txt"  

        
        open(output_file, 'w').close()# Opening the file to clear its contents

        with open(output_file, 'a') as file:        # Reopening the file in append mode to add new content


            parser = parsingn1dmlib(pathof1ib)        

            parseddetails = parser.parsing1ib('delays')
            parseddetails1 = parser.parsing1ib('slews')
            sta_engine = STAEngine(parseddetails, parseddetails1)
            #print(f"parseddet: {parseddetails}\n parseddet1: {parseddetails1}\n staengine: {sta_engine}")
            sta_engine.read_circuit_file(pathreadforcktfile)         

            sta_engine.extract_nldmstaengine()
            
            final_load_capacitances = sta_engine.assign_load_capacitances()        
            #print(f"finalcap: {final_load_capacitances}")
            delay_calculated = sta_engine.calculate_delays_and_slews()
            #print(f"delays: {delay_calculated}")

            slews_calculated = sta_engine.calculate_output_slews()
            #print(f"slews: {slews_calculated}")
            
            slack_calculated = sta_engine.calculate_slack()
            #print(f"slack: {slack_calculated}")

            max_delay = 0.0  # Initializing maximum delay to an initial value

            for node_id, node in sta_engine.nodes.items():                # Writing each node's details to the file

                if node.delay > max_delay:                # Updating the maximum delay if the current node's delay is greater

                    max_delay = node.delay
            
            #print(max_delay)            
            file.write(f"Maximum Delay: {max_delay} ns\n\n")            # After finding the maximum delay, we are writing it to the file
            
            #print(node.slack)
            #print(node.gate_type)
            file.write(f"Gate Slacks:\n")
            for node_id, node in sta_engine.nodes.items():
                file.write(f"{node.gate_type} - {node_id} : Slack = {node.slack} ns\n")

            critical_path = sta_engine.find_critical_path()
            file.write(f"\nCritical Path: \n")
            file.write(f"{critical_path} \n")
                
            #file.write(f"Timing analysis results exported to {output_file}\n")
        
    elif args.read_ckt:
        pathreadforcktfile = Path(args.read_ckt)
        if not pathreadforcktfile.is_file():
            print(f"Error: File '{args.read_ckt}' not found.")   #error handling for wrong read_ckt input found
            return

        output_file = "circuitdetails.txt"  #output is stored in this circuitdetails file which is generated

        open(output_file, 'w').close()        # Clearing the fi1edatastoreds of the output file

        nodes, gates, primaryinps, primaryoups = read_circuit_file(pathreadforcktfile)

        exportingprimaryinfo(primaryinps, primaryoups, output_file)   #function call to export the primary inputs, outputs into output file
        exportinggateinfo(gates, output_file)                                #function call to export gates into output file
        exportfanoutinfo(gates, primaryoups, output_file)             #function call to export fanout information
        exportfanininfo(gates, output_file)                               #function call to export fanin information

    elif args.read_nldm:
        pathof1ib = Path(args.read_nldm)
        parsinglib = parsingn1dmlib(pathof1ib)   #class variable declaration and calling

        if args.delays:
            parsinglib.parsing1ib('delays') #giving input delays to the class parsingnldm
        elif args.slews:
            parsinglib.parsing1ib('slews')  #giving input slews to the class parsingnldm
    else:
        print("Invalid command. Please specify '--read_ckt <pathreadforcktfile>' or '--delays' or '--slews' and '--read_nldm <pathof1ib>'.")

if __name__ == "__main__":
    main()
