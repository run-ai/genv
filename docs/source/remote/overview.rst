.. _Remote Overview:

Overview
========

Genv is an environment management software for GPUs.
It manages all GPUs on a single machine.

Users can create environments and specify GPU resource requirements such as device count and GPU memory.
Genv will then find an available GPU for the environment and will make sure that no one else uses it.

This is mostly relevant for machines with multiple GPUs that several users share.

Genv also includes remote features to help managing shared GPUs accross multiple machines using :code:`genv remote` commands.

Users can list all active environments and see information about all devices in all the remote hosts.

Users can also use Genv to activate a GPU environment on a remote host.
They can specify GPU resource requirements and Genv will look for a device on a remote host with enough available resources, connect to it with SSH and automatically create and configure an environment there.

Quick start
-----------
This is a guide to help you get started with remote features in Genv.

First, you will need to :doc:`install <installation>` Genv on your local machine and one or more remote hosts.

In my case, I have two remote machines: :code:`gpu-server-1` with a single GPU and :code:`gpu-server-2` with two GPUs.

Now, create a hostfile named :code:`hostfile.txt` with the hostnames of your remote hosts.
We will pass it as argument :code:`--hostfile` to all :code:`genv remote` commands.
It should look something like this:

.. code-block:: shell

   $ cat hostfile.txt
   gpu-server-1
   gpu-server-2

Let's see device information from all remote hosts:

.. code-block:: shell

   $ genv remote --hostfile hostfile.txt devices
   HOST               TOTAL    AVAILABLE
   gpu-server-1       1        1
   gpu-server-2       2        2

   Total 3 devices with 3 available on 2 hosts

We can see that we have three devices in total and that all of them are available.
This is because we don't have any GPU environment attached to any of them.

Let's open another terminal and connect to :code:`gpu-server-2` using SSH:

.. code-block:: shell

   $ ssh gpu-server-2

There, let's activate a new environment and attach to a GPU:

.. code-block:: shell

   $ genv activate --name my-env --gpus 1
   (genv) $

Now let's go back to our local terminal, and see all active environments on the remote hosts:

.. code-block:: shell

   $ genv remote --hostfile hostfile.txt envs
   HOST               ID      USER            NAME            CREATED
   gpu-server-2       15600   raz(1003)       my-env          42 seconds ago

   Total 1 environments on 2 hosts

Now let's ask Genv to activate an environment with a single GPU attached:

.. code-block:: shell

   $ genv remote --hostfile hostfile.txt activate --gpus 1
   (genv) gpu-server-1 $

You can now run :code:`genv status` and see information about your activated environment.

Let's exit the remote environment by executing :code:`exit`.

Now, let's ask Genv to activate a remote environment once again, but this time let's ask for two GPUs:

.. code-block:: shell

   $ genv remote --hostfile hostfile.txt activate --gpus 2
   Cannot find a host with enough available resources

We can see that Genv can't find a machine with enough available resources.
This is because we have only one machine with two GPUs, but one of them is being used by our local environment from before.

Let's deactivate the local environment on :code:`gpu-server-2` by executing :code:`genv deactivate`, and rerun the :code:`genv remote activate` command from before on the local host.
Now, Genv will activate a remote environment on :code:`gpu-server-2` and attach to both GPUs on it:

.. code-block:: shell

   $ genv remote --hostfile hostfile.txt activate --gpus 2
   (genv) gpu-server-2 $
