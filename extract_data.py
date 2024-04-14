#!/bin/python3
import matplotlib.pyplot as plt
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
		"delay",
	)
	str_in_line = map(lambda x: x in line, strings)
	return any(str_in_line)
		

def parse_tcp_window_line(line:str):
    match = re.search(r'\[(\d+)\s(\d+)\s(\d+)\]', line)
    if match:
        return tuple(int(match.group(i)) for i in range(1, 4))


def parse_def_line(line:str):
    match = re.search(r'(\d+)', line)
    if match:
        return int(match.group(1))


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
		"Link delay": 0,
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
				"Link delay": 0,
			}
		if line.startswith("Link delay"): 
			obj['Link delay'] = parse_def_line(line)
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


def make_graph_for_t1(data_generator):
	tcp_window = []
	avg_throughput = []
	stable_throughput = []
	for data in data_generator():
		if data['TCP Window'] in (0, 1000): continue
		tcp_window.append(data['TCP Window'])
		avg_throughput.append(data['TCP1 Average Throughput'])
		stable_throughput.append(data['Stable Throughput'])
	plt.figure(figsize=(10, 6))
	plt.plot(tcp_window, avg_throughput, 'o', label='Average Throughput')
	plt.plot(tcp_window, stable_throughput, 'x', label='Stable Throughput')
	plt.xlabel('TCP Window')
	plt.ylabel('Throughput')
	plt.title('TCP Throughput')
	plt.legend()
	plt.grid(True)
	plt.savefig('task1.png')


def make_graph_for_t2(data_generator):
	tcp_window = []
	avg_throughput = []
	stable_throughput = []
	for data in data_generator():
		if data['Link buffer'] in (0, 1000): continue
		tcp_window.append(data['Link buffer'])
		avg_throughput.append(data['TCP1 Average Throughput'])
		stable_throughput.append(data['Stable Throughput'])
	plt.figure(figsize=(10, 6))
	plt.plot(tcp_window, avg_throughput, 'o', label='Average Throughput')
	plt.plot(tcp_window, stable_throughput, 'x', label='Stable Throughput')
	plt.xlabel('Link buffer')
	plt.ylabel('Throughput')
	plt.title('TCP Throughput')
	plt.legend()
	plt.grid(True)
	plt.savefig('task2.png')


def make_graph_for_t3a(data_generator):
	tcp_window = []
	avg_throughput1 = []
	avg_throughput2 = []
	avg_throughput3 = []
	stable_throughput1 = []
	stable_throughput2 = []
	stable_throughput3 = []
	gen = data_generator()
	for i, data in enumerate(gen):
		if i == 0: continue
		tcp_window.append(data['Link delay'])
		avg_throughput1.append(data['TCP1 Average Throughput'])
		avg_throughput2.append(data['TCP2 Average Throughput'])
		avg_throughput3.append(data['TCP3 Average Throughput'])
		stable_throughput1.append(data['Stable Throughput 1'])
		stable_throughput2.append(data['Stable Throughput 2'])
		stable_throughput3.append(data['Stable Throughput 3'])
	plt.figure(figsize=(10, 6))
	plt.plot(tcp_window, avg_throughput1, 'o', label='Average Throughput 1', color="red")
	plt.plot(tcp_window, avg_throughput2, 'o', label='Average Throughput 2', color="green")
	plt.plot(tcp_window, avg_throughput3, 'o', label='Average Throughput 3', color="pink")
	plt.plot(tcp_window, stable_throughput1, 'x', label='Stable Throughput 1', color="red")
	plt.plot(tcp_window, stable_throughput2, 'x', label='Stable Throughput 2', color="green")
	plt.plot(tcp_window, stable_throughput3, 'x', label='Stable Throughput 3', color="pink")
	plt.xlabel('Link delay')
	plt.ylabel('Throughput')
	plt.title('TCP Throughput')
	plt.legend()
	plt.grid(True)
	plt.savefig('task3a.png')


def make_graph_for_t3b(data_generator):
	tcp_window = []
	avg_throughput1 = []
	avg_throughput2 = []
	avg_throughput3 = []
	stable_throughput1 = []
	stable_throughput2 = []
	stable_throughput3 = []
	v1s=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,10,10,10,10,10,10,10,10,10,15,15,15,15,15,15,20,20,20,30]
	v2s=[10,10,10,10,10,15,15,15,15,20,20,20,30,30,50,15,15,15,15,20,20,20,30,30,50,20,20,20,30,30,50,30,30,50,50]
	v3s=[15,20,30,50,100,20,30,50,100,30,50,100,50,100,100,20,30,50,100,30,50,100,50,100,100,30,50,100,50,100,100,50,100,100,100]
	gen = data_generator()
	for i, data in enumerate(gen):
		if i == 0: continue
		tcp_window.append((v1s[i-1], v2s[i-1], v3s[i-1]))
		avg_throughput1.append(data['TCP1 Average Throughput'])
		avg_throughput2.append(data['TCP2 Average Throughput'])
		avg_throughput3.append(data['TCP3 Average Throughput'])
		stable_throughput1.append(data['Stable Throughput 1'])
		stable_throughput2.append(data['Stable Throughput 2'])
		stable_throughput3.append(data['Stable Throughput 3'])
	tcp_window = list(map(str, tcp_window))
	plt.figure(figsize=(10, 14))
	plt.xticks(rotation=90)
	plt.plot(tcp_window, avg_throughput1, 'o', label='Average Throughput 1', color="red")
	plt.plot(tcp_window, avg_throughput2, 'o', label='Average Throughput 2', color="green")
	plt.plot(tcp_window, avg_throughput3, 'o', label='Average Throughput 3', color="pink")
	plt.plot(tcp_window, stable_throughput1, 'x', label='Stable Throughput 1', color="red")
	plt.plot(tcp_window, stable_throughput2, 'x', label='Stable Throughput 2', color="green")
	plt.plot(tcp_window, stable_throughput3, 'x', label='Stable Throughput 3', color="pink")
	plt.xlabel('Link delay')
	plt.ylabel('Throughput')
	plt.title('TCP Throughput')
	plt.legend()
	plt.grid(True)
	plt.savefig('task3b.png')


