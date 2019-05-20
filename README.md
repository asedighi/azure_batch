# Azure Batch Wrapper

This project aims to provide a framework upon which the use of Azure Batch can be simpler.  The goal for the project was to enable a developer to get up and running with Azure Batch with 10 or so lines of code.  

The other purpose of this project will be to make batch more "real-time" and have it act like an interactive scheduler.

#How to use
you need to create/update credentials.json.  The template is there, but you need to add proper values


The rest is just a few lines of code.  batch_driver_example.py shows how this can be accomplished.  



**Start by creating a storage interface**
    
    storage = AzureBatchStorage()

**Upload your input resources to the storage**

    storage.addInputFilePath("a.txt")
    storage.addInputFilePath("b.txt")
**Upload the input files**
    storage.uploadInputFiles()


**Upload your task file**
This file needs to implement a method called do_action(self, *argv).  This method is your main business logic

    storage.addApplicationFilePath("task.py")

**Upload your application/business logic to Storage**
    storage.uploadApplicationFiles()
    
    
**Create a batch instance**

    my_batch = AzureBatch(storage)
    
**Register your input and application files with Batch**

    app = storage.getAppResourceFiles()
    input_files = storage.getAppInputFiles()


**Create a pool**

    my_batch.create_pool(app_resources=app, app_name="task.py", input_resources=input_files)


**You can use an already existing pool**
This will keep everything intact.  Nothing will change


    my_pool = "azpool_1558014841"
    my_batch.use_exisiting_pool(my_pool)


**Or, you can re-purpose an existing pool with new input files/exe**

    my_batch.repurpose_existing_pool(my_pool,app, "task.py", input_files)


**Create a new job**

    job_id = my_batch.create_a_job()


**Create a list of tasks/task input**

In this example, task.py will be called twice: once with a.txt and once with b.txt as input
    
    args = ['a.txt' , 'b.txt']

**Run the jobs/tasks on the newly created pool**

    my_batch.add_tasks_to_job(job_id, args)





**Other features:**

* You dont need to create a new pool.  You can reuse the pool already created for the same job
* repurpose an already created pool for a new job   
* Config files are there for pool sizing. etc.  
* the engine/task can create an output file, and submit that output file for it to be copied to Azure Blob
* Update/overwrite of config files (TODO)
* Error Handling (TODO)




**Example Task.py**

Task.py is currently the file name to be used for running a task by engine on Azure Batch.  


First, import the base class.  This is needed specially as more features are added to this framework

````
from engine.azbatchengine import AzureBatchEngine
````

TaskDo is the name of the class that takes in AzureBatchEngine base class.  You need to call the base class constructor
 

````
class TaskDo(AzureBatchEngine):
    def __init__(self):
        AzureBatchEngine.__init__(self)
````

do_action is the method that represents the business logic.  The arguments (args) are past in from the client driver shown above.  


    def do_action(self, *args):
        print('Hello world from do_action')
        print("the current working directory is: {}".format(os.getcwd()))

        for i in args:
            print("i need to do something to: {}".format(i))
        
        
        #### Do something here...

Once all done, you may want to upload the result file back into Azure Blob to be picked up (by the driver again perhaps). 

        self.addFileToUpload("a.txt")
        
        
  