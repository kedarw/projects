#!/usr/bin/python

import sys
import os
import re
from collections import defaultdict
from collections import Counter
import glob

ignore_list = ["Histogram: IO lengths of Write commands",
               "Histogram: IO lengths of Read commands",
               "Histogram: distance (in LBNs) between successive Write commands",
               "Histogram: distance (in LBNs) between successive Read commands",
               "Histogram: distance (in LBNs) between each command from the closest of previous 16",
               "Histogram: latency of IOs in Microseconds (us)",
               "Histogram: number of outstanding IOs when a new IO is issued",
               "Histogram: latency of IO interarrival time in Microseconds (us)"
               ]

def parse_stat_files(stats_dir):
    print ("Parsing stat files in directory : "+str(stats_dir))

    old_files = glob.glob(str(stats_dir)+"/stats*.2")
    for old_file in old_files:
        os.remove(old_file)

    stat_files = glob.glob(str(stats_dir)+"/stats*")

    no_of_files = 0
    exclude_keywords = ['Histogram', 'min', 'max', 'mean', 'count']

    for stat_file in stat_files:
        histos_data = defaultdict(list)

        with open(stat_file) as origin_file:
            histos = []
            histos_heading = ""
            for line in origin_file:
                found = re.findall('Histogram:', line)
                if found:
                    histos_heading = line.rstrip("\n")
                    histogram = histos_heading.split(",")
                    histos.append(histogram[0])
                if ',' in line and not any(keyword in line for keyword in exclude_keywords):
                    temp = line.rstrip("\n")
                    key_value = temp.split(",")
                    histos_data[histos_heading].append((int(key_value[1]), int(key_value[0])))

        unique_histos = set(histos) - set(ignore_list)

        f = file(str(stat_file)+".2", "w")

        for histo in unique_histos:
            f.write(str(histo)+'\n')
            f.write('min,0\nmax,0\nmean,0\ncount,0\nFrequency,Histogram Bucket Limit\n')

            data_lists = []
            for data in histos_data:
                if histo in data:
                    data_lists.append(histos_data[data])
            counters = Counter()
            for data_list in data_lists:
                counters.update(dict(data_list))
            cs = sorted(counters.items())
            temp = ""
            for item in cs:
                temp= temp + (str(item[1])+','+str(item[0])+'\n')
            f.write(temp)

        f.close()
        no_of_files = no_of_files + 1

    print ("Processed " + str(no_of_files) + " stat files successfully")

def main():
    if len(sys.argv) == 2:
        parse_stat_files(sys.argv[1])
    else:
        print "Usage: parse_vscsi_stats.py <directory_with_vscsi_stats_files_without_last / >"
        sys.exit(2)

if __name__ == "__main__":
    main()
