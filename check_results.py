"""
@author = Drew Hoo

Script to check the accuracy of our program according to the instructions:
"We will read the output file produced by your program where you stored the K files closest to each query. We will read it line by line. If the category that most frequently appears on these K files is the same category as the input file, then you get one point. Otherwise you get zero points. This will produce a total score."

tl;dr
For any K, where K is the number of similar images to be returned, if our program returns a majority of the similar images as the same category as the query (input image), then we get a point, else zero.

Returns a percentage
"""
import sys
import pdb
import time

def create_dicts(db_decode, query_decode):
    db_dict = {} 
    query_dict = {}
    with open(db_decode, 'r') as db:
        for line in db:
            temp = line.rstrip().split()
            db_dict[temp[0]] = temp[1]
    with open(query_decode, 'r') as q:
        for line in q:
            temp = line.rstrip().split()
            query_dict[temp[0]] = temp[1]
    return db_dict, query_dict

def check(output, k, db_dict, query_dict):
    majority = int(k) / 2 + 1
    correct = 0
    total = 0
    with open(output, 'r') as out:
        for line in out:
            total += 1
            output_line = line.rstrip().split()
            if len(output_line) < 6:
                print '\nOutput len < 5: len = {}'.format(len(output_line))
                print output_line
                print 'at line: {}\n'.format(total-1)
            else:
                query_label = query_dict.get(output_line[0])
                output_line.pop(0)
                counter = 0
                for x in output_line:
                    if db_dict.get(x) == query_label:
                        counter +=1
                if counter >= majority:
                    correct += 1
    return correct, total

"""
./test_solution_exec ./Test1/output/database_decode_key ./Test1/output/queries_decode_key ./Test1/output/this_is_the_output 5 ./Test1/output/performance_file
"""

if __name__ == '__main__':
    t0 = time.clock()
    cmdline_args = sys.argv
    db_decode = cmdline_args[1]
    query_decode = cmdline_args[2]
    output = cmdline_args[3]
    k = cmdline_args[4]
    performance = cmdline_args[5]

    db_dict, query_dict = create_dicts(db_decode, query_decode)

    correct, total = check(output, k, db_dict, query_dict)

    with open(performance, 'w') as f:
        performance = float(correct) / float(total)
        f.write(str(performance))

    print time.clock() - t0
