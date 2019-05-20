# Copyright (c) Microsoft Corporation
#
# All rights reserved.
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
# @author: asedighi

from azure.common.credentials import ServicePrincipalCredentials
import json 

import os
import time


DEFAULT_LOCATION = 'eastus'



def getRandomizer():
    timestamp = int(time.time()* 100000)
    return str(timestamp)



def find_file_path(name, path="../../.."):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

    return None


class ReadConfig():
    def __init__(self, name=''):
        config = name

        json_config = ''

        if os.path.isfile(config):
            print("Found {}".format(config))
            with open(config) as json_data:
                json_config = json.load(json_data)

        else:
            my_path = find_file_path(name, "../../../../")
            print("found: {}".format(my_path))
            if os.path.isfile(my_path):
                with open(my_path) as json_data:
                    json_config = json.load(json_data)

        return  json_config




class AzureCredentials():
   
    def __init__(self):
        '''
        Constructor
        '''
        self.cred = ''

        if os.path.isfile('./credentials.json'):
            print("Found credentials.json in current directory")
            with open('./credentials.json') as json_data:
                self.cred = json.load(json_data)

        else:
            my_path = find_file_path("credentials.json", "../../../../")
            if my_path == None:
                print("I was not able to find the credentials.json file... exiting....")
                exit(-1)
            print("found: {}".format(my_path))
            if os.path.isfile(my_path):
                with open(my_path) as json_data:
                    self.cred = json.load(json_data)

        '''
        application or client id are the same
        '''
        self.batch_account_name = self.cred['BATCH_ACCOUNT_NAME']
        self.batch_account_key = self.cred['BATCH_ACCOUNT_KEY']
        self.batch_account_url = self.cred['BATCH_ACCOUNT_URL']
        self.storage_account_name = self.cred['STORAGE_ACCOUNT_NAME']
        self.storage_account_key = self.cred['STORAGE_ACCOUNT_KEY']
        self.LOCATION = DEFAULT_LOCATION

        
        
    def getLocation(self):
        return self.LOCATION
    
    def setLocation(self, location):
        self.LOCATION = location
    
    
    def getBatchAccountName(self):
        return self.batch_account_name
    
    def getBatchAccountKey(self):
        return self.batch_account_key
    
    def getBatchAccountUrl(self):
        return self.batch_account_url
    
    def getStorageAccountName(self):
        return self.storage_account_name

    def getStorageAccountKey(self):
        return self.storage_account_key



'''
{
	"BATCH_NODE_COUNT": 2,
	"v": "BASIC_A1",
	"BATCH_OS_PUBLISHER":"Canonical",
	"BATCH_OS_TYPE": "UbuntuServer",
	"BATCH_OS_VERSION": 16
}
'''



class AzureBatchConfiguration():

    def __init__(self):

        self.batch = ''


        if os.path.isfile('./batch.json'):
            print("Found batch.json in current directory")
            with open('./batch.json') as json_data:
                self.batch = json.load(json_data)

        else:
            my_path = find_file_path("batch.json", "../../../../")

            print("Found: {}".format(my_path))

            if os.path.isfile(my_path):
                with open(my_path) as json_data:
                    self.batch = json.load(json_data)

        self.batch_node_count = self.batch['BATCH_NODE_COUNT']
        self.batch_vm_size = self.batch['BATCH_VM_SIZE']
        self.batch_os_publisher = self.batch['BATCH_OS_PUBLISHER']
        self.batch_os_type = self.batch['BATCH_OS_TYPE']
        self.batch_os_version = self.batch['BATCH_OS_VERSION']
        self.batch_engine_name = self.batch['BATCH_ENGINE_NAME']


    def getNodeCount(self):
        return self.batch_node_count

    def getVMSize(self):
        return self.batch_vm_size


    def getOSPublisher(self):
        return self.batch_os_publisher

    def getOSType(self):
        return self.batch_os_type

    def getOSVersion(self):
        return self.batch_os_version


    def getEngineName(self):
        return self.batch_engine_name



class TaskConfig():
    def __init__(self):

        self.task = ''
        if os.path.isfile('./task.json'):
            print("Found task.json in current directory")
            with open('./task.json') as json_data:
                self.task = json.load(json_data)

        else:
            my_path = find_file_path("task.json", "../../../../")

            print("found: {}".format(my_path))
            if os.path.isfile(my_path):
                with open(my_path) as json_data:
                    self.task = json.load(json_data)

        self.task_modules = self.task['TASK_MODULES']
        self.task_args = self.task['TASK_ARGS']
        self.task_output = self.task['TASK_OUTPUT_CONTAINER']

        self.task_modules_dir = self.task['TASK_MODULES_DIRECTORY']

    def getTaskModules(self):
        return self.task_modules

    def getTaskModulesDir(self):
        return self.task_modules_dir

    def getTaskArgs(self):
        return self.task_args

    def getOutputContainer(self):
        return self.task_output

