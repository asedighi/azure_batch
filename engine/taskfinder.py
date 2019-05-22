import importlib
import sys
import os
from os.path import isfile

import ntpath

from os import walk
from inspect import getmembers, isfunction

def task_importer(engine, task_dir, *args):

    module_name = ntpath.basename(task_dir)

    tasks = []
    for (dirpath, dirnames, filenames) in walk(task_dir):
        for f in filenames:
            if isfile(os.path.join(dirpath, f)) and not (f.endswith('__init__.py') or f.endswith('json')):
                tasks.extend([f])
        break


    """
    find task modules and import them
    """
    for i in tasks:
        try:
            mod_to_import = module_name + "." + os.path.splitext(i)[0]
            print("About to import: {}".format(mod_to_import))
            mod = importlib.import_module(mod_to_import)
        except ImportError:
            print("unable to locate module: " + i)
            return (None, None)

        functions_list = [o for o in getmembers(mod) if isfunction(o[1])]

        print(functions_list)

        mod.do_action(engine, *args)




if __name__ == "__main__":
    module, modClass = task_importer("../tasks")