def make_graph_for_t3b2(data_generator):
	tcp_window = []
	avg_throughput1 = []
	avg_throughput2 = []
	avg_throughput3 = []
	stable_throughput1 = []
	stable_throughput2 = []
	stable_throughput3 = []
	v1s=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,10,10,10,10,10,10,10,10,10,15,15,15,15,15,15,20,20,20,30]
	v2s=[10,10,10,10,10,15,15,15,15,20,20,20,30,30,50,15,15,15,15,20,20,20,30,30,50,20,20,20,30,30,50,30,30,50,50]
	v3s=[15,20,30,50,100,20,30,50,100,30,50,100,50,100,100,20,30,50,100,30,50,100,50,100,100,30,50,100,50,100,100,50,100,100,100]
	gen = data_generator()
	for i, data in enumerate(gen):
		if i == 0: continue
		if v1s[i-1] == 0: continue
		tcp_window.append((v1s[i-1], v2s[i-1], v3s[i-1]))
		avg_throughput1.append(data['TCP1 Average Throughput'])
		avg_throughput2.append(data['TCP2 Average Throughput'])
		avg_throughput3.append(data['TCP3 Average Throughput'])
		stable_throughput1.append(data['Stable Throughput 1'])
		stable_throughput2.append(data['Stable Throughput 2'])
		stable_throughput3.append(data['Stable Throughput 3'])
	tcp_window = list(map(str, tcp_window))
	plt.figure(figsize=(10, 14))
	plt.xticks(rotation=90)
	plt.plot(tcp_window, avg_throughput1, 'o', label='Average Throughput 1', color="red")
	plt.plot(tcp_window, avg_throughput2, 'o', label='Average Throughput 2', color="green")
	plt.plot(tcp_window, avg_throughput3, 'o', label='Average Throughput 3', color="pink")
	plt.plot(tcp_window, stable_throughput1, 'x', label='Stable Throughput 1', color="red")
	plt.plot(tcp_window, stable_throughput2, 'x', label='Stable Throughput 2', color="green")
	plt.plot(tcp_window, stable_throughput3, 'x', label='Stable Throughput 3', color="pink")
	plt.xlabel('Link delay')
	plt.ylabel('Throughput')
	plt.title('TCP Throughput')
	plt.legend()
	plt.grid(True)
	plt.savefig('task3b2.png')


def main():
	f1 = r"/mnt/c/Users/Chris/Downloads/lab1tcp/EINTE/task1.log"
	f2 = r"task2_5000.log"
	f3a = r"/mnt/c/Users/Chris/Downloads/lab1tcp/EINTE/task3a.log"
	f3b = r"/mnt/c/Users/Chris/Downloads/lab1tcp/EINTE/task3b.log"
	stream = stream_file_lines(f1)
	filtered = filter(line_is_relevant, stream)
	#any(map(print, stream))
	#any(map(print, filtered))
	#any(map(print, make_t1_objs_from_stream(stream)))
	#any(map(print, make_t2_objs_from_stream(stream)))
	#any(map(print, make_t3_objs_from_stream(stream)))
	stream1 = stream_file_lines(f1)
	x = lambda : make_t1_objs_from_stream(stream1)
	make_graph_for_t1(x)
	stream2 = stream_file_lines(f2)
	x = lambda : make_t2_objs_from_stream(stream2)
	make_graph_for_t2(x)
	stream3 = stream_file_lines(f3a)
	x = lambda : make_t3_objs_from_stream(stream3)
	make_graph_for_t3a(x)
	stream3 = stream_file_lines(f3b)
	x = lambda : make_t3_objs_from_stream(stream3)
	make_graph_for_t3b(x)
	stream3 = stream_file_lines(f3b)
	x = lambda : make_t3_objs_from_stream(stream3)
	make_graph_for_t3b2(x)
	
	

if __name__ == "__main__":
	#f3 = r"/mnt/c/Users/Chris/Downloads/lab1tcp/EINTE/task3a.log"
	#stream = stream_file_lines(f3)
	#stream3 = stream_file_lines(f3)
	#x = lambda : make_t3_objs_from_stream(stream3)
	#make_graph_for_t3(x)
	#any(map(print, make_t3_objs_from_stream(stream)))
	##any(map(print, filter(line_is_relevant_to_task3, stream)))
	main()

