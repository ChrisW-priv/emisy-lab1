#!/bin/python3

import re


def stream_file_lines(filepath:str):
	with open(filepath) as file:
		data = file.read()
	for line in data.split('\n'):
		yield line


def line_is_relevant(line:str):
	strings = (
		"Simulation time",
		"Initialization time",
		"Active sources",
		"TCP Windows",
		"Link delay",
		"Link capacity",
		"Link buffer",
		"TCP1 Average Throughput",
		"TCP2 Average Throughput",
		"TCP3 Average Throughput",
		"Stable Throughput",
	)
	str_in_line = map(lambda x: x in line, strings)
	return any(str_in_line)
		

def line_is_relevant_to_task1(line:str):
	strings = (
		"TCP Windows",
		"TCP1 Average Throughput",
		"Stable Throughput",
	)
	str_in_line = map(lambda x: x in line, strings)
	return any(str_in_line)
		

def line_is_relevant_to_task2(line:str):
	strings = (
		"Link buffer",
		"TCP1 Average Throughput",
		"Stable Throughput",
	)
	str_in_line = map(lambda x: x in line, strings)
	return any(str_in_line)
		

def line_is_relevant_to_task3(line:str):
	strings = (
		"TCP Windows",
		"TCP1 Average Throughput",
		"TCP2 Average Throughput",
		"TCP3 Average Throughput",
		"Stable Throughput",
	)
	str_in_line = map(lambda x: x in line, strings)
	return any(str_in_line)
		

def parse_tcp_window_line(line:str):
    match = re.search(r'\[(\d+)\s(\d+)\s(\d+)\]', line)
    if match:
        return tuple(int(match.group(i)) for i in range(1, 4))


def parse_tcp_throughput(line:str):
	start_index = line.find('= ')
	assert start_index != -1, "there is no '=' sign on tcp throughput line, line passed: " + line
	end_index = line.find(' [', start_index + 2)
	assert start_index != -1, "there is no '[' sign on tcp throughput line, line passed: " + line
	integer_value = float(line[start_index + 2:end_index])
	return integer_value


def make_t1_objs_from_stream(stream):
	t1_relevant = filter(line_is_relevant_to_task1, stream)
	obj = {"TCP Window": 0, "TCP1 Average Throughput": 0, "Stable Throughput": 0}
	for line in t1_relevant:
		if line.startswith("TCP Windows"): 
			yield obj
			tcp_window, *_ = parse_tcp_window_line(line)
			obj = {"TCP Window": tcp_window, "TCP1 Average Throughput": 0, "Stable Throughput": 0}
		if line.startswith("TCP1"): 
			obj['TCP1 Average Throughput'] = parse_tcp_throughput(line)
		if "Stable" in line and obj['Stable Throughput'] == 0:
			obj['Stable Throughput'] = parse_tcp_throughput(line)

		
def make_t2_objs_from_stream(stream):
	t2_relevant = filter(line_is_relevant_to_task2, stream)
	obj = {"Link buffer": 0, "TCP1 Average Throughput": 0, "Stable Throughput": 0}
	for line in t2_relevant:
		if line.startswith("Link buffer"): 
			yield obj
			x = parse_def_line(line)
			obj = {"Link buffer": x, "TCP1 Average Throughput": 0, "Stable Throughput": 0}
		if line.startswith("TCP1"): 
			obj['TCP1 Average Throughput'] = parse_tcp_throughput(line)
		if "Stable" in line and obj['Stable Throughput'] == 0:
			obj['Stable Throughput'] = parse_tcp_throughput(line)


def make_t3_objs_from_stream(stream):
	t3_relevant = filter(line_is_relevant_to_task3, stream)
	obj = {
		"TCP1 Window": 0,
		"TCP2 Window": 0,
		"TCP3 Window": 0,
		"TCP1 Average Throughput": 0,
		"Stable Throughput 1": 0,
		"TCP2 Average Throughput": 0,
		"Stable Throughput 2": 0,
		"TCP3 Average Throughput": 0,
		"Stable Throughput 3": 0,
	}
	last_line = ""
	for line in t3_relevant:
		if line.startswith("TCP Windows"): 
			yield obj
			tcp1, tcp2, tcp3 = parse_tcp_window_line(line)
			obj = {
				"TCP1 Window": tcp1,
				"TCP2 Window": tcp2,
				"TCP3 Window": tcp3,
				"TCP1 Average Throughput": 0,
				"Stable Throughput 1": 0,
				"TCP2 Average Throughput": 0,
				"Stable Throughput 2": 0,
				"TCP3 Average Throughput": 0,
				"Stable Throughput 3": 0,
			}
		if line.startswith("TCP1"): 
			obj['TCP1 Average Throughput'] = parse_tcp_throughput(line)
		if line.startswith("TCP2"): 
			obj['TCP2 Average Throughput'] = parse_tcp_throughput(line)
		if line.startswith("TCP3"): 
			obj['TCP3 Average Throughput'] = parse_tcp_throughput(line)
		if "Stable" in line and "TCP1" in last_line:
			obj['Stable Throughput 1'] = parse_tcp_throughput(line)
		if "Stable" in line and "TCP2" in last_line:
			obj['Stable Throughput 2'] = parse_tcp_throughput(line)
		if "Stable" in line and "TCP3" in last_line:
			obj['Stable Throughput 3'] = parse_tcp_throughput(line)
		last_line = line

		
def main(filepath:str):
	stream = stream_file_lines(filepath)
	filtered = filter(line_is_relevant, stream)
	#any(map(print, stream))
	#any(map(print, filtered))
	#any(map(print, make_t1_objs_from_stream(stream)))
	#any(map(print, make_t2_objs_from_stream(stream)))
	any(map(print, make_t3_objs_from_stream(stream)))
	

if __name__ == "__main__":
	#main(r"/mnt/c/Users/Chris/Downloads/lab1tcp/EINTE/task1.log")
	main(r"/mnt/c/Users/Chris/Downloads/lab1tcp/EINTE/task2.log")

