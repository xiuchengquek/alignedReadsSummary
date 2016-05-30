#!/usr/bin/env python

__author__ = 'quek'

import argparse
import sys
import os
from collections import defaultdict
import re
import json


def parse_args(args):
    """
    function to parse arguments from the environment. Wrapped in a function to allow unit testing.
    Also make sure that only either dir is file is supplied, throws an error when both are supplied
     :param args: sys.argv
    :return:Convert the strings to objects and assign them as attributes of the namespace.
            Return the populated namespace. using the parse_args() method of ArgumentParser
            Namespace(foo='FOO', x=None)

    """
    parser = argparse.ArgumentParser(description='Parse your tophat align summary')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action='store_true')
    parser.add_argument("-m", "--mode", help="input type is a directory or file", choices=['file', 'directory'], default='directory')
    parser.add_argument("-i", "--input", metavar='</dir> || file1,file2... ', help="provide a list of file or direcotry")
    parser.add_argument("-o", "--out", metavar='outfile.tsv', help="name of outputfile")

    return parser.parse_args(args)

def dict_totsv():
    pass

class summaryParser(object):
    """
    Object containing attributes and methods to parse align_summary.txt
    """

    def __init__(self, mode, variable):
        """
        initi requries a list of file or a directory containing the files
        """
        self.mode = mode
        if self.mode == 'file':
            self.file_list = variable.split(',')

        elif self.mode =='directory':
            self.file_list = os.listdir(variable)
            self.file_list = [os.path.join(variable, x ) for x in self.file_list]

    def getStats(self, f, aligned=None):
        """
        method to look at the next 3 lines of file and get required stats
        """
        regex = re.compile('([\d|.%]+)')
        input =  regex.search(f.next()).group(1)
        mapped = regex.search(f.next()).group(1)
        multiple = regex.search(f.next()).group(1)

        if aligned:
            """
            things are done differently here
            """
            aligned_pairs = regex.search(aligned).group(1)
            return { 'Aligned' : int(aligned_pairs), 'Multiple' : int(input), 'Discordant' : int(mapped)}
        return { 'Input' : int(input), 'Mapped' : int(mapped), 'Multiple' : int(multiple) }



    def parseFile(self, file):
        """ function to find the no of
        1) Input Reads,
        2) Mapped Reads
        3) Multi Mappers
        """
        return_dict = {}
        with open(file) as f:
            for line in f:
                line = line.strip()

                if line:
                    if line.startswith('Left'):
                        return_dict['Left'] = self.getStats(f)
                    elif line.startswith('Right'):
                        return_dict['Right'] = self.getStats(f)
                    elif line.startswith('Aligned'):
                        return_dict['Aligned'] = self.getStats(f, line)
                    elif line.startswith('Reads'):
                        return_dict['Reads'] = self.getStats(f)
                    else:
                        matched_summary = re.search('([\d|.%]+)', line)
                        return_dict['Overall'] = matched_summary.group(1)

                        #return_dict['Summary'] = re.search('(\d+\.\d+%)', line).group(1)

        return return_dict

    def run(self):
        """
    Convert align summary file into dictionary
    :return: dictionary containin the following key and value

    {'filename' :
        {'Left' : {'Input' : <value>,
                    'Mapped':<value>,
                    'Multiple Alignments' : <value>
                    },
        {'Right' :   {'Input' : <value>,
                'Mapped' : <value>,
                'Multiple Alignments' : <value>
                },
        'overall' : <value>
        }
    }
    """
        return_dict = {}
        for x in self.file_list:
            return_dict[x] = self.parseFile(x)

        return return_dict





def calculator(input_dict):
    """

    :param input_dict: from summary.
    :return: stack ready json
    """
    return_array = []
    return_dict = {}
    x = 0
    for keys, value in input_dict.iteritems():
        if 'labels' in return_dict:
            return_dict['labels'].append(keys)
        else:
            return_dict['labels'] = [keys]


        for subkey, subval in value.iteritems():
            if subkey == 'Aligned':
                total_reads = subval['Aligned']
                discordant_reads = subval['Discordant']
                multi_mappers  = subval['Multiple']
                unique_concordant = total_reads - discordant_reads - multi_mappers
                discordant_reads = {'name' : keys,  'x' : x, 'y' : discordant_reads }
                unique_concordant = {'name' : keys, 'x' : x, 'y' : unique_concordant }
                multi_mappers = {'name' : keys,  'x' : x, 'y' : multi_mappers }


                if subkey in return_dict:
                    return_dict[subkey]['values'][0].append(unique_concordant)
                    return_dict[subkey]['values'][1].append(discordant_reads)
                    return_dict[subkey]['values'][2].append(multi_mappers)


                else:
                    return_dict[subkey] = {}
                    legend =  ['Unique-Concordant', 'Discordant', 'Multi-Mappers']
                    return_dict[subkey]['legend'] = legend
                    return_dict[subkey]['values'] = []

                    return_dict[subkey]['values'].append([unique_concordant])
                    return_dict[subkey]['values'].append([discordant_reads])
                    return_dict[subkey]['values'].append([multi_mappers])




            elif subkey == 'Overall':
                pass
            else:

                total_reads = subval['Input']
                mapped_reads = subval['Mapped']
                multi_mappers  = subval['Multiple']
                unique_reads = mapped_reads -  multi_mappers
                unmapped_reads = total_reads - mapped_reads
                unmapped_reads = {'name' : keys, 'x' : x, 'y' : unmapped_reads }
                unique_reads = {'name' : keys,  'x' : x, 'y' : unique_reads }
                multi_mappers = {'name' : keys,  'x' : x, 'y' : multi_mappers }


                if subkey in return_dict:
                    return_dict[subkey]['values'][0].append(unmapped_reads)
                    return_dict[subkey]['values'][1].append(unique_reads)
                    return_dict[subkey]['values'][2].append(multi_mappers)


                else:
                    return_dict[subkey] = {}
                    legend = ['Unmapped', 'Unique',  'Multi-Mappers']
                    return_dict[subkey]['legend'] = legend
                    return_dict[subkey]['values'] = []
                    return_dict[subkey]['values'].append([unmapped_reads])
                    return_dict[subkey]['values'].append([unique_reads])
                    return_dict[subkey]['values'].append([multi_mappers])
        x = x + 1




    return return_dict













if __name__ == '__main__' :
    args = parse_args(sys.argv[1:])
    return_dict = summaryParser(args.mode, args.input).run()
    with open(args.out,'w+') as f:
        json.dump(calculator(return_dict), f, sort_keys=True, indent=4, separators=(',', ': '))













