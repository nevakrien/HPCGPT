from os.path import join
from collections import Counter
import numpy as np 
import matplotlib.pyplot as plt

class PerfEventData:
	event_source: str
	process_id: int
	timestamp: float
	cycles: int
	event_name: str
	memory_address: str
	function_name: str
	#event_context: str

	def __init__(self, split_data):
		if(type(split_data)==str):
			split_data=split_data.split()

		assert len(split_data)>6

		self.event_source = split_data[0]
		self.process_id = int(split_data[1])
		self.timestamp = float(split_data[2].rstrip(':'))
		self.cycles = int(split_data[3])
		self.event_name = split_data[4]
		self.memory_address = split_data[5]

		# Combine the remaining fields in the "code name" part
		self.function_name = split_data[6]
		for extra_field in split_data[7:]:
			self.function_name += ' ' + extra_field

	def to_dict(self):
		return {
			"event_source": self.event_source,
			"process_id": self.process_id,
			"timestamp": self.timestamp,
			"cycles": self.cycles,
			"event_name": self.event_name,
			"memory_address": self.memory_address,
			"function_name": self.function_name,
			#"event_context": self.event_context
		}

def plot_sep(processes):
	# Plotting
	for pid, events in processes.items():
	    timestamps = [e['timestamp'] for e in events]
	    cycles = [e['cycles'] for e in events]
	    colors = np.log10(cycles)  # Log scale for intensity

	    plt.figure(figsize=(10, 6))
	    scatter = plt.scatter(timestamps, cycles, c=colors, cmap='viridis', alpha=0.6)
	    plt.colorbar(scatter, label='Log10(Cycle Count)')
	    plt.title(f"Process ID: {pid}")
	    plt.xlabel("Timestamp")
	    plt.ylabel("Cycle Count")
	    plt.yscale('log')  # Log scale for y-axis
	    plt.grid(True)
	plt.show()

def plot(processes):
    plots_per_window=6
    num_processes = len(processes)
    num_windows = np.ceil(num_processes / plots_per_window).astype(int)

    for window in range(num_windows):
        plt.figure(figsize=(15, 10))  # Adjust the figure size as needed
        for i in range(plots_per_window):
            index = window * plots_per_window + i
            if index >= num_processes:
                break
            pid, events = list(processes.items())[index]

            timestamps = [e['timestamp'] for e in events]
            cycles = [e['cycles'] for e in events]
            colors = np.log10(cycles)  # Log scale for intensity

            ax = plt.subplot(2, 3, i+1)  # Adjust the grid dimensions as needed
            scatter = ax.scatter(timestamps, cycles, c=colors, cmap='viridis', alpha=0.6)
            plt.colorbar(scatter, ax=ax, label='Log10(Cycle Count)')
            ax.set_title(f"Process ID: {pid}")
            ax.set_xlabel("Timestamp")
            ax.set_ylabel("Cycle Count")
            ax.set_yscale('log')  # Log scale for y-axis
            ax.grid(True)

        plt.tight_layout()
    plt.show()


def plot_combined(processes,excludes=[]):
	fig, ax = plt.subplots(figsize=(15, 10))
	global scatter_plots
	scatter_plots = {}

	colors = plt.cm.hsv(np.linspace(0, 1, len(processes)))

	for i, pid in enumerate(processes.keys()):
		if(i in excludes):
			continue
		events = processes[pid]
		timestamps = [e['timestamp'] for e in events]
		cycles = [e['cycles'] for e in events]
		color = colors[i]

		ax.scatter(timestamps, cycles, c=[color for _ in cycles], alpha=0.6, label=f'process {i}')


	ax.set_yscale('log')
	ax.set_xlabel("Timestamp")
	ax.set_ylabel("Cycle Count")
	ax.set_title("Events for Multiple Processes")
	ax.grid(True)
	ax.legend()

	#plt.ion()
	plt.show()

def plot_include(processes,include):
	a=list(range(len(processes)))
	plot_combined(processes,[x for x in a if x not in include])



if __name__=="__main__":

	with open(join('results','output.txt')) as f:
		data=f.read()

	data=[PerfEventData(x).to_dict() for x in data.split('\n') if x]

	#print(data[:3])
	#print(max([d['cycles'] for d in data]))
	#print(Counter([d['event_name'] for d in data]))
	#print(len(Counter([d['process_id'] for d in data])))
	proces={k:[] for k in set([d['process_id'] for d in data])}
	for d in data:
		proces[d['process_id']].append(d)

	for v in proces.values():
		v.sort(key=lambda d:d['timestamp'])

	#print({k:len(v) for k,v in proces.items()})
	print(len(proces))
	#plot(proces)
	plot_combined(proces)
	#plot_include(proces,[4,5,6,0])