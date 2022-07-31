#!/usr/bin/env python3
import psutil
import argparse
import heapq


def print_top_procs(max_lines=None, sort_memory=False):
    """
    :param max_lines: limit result by this number of processes
    :param sort_memory: sort top results by memory usage
    :type max_lines: int
    :type sort_memory: bool
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
                # TODO: make iter length and interval variables
                # TODO: speed improvement for gathering CPU percentage
                cpu_total = []
                for _ in range(3):
                    p_cpu = proc.cpu_percent(interval=0.001)
                    cpu_total.append(p_cpu)
                proc_cpu_percent = float(sum(cpu_total)) / len(cpu_total)
                negative_cpu = 0 - proc_cpu_percent
                heapq.heappush(max_heap, (negative_cpu, proc_id))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # process output
    result_lines = len(max_heap)
    if max_lines:
        result_lines = max_lines

    while result_lines > 0:
        neg_usage, pid = heapq.heappop(max_heap)
        print(pid, proc_dict[pid])
        result_lines -= 1

    return


def main():
    """main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number", type=int,
                        help="limit result to this number of processes")
    parser.add_argument("-m", "--memory", action="store_true",
                        help="sort by memory usage")
    # TODO: implement this
    #parser.add_argument("-s", "--save", action="store_true",
    #                    help="save result in Prometheus format")

    args = parser.parse_args()

    print_top_procs(max_lines=args.number, sort_memory=args.memory)


if __name__ == "__main__":
    main()
