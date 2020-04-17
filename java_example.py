from subprocess import *
import sys


def java_runner(*args) -> list:
    process = Popen(['java', '-jar'] + list(args), stdout=PIPE, stderr=PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != b'' and len(line) > 0 and line.endswith(b'\n'):
           ret.append(line[:-1].decode('utf-8'))

    #for i in range(len(ret)):
    #    print("line: {}:{}".format(i,ret[i]))
    stdout, stderr = process.communicate()

    ret += stdout.split(b'\n')
    if stderr != b'':
        ret += stderr.split(b'\n')
    ret.remove(b'')
    return ret

'''

You need to replace:

sys.stdout.write(nextline)

with:

sys.stdout.write(nextline.decode('utf-8'))

or maybe:

sys.stdout.write(nextline.decode(sys.stdout.encoding))

You will also need to modify if nextline == '' to if nextline == b'' since:

>>> '' == b''
False

'''



if __name__ == '__main__':

    print("Received input: {}".format(sys.argv[1:]))

    jar_args = ['pi.jar']  # Any number of args to be passed to the jar file

    result = java_runner(*jar_args)

    for i in range(len(result)):
        print("line: {}:{}".format(i,result[i]))

