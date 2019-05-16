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

import os

from batchwrapper.azstorage import AzureStorage

class AzureBatchStorage():

    def __init__(self):

        self.storage = AzureStorage()
        self.input_files = list()
        self.app_files = list()
        self.input_container = self.storage.getDefaultInputContainer()
        self.app_container = self.storage.getDefaultAppContainer()
        self.output_container = self.storage.getDefaultOutputContainer()
        self.batch_input_files = list()
        self.batch_application_files = list()




    def addInputFilePath(self, file_path):

        exists = os.path.isfile(os.path.realpath(file_path))
        if exists:
            self.input_files.append(os.path.realpath(file_path))
            print("Currently, {} data files are in list to be uploaded".format(len(self.input_files)))
            for l in self.input_files:
                print("file: {}".format(l))
        else:
            print("File {} not found.  Please check name and path".format(file_path))


    def uploadInputFiles(self):

        temp = list()
        temp = [
            self.storage.createInputContainer(self.input_container, file_path)
            for file_path in self.input_files]

        self.batch_input_files.extend(temp)

        self.input_files.clear()

    def addApplicationFilePath(self, file_path):
        exists = os.path.isfile(os.path.realpath(file_path))
        if exists:
            self.app_files.append(os.path.realpath(file_path))
            print("Currently, {} executible files are in list to be uploaded".format(len(self.app_files)))
            for l in self.app_files:
                print("file: {}".format(l))
        else:
            print("File {} not found.  Please check name and path".format(file_path))



    def uploadApplicationFiles(self):

        temp = list()
        temp = [
            self.storage.createInputContainer(self.app_container, file_path)
            for file_path in self.app_files]
        self.batch_application_files.extend(temp)

        print(self.batch_application_files)

        self.app_files.clear()

    def getAppResourceFiles(self):
        if len(self.app_files) > 0:
            self.uploadApplicationFiles()
        return self.batch_application_files

    def getAppInputFiles(self):
        if len(self.input_files) > 0:
            self.uploadInputFiles()
        return self.batch_input_files



    def createOutputFolder(self):
        container_name, output_container_sas_token = self.storage.create_output_container(self.output_container)
        ### create a output.json file
        self.addApplicationFilePath("output.json")
        self.uploadApplicationFiles()


if __name__ == '__main__':

    a = AzureBatchStorage()
    a.addInputFilePath("ab.txt")
    a.addInputFilePath("a.txt")
    a.addInputFilePath("b.txt")
    a.addApplicationFilePath("task.py")