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


import datetime
import os
import sys
import time

from batchwrapper.azbatchstorage import AzureBatchStorage
from batchwrapper.azbatch import AzureBatch

if __name__ == '__main__':

    start_time = datetime.datetime.now().replace(microsecond=0)
    print('Start time: {}'.format(start_time))



    #Start by creating a storage interface
    storage = AzureBatchStorage()


    storage.addInputFilePath("a.txt")
    storage.addInputFilePath("b.txt")
    storage.uploadInputFiles()

    storage.addTaskFilePath("tasks/1_task.py")
    storage.addTaskFilePath("tasks/2_task.py")
    storage.uploadTaskFiles()

    my_batch = AzureBatch(storage)
    app = storage.getApplicationFiles()
    input_files = storage.getApplicationInputFiles()
    tasks = storage.getBatchTaskFiles()

    #my_pool = "azpool_155836035085950"

    my_pool = my_batch.get_available_pool()
    my_batch.repurpose_existing_pool(my_pool,app, input_files, tasks)

    #my_batch.use_exisiting_pool(my_pool)



    #my_batch.delete_all_pools()

    #my_batch.create_pool(app_resources=app, input_resources=input_files, task_files=tasks)





    job_id = my_batch.create_a_job()


    args = ['a.txt' , 'b.txt']

    my_batch.add_tasks_to_job(job_id, args)

