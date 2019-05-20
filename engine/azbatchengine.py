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



import sys

sys.path.append('.')
sys.path.append('..')
sys.path.append('/mnt/batch/tasks/shared/')
sys.path.append('/mnt/batch/tasks/shared/engine')
sys.path.append('/mnt/batch/tasks/shared/batchwrapper')

#print ("working sys path is: ")
#print (sys.path)

from batchwrapper.config import getRandomizer
from batchwrapper.config import AzureCredentials
from batchwrapper.config import ReadConfig
from batchwrapper.config import TaskConfig
from batchwrapper.config import find_file_path
import argparse
import ntpath
import azure.storage.blob as azureblob

class AzureBatchEngine():

    def __init__(self):



        configuration = AzureCredentials()

        self.account_name = configuration.getStorageAccountName()
        self.account_key = configuration.getStorageAccountKey()
        self.blob_client = azureblob.BlockBlobService(account_name=self.account_name, account_key=self.account_key)

        task = TaskConfig()

        self.container_name = task.getOutputContainer()
        self.blob_client.create_container(self.container_name, fail_on_exist=False)
        print("\tOutput Container to be used is: {}... ".format(self.container_name))


        self.file_list_to_upload = list()
        self.result_to_upload = ''


    def getOutputContainer(self):
        return self.container_name


    def readJsonConfigFile(self, name=''):
        if name == '':
            return
        return ReadConfig(name)


    def do(self, *args):
        #task = TaskDo()

        self.do_action(*args)

        #self.uploadResultData()
        self.uploadFiles()

    def do_action(self, *args):
        pass

    def addFileToUpload(self, file_name=''):


        #/mnt/batch/tasks/workitems/<job id>/job-<#>/<task id>/wd
        #/mnt/batch/tasks/shared
        name = find_file_path(file_name, "../../../../../")
        print("found file to upload: {}".format(name))
        if name != '':
            self.file_list_to_upload.extend([name])

        print("Will upload: {}".format(self.file_list_to_upload))



    def dataToUpload(self, data=''):
        if data != '':
            self.result_to_upload = data


    def uploadResultData(self):
        pass


    def uploadFiles(self):


        for output_file in self.file_list_to_upload:

            print('Uploading file {} to container [{}]...'.format(output_file, self.container_name))
            self.blob_client.create_blob_from_path(self.container_name, ntpath.basename(output_file), output_file)
            self.file_list_to_upload.remove(output_file)




if __name__ == '__main__':

    print("received input: {}".format(sys.argv[1:]))

    from task import TaskDo

    engine = TaskDo()
    engine.do(sys.argv[1:])


