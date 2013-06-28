#!/usr/bin/python
import glob, zlib, sys, os, subprocess, select

dec = zlib.decompressobj()
trace_started = False
leftovers = ''
for filename in sys.argv[1:]:

    # Whilst going through the python learning experience just take the
    # code from systrace.py. Ideally we would just read the file normally
    atrace_args = ['cat', filename]
    adb = subprocess.Popen(atrace_args, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

#    with open(filename, 'r') as compressed:
#        with open(filename + '-decompressed', 'w') as expanded:
    while True:
        ready = select.select([adb.stdout, adb.stderr], [], [adb.stdout, adb.stderr])

        if adb.stdout in ready[0]:
            out = leftovers + os.read(adb.stdout.fileno(), 4096)
            out = out.replace('\r\n', '\n')
            if out.endswith('\r'):
                out = out[:-1]
                leftovers = '\r'
            else:
                leftovers = ''
            if not trace_started:
                lines = out.splitlines(True)
                out = ''
                for i, line in enumerate(lines):
                    if line == 'TRACE:\n':
                        sys.stdout.write("downloading trace...")
                        sys.stdout.flush()
                        out = ''.join(lines[i+1:])
                        trace_started = True
                        break
                    elif 'TRACE:'.startswith(line) and i == len(lines) - 1:
                        leftovers = line + leftovers

            if len(out) > 0:
                out = dec.decompress(out)
                print out
            result = adb.poll()
            if result is not None:
                break;
    #            data = dec.decompress(compressed.read())
    #            expanded.write(data)
