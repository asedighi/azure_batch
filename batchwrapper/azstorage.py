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



from batchwrapper.config import AzureCredentials

from batchwrapper.config import getRandomizer

import azure.storage.blob as azureblob
import azure.batch.models as batchmodels
import datetime
import os
import time



class AzureStorage():

    def __init__(self):

        configuration = AzureCredentials()
        random = getRandomizer()
        self.app_container_name = 'application-' + random
        self.input_container_name = 'input-' + random
        self.output_container_name = 'output-' + random

        self.account_name = configuration.getStorageAccountName()
        self.account_key = configuration.getStorageAccountKey()
        self.location = configuration.getLocation()
        self.blob_client = azureblob.BlockBlobService(account_name=self.account_name, account_key=self.account_key)


    def getDefaultAppContainer(self):
        return self.app_container_name


    def getDefaultInputContainer(self):
        return self.input_container_name


    def getDefaultOutputContainer(self):
        return self.output_container_name

    def createInputContainer(self, container_name='', file_path=''):
        """
        Uploads a local file to an Azure Blob storage container.

        :param str container_name: The name of the Azure Blob storage container.
        :param str file_path: The local path to the file.
        :rtype: `azure.batch.models.ResourceFile`
        :return: A ResourceFile initialized with a SAS URL appropriate for Batch
        tasks.
        """
        blob_name = os.path.basename(file_path)

        self.blob_client.create_container(container_name, fail_on_exist=False)
        print("\tCreated {}... ".format(container_name))

        print('Uploading file {} to container [{}]...'.format(file_path,
                                                              container_name))

        self.blob_client.create_blob_from_path(container_name,
                                                blob_name,
                                                file_path)

        sas_token = self.blob_client.generate_blob_shared_access_signature(
            container_name,
            blob_name,
            permission=azureblob.BlobPermissions.READ,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2))

        sas_url = self.blob_client.make_blob_url(container_name,
                                                  blob_name,
                                                  sas_token=sas_token)

        return batchmodels.ResourceFile(file_path=blob_name,
                                        blob_source=sas_url)



    def create_output_container(self, container_name=''):

        if(container_name==''):
            container_name=self.getDefaultOutputContainer()
        self.blob_client.create_container(container_name, fail_on_exist=False)
        print("\tCreated {}... ".format(container_name))
        output_container_sas_token = self._get_container_sas_token(container_name, azureblob.BlobPermissions.WRITE)
        return container_name, output_container_sas_token


    def _get_container_sas_token(self, container_name, blob_permissions):
        """
        Obtains a shared access signature granting the specified permissions to the
        container.

        :param str container_name: The name of the Azure Blob storage container.
        :param BlobPermissions blob_permissions:
        :rtype: str
        :return: A SAS token granting the specified permissions to the container.
        """
        # Obtain the SAS token for the container, setting the expiry time and
        # permissions. the shared access signature becomes valid immediately.
        container_sas_token = \
            self.blob_client.generate_container_shared_access_signature(
                container_name,
                permission=blob_permissions,
                expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=6))

        return container_sas_token



    def download_blobs_from_container(self,container_name, directory_path='./job_output'):
        """
        Downloads all blobs from the specified Azure Blob storage container.

        :param container_name: The Azure Blob storage container from which to
         download files.
        :param directory_path: The local directory to which to download the files.
        """
        print('Downloading all files from container [{}]...'.format(
            container_name))

        container_blobs = self.blob_client.list_blobs(container_name)

        for blob in container_blobs.items:
            destination_file_path = os.path.join(directory_path, blob.name)

            self.blob_client.get_blob_to_path(container_name,
                                               blob.name,
                                               destination_file_path)

            print('  Downloaded blob [{}] from container [{}] to {}'.format(
                blob.name,
                container_name,
                destination_file_path))

        print('  Download complete!')
