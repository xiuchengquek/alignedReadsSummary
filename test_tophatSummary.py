__author__ = 'quek'

import unittest
from tophatSummary import parse_args, summaryParser, calculator
import os
import shutil
import mock
import copy





class summaryParserTestCase(unittest.TestCase):
    maxDiff = None
    def setUp(self):
        self.expected = { 'resources/example_a.txt' : {  'Left' : {'Input' : 29138443, 'Mapped' : 28246263, 'Multiple': 842580},
                                                    'Right' : {'Input' : 29138443, 'Mapped' : 28159401, 'Multiple': 839836},
                                                    'Aligned': {'Aligned': 27570485, 'Multiple': 807906, 'Discordant': 242546},
                                                    'Overall': '96.8%'}}
        self.expectedDouble = copy.deepcopy(self.expected)
        self.expectedDouble['resources/example_b.txt'] = self.expectedDouble['resources/example_a.txt']

    def test_getStats(self):
        m = iter(['Input     :  45094315',
        'Mapped   :  43581884 (96.6% of input)',
        'of these:   1681876 ( 3.9%) have multiple alignments (60012 have >20)'])
        return_dict = summaryParser('blah','blah').getStats(m)

        expected = {
            'Input' : 45094315,
            'Mapped' : 43581884,
            'Multiple' : 1681876,
        }

        self.assertDictEqual(expected,return_dict)

    def test_parseFile(self):
        file = 'resources/example_a.txt'
        return_dict = summaryParser('file','file').parseFile(file)
        self.assertDictEqual(self.expected['resources/example_a.txt'],return_dict)

    def test_filelist(self):
        files = 'resources/example_a.txt,resources/example_b.txt'
        args = parse_args(['--mode', 'file', '--input',files])

        self.assertEqual('file', args.mode)
        self.assertEqual(files, args.input)

        summary = summaryParser(args.mode, args.input)
        return_dict = summary.run()

        self.assertDictEqual(self.expectedDouble, return_dict)

        args = parse_args(['--mode', 'directory', '--input','resources'])
        summary = summaryParser(args.mode, args.input)
        return_dict = summary.run()

        self.assertDictEqual(self.expectedDouble, return_dict)


class calculatorTestCase(unittest.TestCase):
    maxDiff = None
    def setUp(self):
        self.mock = { 'resources/example_a.txt' : {  'Left' : {'Input' : 10000, 'Mapped' : 9000, 'Multiple': 500},
                                                            'Right' : {'Input' : 10000, 'Mapped' : 9000, 'Multiple': 500},
                                                            'Aligned': {'Aligned': 10000, 'Multiple': 500, 'Discordant': 500},
                                                            'Overall': '96.8%'},
                             'resources/example_b.txt'  : { 'Left' : {'Input' : 10000, 'Mapped' : 9000, 'Multiple': 500},
                                                            'Right' : {'Input' : 10000, 'Mapped' : 9000, 'Multiple': 500},
                                                            'Aligned': {'Aligned': 10000, 'Multiple': 500, 'Discordant': 500},
                                                            'Overall': '96.8%'}
        }

        self.expected = { 'Left' :
                              {
                                'legend' : ['Unmapped', 'Unique',  'Multi-Mappers'],
                                'values' :

                                         [[{ 'name' : 'resources/example_a.txt' , 'x' : 0, 'y': 1000 },
                                           { 'name' : 'resources/example_b.txt' , 'x' : 1, 'y': 1000 }],
                                          [{ 'name' : 'resources/example_a.txt' , 'x' : 0, 'y': 8500 },
                                           { 'name' : 'resources/example_b.txt' , 'x' : 1, 'y': 8500 }],
                                          [{ 'name' : 'resources/example_a.txt' , 'x' : 0, 'y': 500 },
                                           { 'name' : 'resources/example_b.txt' , 'x' : 1, 'y': 500 }]]

                                },
                             'Right' : {
                                 'legend' : ['Unmapped', 'Unique',  'Multi-Mappers'],
                                 'values' :

                                      [[{ 'name' : 'resources/example_a.txt' , 'x' : 0, 'y': 1000 },
                                           { 'name' : 'resources/example_b.txt', 'x' : 1, 'y': 1000 }],
                                          [{ 'name' : 'resources/example_a.txt', 'x' : 0, 'y': 8500 },
                                           { 'name' : 'resources/example_b.txt', 'x' : 1, 'y': 8500 }],
                                          [{ 'name' : 'resources/example_a.txt', 'x' : 0, 'y': 500 },
                                           { 'name' : 'resources/example_b.txt', 'x' : 0, 'y': 500 }]],

                             },
                            'Aligned' : {
                                'legend' : ['Discordant', 'Unique-Concordant',  'Multi-Mappers'],
                                'values' :

                                         [[{ 'name' : 'resources/example_a.txt' , 'x' : 0, 'y': 500 },
                                           { 'name' : 'resources/example_b.txt' , 'x' : 1, 'y': 500 }],
                                          [{ 'name' : 'resources/example_a.txt' , 'x' : 0, 'y': 9000 },
                                           { 'name' : 'resources/example_b.txt' , 'x' : 1, 'y': 9000 }],
                                          [{ 'name' : 'resources/example_a.txt' , 'x' : 0, 'y': 500 },
                                           { 'name' : 'resources/example_b.txt' , 'x' : 1, 'y': 500 }]],
                                },


                            'labels' : ['resources/example_a.txt', 'resources/example_b.txt'],


        }


    def test_calculation(self):



        return_dict= calculator(self.mock)

        self.assertListEqual(sorted(self.expected.keys()), sorted(return_dict.keys()))
        self.assertDictEqual(self.expected['Left'], return_dict['Left'])

        #self.assertListEqual(self.expected['Left'], return_dict['Left'])















if __name__ == '__main__':
    unittest.main()
