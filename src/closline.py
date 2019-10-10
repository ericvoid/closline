#!/usr/bin/python

#Copyright (C) 2011 by Ben Brooks Scholz

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import json

from httplib import HTTPSConnection
from urllib import urlencode
from sys import argv
from sys import exit
from optparse import OptionParser

# parse command line options
parser = OptionParser()

# optimization level options
parser.add_option("-s", action="store_const", const="simple", dest="optimize")
parser.add_option("-a", action="store_const", const="advanced", dest="optimize")
parser.add_option("-w", action="store_const", const="whitespace", dest="optimize")

# warning level options
parser.add_option("-q", action="store_const", const="quiet", dest="warning")
parser.add_option("-d", action="store_const", const="default", dest="warning")
parser.add_option("-v", action="store_const", const="verbose", dest="warning")

# pretty print option
parser.add_option("-p", action="store_true", dest="pprint")

(options, args) = parser.parse_args()

# check for filename argument
if len(args) == 0:
    print "Missing argument."
    exit()

# set the optimization type according to the parsed options
if options.optimize == "advanced":
    optimize_level = "ADVANCED_OPTIMIZATIONS"
    print "Compiling Javascript with advanced optimizations...\n"
elif options.optimize == "whitespace":
    optimize_level = "WHITESPACE_OPTIMIZATIONS"
    print "Compiling Javascript without whitespace...\n"
else:
    optimize_level = "SIMPLE_OPTIMIZATIONS"
    print "Compiling Javascript with simple optimizations...\n"

# set the warning type according to the parsed options
if options.warning == "verbose":
    warning_level = "VERBOSE"
elif options.warning == "quiet":
    warning_level = "QUIET"
else:
    warning_level = "DEFAULT"
    
# handle output file names
file_path = argv.pop()
input_js = open(file_path).read()    
comp_name = file_path[:len(file_path)-3] + ".min.js"

params = [
    ('js_code', input_js),
    ('compilation_level', optimize_level),
    ('output_format', 'json'),
    ('output_info', 'compiled_code'),
    ('output_info', 'statistics'),
    ('output_info', 'errors'),
]

if options.pprint:
    # define the POST parameters with pretty print
    params.append(('formatting', 'pretty_print'))

# prepare the connection
headers = { "Content-type": "application/x-www-form-urlencoded" }
connect = HTTPSConnection('closure-compiler.appspot.com')

# make the HTTP request for compiled code
connect.request('POST', '/compile', urlencode(params), headers)
compile_response = connect.getresponse()

if compile_response.status != 200:
    print 'unexpected API response'
    print 'status:', compile_response.status
    print 'reason:', compile_response.reason
    print 'msg:', compile_response.msg
    exit(1)

response_data = compile_response.read()

# close the connection
connect.close()

if not response_data:
    print 'unexpected API response'
    print 'empty response'
    exit(1)

output = json.loads(response_data)

if "errors" in output:
    for entry in output["errors"]:
        print u"error: {}".format(entry["error"])
        print entry["line"]
        print '(line:{} col:{})'.format(entry["lineno"], entry["charno"])
        print

    print "Failed."
    exit(1)

else:
    with open(comp_name, 'w') as out_file:
        out_file.write(output['compiledCode'])
        out_file.close()

    print "Complete."
