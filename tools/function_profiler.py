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

from os.path import join

def create_conversion_functions(std_start, std_end, perf_start, perf_end):
    """
    Create conversion functions based on start and end times from std::chrono and perf.

    Args:
    std_start (float): Start time from std::chrono.
    std_end (float): End time from std::chrono.
    perf_start (float): Start time from perf.
    perf_end (float): End time from perf.

    Returns:
    tuple of functions: (std_to_perf, perf_to_std)
    """
    # Calculate the scale and offset for conversion
    std_duration = std_end - std_start
    perf_duration = perf_end - perf_start
    scale = perf_duration / std_duration
    offset = perf_start - std_start * scale

    # Conversion functions
    def std_to_perf(std_time):
        """Convert std::chrono time to perf time."""
        return std_time * scale + offset

    def perf_to_std(perf_time):
        """Convert perf time to std::chrono time."""
        return (perf_time - offset) / scale

    return std_to_perf, perf_to_std

def analys(samples,calls):
    pass


if __name__ == "__main__":
    file_path=join('results','combo')

    perf_samples=r_sample.parse_file(join(file_path,'output.txt'))
    raw_logs=r_code.parse_file(join(file_path,'code_perf_output.txt'))
    function_calls=r_code.make_intervals(raw_logs)

    print(max(x.timestamp for x in perf_samples))
    print(max(x.seconds for x in raw_logs))
    #perf_samples.sort(key=lambda x: x.timestamp)
