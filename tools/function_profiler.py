# import sys
# import os

# # Get the directory of the current script
# current_dir = os.path.dirname(os.path.abspath(__file__))

# # Add the 'tools' directory to sys.path
# tools_dir = os.path.join(current_dir)
# print(tools_dir)
# if tools_dir not in sys.path:
#     sys.path.append(tools_dir)

import read_perf as r_sample
import read_code_perf as r_code

from read_code_perf import FunctionData,LogData

from os.path import join
from typing import List
from dataclasses import dataclass

from multiprocessing import Pool

@dataclass
class CallData():
    function : FunctionData
    inner_calls :list#will be a List['CallData'] at the end


#this is fairly slow... even tho its quite optimized.
#we are still moving a bunch of memory around gcing and using 1 thread 
#but for python this is pretty much as far as it goes
def make_call_stack(raw_logs : List[LogData]):
    ans=[]

    if len(raw_logs)==0:
        return ans
    
    start_log=raw_logs[0]
    inner_calls=[]

    with Pool() as pool:
        for log in raw_logs[1:]:
            if start_log==None:
                start_log=log 
                continue

            if(log.name==start_log.name):
                entry=CallData(
                        FunctionData(start_log,log),
                        inner_calls
                        )
                pool.apply_async(process_call,(entry,))
                ans.append(entry)
                start_log=None
                ans=[]
            else:
                inner_calls.append(log)
        
        assert start_log is None #checking all calls closed
        
        pool.close()  # No more tasks will be submitted to the pool
        pool.join()   # Wait for the worker processes to exit
    
    return ans

def process_call(x:CallData):
    x.inner_calls=make_call_stack(x.inner_calls)

if __name__ == "__main__":
    file_path=join('results','combo')

    perf_samples=r_sample.parse_file(join(file_path,'output.txt'))
    raw_logs=r_code.parse_file(join(file_path,'code_perf_output.txt'))
    function_calls=r_code.make_intervals(raw_logs)

    call_stack=make_call_stack(raw_logs)

    print(max(x.timestamp for x in perf_samples))
    print(max(x.seconds for x in raw_logs))
    #perf_samples.sort(key=lambda x: x.timestamp)
