import read_perf as r_sample
import read_code_perf as r_code

from read_code_perf import FunctionData,LogData
from read_perf import PerfEventData

from os.path import join
from typing import List,Generator
from dataclasses import dataclass

#from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor


from collections import defaultdict
import pandas as pd 

import copy

@dataclass
class CallData():
    function : FunctionData
    inner_calls :list#will be a List['CallData'] at the end
    processed :bool = False

@dataclass
class PerfDataTime():
    call:CallData 
    time :float


#this code was really slow until I used specifcly ThreadPoolExecutor 
#ProcessPoolExecutor had too nuch overhead? 
#serial code was also very slow not sure why.
def make_call_stack(raw_logs: List[LogData],ignores=[]):
    if not raw_logs:
        return []

    start_log = raw_logs[0]
    tasks = []
    inner_calls = []
    
    with ThreadPoolExecutor() as executor:
        for log in raw_logs[1:]:
            if log.name in ignores:
                continue
            if start_log is None:
                start_log = log
                continue

            if log.name == start_log.name:
                entry = CallData(FunctionData(start_log, log), [])
                future = executor.submit(process_call, entry, inner_calls)
                tasks.append((future, entry))
                start_log = None
                inner_calls = []
            else:
                inner_calls.append(log)

        assert start_log is None

    ans = [future.result() for future, _ in tasks]

    
    return ans

def process_call(call_data: CallData, inner_logs: List[LogData]):
    call_data.inner_calls = make_call_stack(inner_logs)
    call_data.processed = True
    return call_data

#PLOTING

def print_call_stack(call_data, level=0):
    indent = " " * (level * 4)  # 4 spaces per indentation level
    start = call_data.function.start
    end = call_data.function.end
    duration = end - start
    print(f"{indent}{call_data.function.name}: Start = {start}, End = {end}, Duration = {duration}")

    for inner_call in call_data.inner_calls:
        print_call_stack(inner_call, level + 1)

#PROFILE
def _calculate_time(calls,funcs):
    total_time=0

    for c in calls:
        inner_time=_calculate_time(c.inner_calls,funcs)
        call_time=c.function.end-c.function.start
        total_time+=call_time

        funcs[c.function.name].append(PerfDataTime(c,call_time-inner_time))

    return total_time

def calculate_time(calls):
    data=defaultdict(lambda:[])
    _calculate_time(calls,data)
    return {k:sum(x.time for x in v) for k,v in data.items()}


class CallIntevals():
    #function : FunctionData
    #inner_calls# =[]#will be a List['CallData'] at the end
    #i=0

    def __init__(self,function):
        self.function=function
        self.inner_calls=[]
        self.i=0


    def get_atributed(self,t):
        """
        we are assuming that t is in the range for self
        note that this method modifys the class
        we are expecting you to be responsible and call in in assending orders of t
        this also assumes the call tree u put here is valid 
        """
        #print(f"got {t} in func {self.function.name}")
        
        if(self.i==len(self.inner_calls)):
            print(f"no call stack remaining returining {self.function.name}")
            return self

        c=self.inner_calls[self.i]
        if c.function.start>t:
            print(f"inner func {c.function.name} is too late with {c.function.start}returning {self.function.name}")
            return self
        
        if(t>c.function.end):
            print(f"inner func {c.function.name} is too early returning incrementing")
            self.i+=1
            return self.get_atributed(t)

        print(f"inner func {c.function.name} is valid calling it")
        return c.get_atributed(t)


    @staticmethod
    def from_call(call:CallData):
        x=CallIntevals(call.function)
        with ThreadPoolExecutor() as pool:
            x.inner_calls=list(pool.map(CallIntevals.from_call,call.inner_calls))
        
        x.function.start#-=7.5#-=6.33 #magic pref number got from expirementing around until it made sense
        x.function.end#-=7.5#-=6.33
        x.inner_calls.sort(key=lambda x:x.function.start)#,reverse=True)
        return x


def get_perfstuff(call,perf_data):
    data=defaultdict(lambda:[])
    call=CallIntevals.from_call(call)
    assert len(call.inner_calls)

    perf_data.sort(key=lambda x: x.timestamp)

    for p in perf_data[-10:]:
        a=call.get_atributed(p.timestamp)
        #print(call.i)
        data[a.function.name].append(p)

    return data




#Validation:
def check_processed(call):
    if not call.processed:
        return False

    if len(call.inner_calls)==0:
        return True

    return all(map(check_processed,call.inner_calls))

def align_timers(raw_logs,perf_samples):
    min_sample=(min(x.timestamp for x in perf_samples))
    min_func=(min(x.seconds for x in raw_logs))

    offset=min_func-min_sample
    for log in raw_logs:
        log.seconds-=offset

if __name__ == "__main__":
    file_path=join('results','combo')

    perf_samples=r_sample.parse_file(join(file_path,'output.txt'))
    raw_logs=r_code.parse_file(join(file_path,'code_perf_output.txt'))
    #function_calls=r_code.make_intervals(raw_logs)
    perf_samples=[x for x in perf_samples if x.event_source=='TinyGPT_benchma']
    #align_timers(raw_logs,perf_samples)

    call_stack=make_call_stack(raw_logs)#,['gpt2'])

    print(check_processed(call_stack[0]))

    print(type(call_stack[0].function))
    print(len(call_stack))
    

    max_sample=(max(x.timestamp for x in perf_samples))
    max_func=(max(x.seconds for x in raw_logs[1:-1]))

    min_sample=(min(x.timestamp for x in perf_samples))
    min_func=(min(x.seconds for x in raw_logs[1:-1]))

    print(f'{min_func}<=inner funcs<={max_func}')
    print(f'{min_sample}<=linux sample<={max_sample}')
    print(f'\npart of program we measured:{(max_func-min_func)/(max_sample-min_sample)}\n')

    print(f'data size on inner funcs: {len([x for x in perf_samples if min_func<x.timestamp<max_func])}\n')
    #perf_samples.sort(key=lambda x: x.timestamp)
    
    assert len(call_stack)==1

    #print(print_call_stack(call_stack[0]))
    #print(calculate_time(call_stack))
    times=calculate_time(call_stack)
    total_time=sum(times.values())
    df={k:[v,v/total_time] for k,v in times.items()}
    df=pd.DataFrame(df,index=['time spend','frac'])
    #df['frac']=df['time spend']/df['time spend'].sum()
    print(df)

    print(2*'\n')

    perf_info=get_perfstuff(call_stack[0],perf_samples)
    print(perf_info.keys())

