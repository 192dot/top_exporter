#!/usr/bin/env python3
import psutil
import argparse
import heapq
import platform
import subprocess

DEFAULT_INTERVAL = 0.001
DEFAULT_MAX_PROCS = 10


def print_top_procs(num_procs=DEFAULT_MAX_PROCS, sort_memory=False, interval=DEFAULT_INTERVAL, generic_os=False):
    """
    :param num_procs: limit result by this number of processes
    :param sort_memory: sort top results by memory usage
    :param interval: interval to capture processes' CPU usage
    :param generic_os: makes use of psutil library.
    note if top -b (batch mode) is not available, it will fall to True
    :type num_procs: int
    :type sort_memory: bool
    :type generic_os: bool
    :type interval: float
    :return: None
    """

    # in case of failure, fall back to using psutil library
    fall_back_to_psutil = False

    if generic_os is False:
        # Mac OS
        if platform.system() == 'Darwin':
            if sort_memory is False:
                cmd = 'top -l 1'
            else:
                cmd = 'top -l 1 -o mem'
        # Linux
        else:
            if sort_memory is False:
                cmd = 'top -b -n 1'
            else:
                cmd = 'top -b -n 1 -o +%MEM'

        cmd_list = cmd.split()

        try:
            process = subprocess.Popen(cmd_list,
                                       shell=False,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            procs_raw = process.stdout.readlines()
            process_raw_top(procs_raw, num_procs)
            #return

        except Exception as e:
            print(str(e))
            print('got exception when running os top command, will try the Python library')
            fall_back_to_psutil = True
        #print(process.stderr.readline)

        if process.stderr.readline():
            print(process.stderr.readline())
            print('got error when running os top command, will try the Python library')
            fall_back_to_psutil = True

    if generic_os is True or fall_back_to_psutil is True:
        get_top_procs_psutil(num_procs=num_procs, sort_memory=False, interval=interval)
        print('here')


def process_raw_top(procs_raw, num_procs):
    """process raw top and output data in Prometheus format
    :param procs_raw: blob of string output from top
    :return: None
    """
    result = ''
    for line in procs_raw:
        if line and line[0].isdigit() is False:
            continue
        else:
            #TODO: process raw top
            print('here')


def get_top_procs_psutil(num_procs=DEFAULT_MAX_PROCS, sort_memory=False, interval=DEFAULT_INTERVAL):
    """
    :param num_procs: limit result by this number of processes
    :param sort_memory: sort top results by memory usage
    :param interval: interval to capture processes' CPU usage
    :type num_procs: int
    :type sort_memory: bool
    :type interval: float
    :return: None
    """

    # heap storing a tuple of process cpu/memory usage and pid
    max_heap = []
    # dict to store the full info of processes
    proc_dict = {}

    for proc in psutil.process_iter():
        try:
            # get process information
            proc_id = proc.pid
            proc_info = proc.as_dict(
                attrs=['name', 'username', 'memory_info', 'status'])
            proc_info['vms'] = proc.memory_info().vms / (1024 * 1024)
            proc_dict[proc_id] = proc_info

            if sort_memory is True:
                negative_vms = 0 - proc_info['vms']
                heapq.heappush(max_heap, (negative_vms, proc_id))
            else:
                # TODO: make iter length a variable
                cpu_total = []
                for _ in range(2):
                    p_cpu = proc.cpu_percent(interval=interval)
                    cpu_total.append(p_cpu)
                proc_cpu_percent = float(sum(cpu_total)) / len(cpu_total)
                negative_cpu = 0 - proc_cpu_percent
                heapq.heappush(max_heap, (negative_cpu, proc_id))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # process output
    result_lines = min(len(max_heap), num_procs)

    while result_lines > 0:
        neg_usage, pid = heapq.heappop(max_heap)
        print(pid, proc_dict[pid])
        result_lines -= 1

    return


def main():
    """main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int,
                        default=DEFAULT_MAX_PROCS,
                        help="limit result to this number of processes")
    parser.add_argument("-i", "--interval", type=float,
                        default=DEFAULT_INTERVAL,
                        help="interval to capture CPU usage samples")
    parser.add_argument("-m", "--memory", action="store_true",
                        help="sort by memory usage")
    parser.add_argument("-g", "--generic", action="store_true",
                        default=False,
                        help="uses Python's psutil. Work for most OS but slow")
    # TODO: implement this
    #parser.add_argument("-s", "--save", action="store_true",
    #                    help="save result in Prometheus format")

    args = parser.parse_args()

    print_top_procs(num_procs=args.number,
                    sort_memory=args.memory,
                    interval=args.interval,
                    generic_os=args.generic)


if __name__ == "__main__":
    main()
