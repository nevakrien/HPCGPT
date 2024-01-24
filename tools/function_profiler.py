import read_perf as r_sample
import read_code_perf as r_code

from read_code_perf import FunctionData,LogData
from read_perf import PerfEventData

from os.path import join
from typing import List,Set
from dataclasses import dataclass

#from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor


from collections import defaultdict
import pandas as pd 

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


@dataclass
class PerfData:
    call: CallData
    data: Set[PerfEventData]  # Now using a set instead of a list

#bad code both buggy and slow keeping it for refrences
from bisect import bisect_left

def find_start_index(logs, start_time):
    """ Find the index of the first log after the start_time using binary search. """
    index = bisect_left([log.timestamp for log in logs], start_time)
    return index if index < len(logs) else None

def logs_for_func(func: FunctionData, sorted_logs) -> List[PerfEventData]:
    start_index = find_start_index(sorted_logs, func.start)
    if start_index is None:
        return []

    relevant_logs = []
    for log in sorted_logs[start_index:]:
        if log.timestamp > func.end:
            break
        relevant_logs.append(log)

    return relevant_logs

def _seperate_logs(calls, logs, funcs):
    logs.sort(key=lambda x: x.timestamp)
    total_logs = set()

    for c in calls:
        inner_logs = _seperate_logs(c.inner_calls, logs, funcs)
        call_logs = logs_for_func(c.function, logs)
        total_logs.update(call_logs)

        unique_call_logs = set(call_logs) - inner_logs
        # Convert to a sorted list when adding to funcs, if necessary
        funcs[c.function.name].append(PerfData(c, sorted(unique_call_logs, key=lambda x: x.timestamp)))

    return total_logs

def get_os_info(calls, system_logs):
    data = defaultdict(list)
    _seperate_logs(calls, system_logs, data)

    return {k: {'cycles': sum(sum(e.cycles for e in x.data) for x in v),
            'PID': set().union(*(set(e.process_id for e in x.data) for x in v))} for k, v in data.items()}


#Validation:
def check_processed(call):
    if not call.processed:
        return False

    if len(call.inner_calls)==0:
        return True

    return all(map(check_processed,call.inner_calls))

if __name__ == "__main__":
    file_path=join('results','combo')

    perf_samples=r_sample.parse_file(join(file_path,'output.txt'))
    raw_logs=r_code.parse_file(join(file_path,'code_perf_output.txt'))
    #function_calls=r_code.make_intervals(raw_logs)

    call_stack=make_call_stack(raw_logs)#,['gpt2'])

    print(check_processed(call_stack[0]))

    print(type(call_stack[0].function))
    print(len(call_stack))
    print(max(x.timestamp for x in perf_samples))
    print(max(x.seconds for x in raw_logs))
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

    perf_info=get_os_info(call_stack,perf_samples)
    print(perf_info)

