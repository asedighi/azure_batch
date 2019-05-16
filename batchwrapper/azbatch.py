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
import sys

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batchauth
import azure.batch.models as batchmodels

from batchwrapper.config import AzureCredentials
from batchwrapper.config import AzureBatchConfiguration
from batchwrapper.config import getRandomizer
from batchwrapper.azbatchstorage import AzureBatchStorage
from azure.batch.models.resource_file import ResourceFile
from azure.batch.operations import PoolOperations

sys.path.append('.')
sys.path.append('..')


import common.helpers


class AzureBatch():

    def __init__(self, batch_storage_account):
        # Create a Batch service client. We'll now be interacting with the Batch
        # service in addition to Storage

        self.my_storage = batch_storage_account

        configuration = AzureCredentials()
        self.account_name = configuration.getBatchAccountName()
        self.account_key = configuration.getBatchAccountKey()
        self.account_url = configuration.getBatchAccountUrl()

        self.credentials = batchauth.SharedKeyCredentials(self.account_name,self.account_key)

        self.batch_client = batch.BatchServiceClient(self.credentials,base_url=self.account_url)


        batch_config = AzureBatchConfiguration()



        self.pool_count = batch_config.getNodeCount()
        self.pool_type = batch_config.getVMSize()
        self.pool_os = batch_config.getOSType()
        self.pool_publisher = batch_config.getOSPublisher()
        self.pool_os_ver = batch_config.getOSVersion()
        self.pool_engine_name = batch_config.getEngineName()

        self.my_storage.addApplicationFilePath("engine/"+batch_config.getEngineName())
        self.my_storage.addApplicationFilePath("batchwrapper/batch.json")
        self.my_storage.addApplicationFilePath("batchwrapper/__init__.py")
        self.my_storage.addApplicationFilePath("batchwrapper/credentials.json")
        self.my_storage.addApplicationFilePath("batchwrapper/config.py")

        self.my_storage.uploadApplicationFiles()


    def use_exisiting_pool(self, pool=''):

        if pool == '':
            print("Pool Name cannot be empty")
            exit(-1)

        print('Searching for  pool [{}]...'.format(pool))

        is_there_pool = self.batch_client.pool.exists(pool)

        print("{} search came back as: {}".format(pool, is_there_pool))

        if is_there_pool == False:
            print("Pool not found ... exiting....")
            exit(-1)

        self.pool_name = pool

        return self.pool_name


    def delete_pool(self, pool=''):
        self.use_exisiting_pool(pool)
        self.batch_client.pool.delete(pool)


    def delete_all_pools(self):

        pool_list = []
        pool_paged = self.batch_client.pool.list()
        for pool_name in pool_paged:
            pool_list.append(pool_name.id)

        for n in pool_list:
            self.delete_pool(n)

    def repurpose_existing_pool(self, pool='', app_resources='', app_name='', input_resources=''):

        self.use_exisiting_pool(pool)

        if app_resources == '':
            print(
                "App resources cannot be empty.  HINT: you get this object from AzureBatchStorage.getAppResourceFiles")
            exit(-1)

        if app_name == '':
            print("App name cannot be empty.  HINT: This python file needs to inherit from AzureBatchEngine")
            exit(-1)







    def create_pool(self, app_resources='', app_name='', input_resources=''):

        random = getRandomizer()
        self.pool_name = 'azpool_' + random

        print('Creating pool [{}]...'.format(self.pool_name))

        if app_resources == '':
            print("App resources cannot be empty.  HINT: you get this object from AzureBatchStorage.getAppResourceFiles")
            exit(-1)

        if app_name == '':
            print("App name cannot be empty.  HINT: This python file needs to inherit from AzureBatchEngine")
            exit(-1)

        # Specify the commands for the pool's start task. The start task is run
        # on each node as it joins the pool, and when it's rebooted or re-imaged.
        # We use the start task to prep the node for running our task script.

        #task_commands = list()

        #temp = list()

        #for i in input_resources:
        #    temp.extend(['cp -p {} $AZ_BATCH_NODE_SHARED_DIR'.format(i.file_path)])


        task_commands = [
            'mkdir -p $AZ_BATCH_NODE_SHARED_DIR/batchwrapper',
            'mkdir -p $AZ_BATCH_NODE_SHARED_DIR/engine',
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR'.format(app_name),
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR/engine/'.format(self.pool_engine_name),
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR/batchwrapper/'.format("credentials.json"),
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR/batchwrapper/'.format("batch.json"),
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR/batchwrapper/'.format("config.py"),
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR/batchwrapper/'.format("__init__.py"),
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR/engine/'.format("__init__.py"),
            'cp -p {} $AZ_BATCH_NODE_SHARED_DIR/'.format("__init__.py"),
        ]

        for i in input_resources:
            print("adding file: {}".format(i.file_path))
            task_commands.extend(['cp -p {} $AZ_BATCH_NODE_SHARED_DIR'.format(i.file_path)])

        task_commands.extend( ['curl -fSsL https://bootstrap.pypa.io/get-pip.py | python', 'pip install azure'])



        print("commands to be published: {}".format(task_commands))


        # Get the node agent SKU and image reference for the virtual machine
        # configuration.
        # For more information about the virtual machine configuration, see:
        # https://azure.microsoft.com/documentation/articles/batch-linux-nodes/

        sku_to_use, image_ref_to_use = \
            common.helpers.select_latest_verified_vm_image_with_node_agent_sku(self.batch_client, self.pool_publisher, self.pool_os, self.pool_os_ver)


        user = batchmodels.AutoUserSpecification(scope=batchmodels.AutoUserScope.pool, elevation_level=batchmodels.ElevationLevel.admin)

        resource_meta = list()
        resource_meta.extend(app_resources)
        resource_meta.extend(input_resources)


        new_pool = batch.models.PoolAddParameter(id=self.pool_name,
            virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
                image_reference=image_ref_to_use,
                node_agent_sku_id=sku_to_use),
            vm_size=self.pool_type,
            target_dedicated_nodes=self.pool_count,
            start_task=batch.models.StartTask(
                command_line=common.helpers.wrap_commands_in_shell('linux',
                                                                   task_commands),
                user_identity=batchmodels.UserIdentity(auto_user=user),
                wait_for_success=True,
                resource_files=resource_meta),
        )

        try:
            self.batch_client.pool.add(new_pool)
        except batchmodels.batch_error.BatchErrorException as err:
            print_batch_exception(err)
            raise

        return self.pool_name


    def create_a_job(self):

        job_id = getRandomizer()

        print('Creating job [{}]...'.format(job_id))

        job = batch.models.JobAddParameter(
            job_id,
            batch.models.PoolInformation(pool_id=self.pool_name))

        try:
            self.batch_client.job.add(job)
        except batchmodels.batch_error.BatchErrorException as err:
            print_batch_exception(err)
            raise

        return job_id


    def add_tasks_to_job(self, job_id, input_files):
        """
        Adds a task for each input file in the collection to the specified job.
        :param str job_id: The ID of the job to which to add the tasks.
        :param  input_file:  batchmodels.ResourceFile object
        """
        tasks = list()

        for task_id, task_input in enumerate(input_files):
            print('Adding {} to job {}...'.format(task_input, job_id))

            command = ['python $AZ_BATCH_NODE_SHARED_DIR/engine/{} {}'.format(self.pool_engine_name, task_input)]

            print("Command to be executed is: {}".format(command))
            tasks.append(batch.models.TaskAddParameter(
                    '{}_{}'.format(str(job_id), str(task_id)),
                    common.helpers.wrap_commands_in_shell('linux', command),
                    #resource_files=[i.file_path]
                    )
            )

        self.batch_client.task.add_collection(job_id, tasks)








def print_batch_exception(batch_exception):
    """
    Prints the contents of the specified Batch exception.

    :param batch_exception:
    """
    print('-------------------------------------------')
    print('Exception encountered:')
    if batch_exception.error and \
            batch_exception.error.message and \
            batch_exception.error.message.value:
        print(batch_exception.error.message.value)
        if batch_exception.error.values:
            print()
            for mesg in batch_exception.error.values:
                print('{}:\t{}'.format(mesg.key, mesg.value))
    print('-------------------------------------------')