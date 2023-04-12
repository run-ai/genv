Quick start
===========

.. contents::
   :depth: 2
   :backlinks: none

Tutorial
--------
This is a guide to help you get started with Genv containers.

Before beginning, make sure that you are running on a GPU machine.
This could be either your local machine or a remote one over SSH.
In my case, I have two GPUs in my machine.

You can verify that by running the command:

.. code-block:: shell

   $ nvidia-smi
   Tue Apr  4 11:17:31 2023
   +-----------------------------------------------------------------------------+
   | NVIDIA-SMI 470.161.03   Driver Version: 470.161.03   CUDA Version: 11.4     |
   |-------------------------------+----------------------+----------------------+
   ...

First, you will need to :doc:`install <installation>` the Genv container toolkit.

Verify the installation by running the command:

.. code-block:: shell

   $ genv-docker run --rm ubuntu env | grep GENV_

You should then see that the environment variable :code:`GENV_ENVIRONMENT_ID` is set.

.. note::

   You can run :code:`genv-docker run --help` to see all the available commands.


Now let's run a container with a single GPU and a memory capacity of 42 MiB:

.. code-block:: shell

   $ genv-docker run -it --rm --gpus 1 --gpu-memory 42mi --entrypoint bash python:3
   $ root@6bce9a20c0cf:/# nvidia-smi
   ...
   |===============================+======================+======================|
   |   0  Tesla T4            Off  | 00000000:00:04.0 Off |                    0 |
   | N/A   43C    P8    10W /  70W |      0MiB /    42MiB |      0%      Default |
   |                               |                      |                  N/A |
   +-------------------------------+----------------------+----------------------+
   ...

As can be seen by running :code:`nvidia-smi` inside the container, the container is accessible to one GPU, and has a memory capacity.

.. warning::

   We are using here Docker image :code:`python:3` because currently the :code:`nvidia-smi` :ref:`shim <Shims>` of Genv requires Python 3.7 or higher.

Now, leave the container running and from another terminal let's query the active Genv environments:

.. code-block:: shell

   $ genv envs
   ID             USER            NAME            CREATED              PID(S)
   6bce9a20c0cf.. 0                               2 minutes ago        7067

As you can see, the container is registered as an active environment.

Let's also query the device attachments:

.. code-block:: shell

   $ genv devices
   ID      ENV ID         ENV NAME        ATTACHED
   0       6bce9a20c0cf..                 3 minutes ago
   1

And we can see that Genv provisioned GPU 0 for this container.

Let's run another container with similar specification as before, 1 GPU and a memory capacity of 42 MiB.
From inside, let's print the GPU UUID that is attached to the container using :code:`nvidia-smi -L`:

.. code-block:: shell

   $ genv-docker run -it --rm --gpus 1 --gpu-memory 42mi --entrypoint bash python:3
   $ root@610017efa8b8:/# nvidia-smi -L
   GPU 0: Tesla T4 (UUID: GPU-b8044599-97ce-62e8-93dd-91d874cdda5b)

Let's run the same :code:`nvidia-smi -L` command from our first container, and see that both containers are indeed attached to the same device:

.. code-block:: shell

   $ root@6bce9a20c0cf:/# nvidia-smi -L
   GPU 0: Tesla T4 (UUID: GPU-b8044599-97ce-62e8-93dd-91d874cdda5b)

If you have more than a single GPU in your machine, which is my case, you can follow the rest of the tutorial.

Let's exit both containers and clean up the state.

Now, we will run two containers once again and check the GPU UUID.
However, this time we will not specify a memory capacity for the container.

Here's the output from the first terminal:

.. code-block:: shell

   $ genv-docker run -it --rm --gpus 1 --entrypoint bash python:3
   root@9588db59d9b8:/# nvidia-smi -L
   GPU 0: Tesla T4 (UUID: GPU-b8044599-97ce-62e8-93dd-91d874cdda5b)

And here's the output from the second terminal:

.. code-block:: shell

   $ genv-docker run -it --rm --gpus 1 --entrypoint bash python:3
   root@2ad83ba2afb7:/# nvidia-smi -L
   GPU 0: Tesla T4 (UUID: GPU-3699c6f6-a062-21a2-f7a1-cf2fc1533dcb)

As you can see, the GPU UUIDs are different, which means that the containers are attached to different GPUs.

We can also check out the device provisioned by Genv from a third terminal:

.. code-block:: shell

   $ genv devices
   ID      ENV ID         ENV NAME        ATTACHED
   0       9588db59d9b8..                 42 seconds ago
   1       2ad83ba2afb7..                 31 seconds ago


Note that if you used :code:`docker` instead of :code:`genv-docker`, both containers would have been attached to GPU at index 1.
This is the `behavior <https://docs.docker.com/engine/reference/commandline/run/#gpus>`__ of argument :code:`--gpus` of :code:`docker run`.

With :code:`genv-docker`, the argument :code:`--gpus` defines the device count rather the device indices.
This amount of devices is then provisioned by Genv for the container.
For more information, see :ref:`here <Container Provisioning GPUs>`.

That wraps the Genv container toolkit quick start tutorial.

Where to Go Next
----------------
Check out the :doc:`usage guide <usage>` to learn about more features of the Genv container toolkit.
