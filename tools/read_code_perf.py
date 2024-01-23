from os.path import join 
import math

class LogData():
	seconds : float #seconds
	name : str
	start : bool

	def __init__(self,s):
		x=s.split()
		
		assert len(x)==3

		if x[0]=='Started':
			self.start=True
		else:
			assert x[0]=='Ended'
			self.start=False

		self.name=x[1]
		self.seconds=float(x[2])

class FunctionData():
	start : float #seconds
	end : float
	name : str


	def __init__(self,s,e):
		assert(s.name==e.name)
		assert(s.start)
		assert(not e.start)

		self.name=s.name
		self.start=s.seconds
		self.end=e.seconds
	

def parse_file(file_path):
	with open(file_path) as f:
		data=f.read()

	#data= [x.split() for x in data.split('\n')]
	return [LogData(x) for x in data.split('\n') if x]

def make_intervals(data):
	funcs=set(x.name for x in data)
	funcs={k:[x for x in data if x.name==k] for k in funcs}
	funcs={k:[FunctionData(start,end) for start,end in zip(v[::2],v[1::2])] for k,v in funcs.items()}
	return funcs

def make_assement(call_list :FunctionData):
	diff=[(x.end-x.start)/1e6 for x in call_list] #/1e9 for nano->seconds
	
	s=sum(diff) #for seconds
	mean=s/len(diff)
	
	if(len(diff)!=1):
		var=sum((mean-x)**2 for x in diff)/(len(diff)-1)
		std=math.sqrt(var)
	else:
		std=0
	return {'mean':mean,'std':std,'calls':len(call_list)}



if __name__=="__main__":
	data=parse_file(join('results','combo','code_perf_output.txt'))
	funcs=make_intervals(data)
	funcs={k:make_assement(v) for k,v in funcs.items()}
	
	aseconds=[(k,v) for k,v in funcs.items()]
	aseconds.sort(key=lambda t:t[1]['mean'])
	aseconds=aseconds[::-1]

	print('')
	for k,v in aseconds:
		print(f'{k}: {v}')
	print('')