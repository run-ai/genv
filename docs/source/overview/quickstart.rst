Quick start
===========

.. contents::
   :depth: 2
   :backlinks: none

Tutorial
--------
This is a guide to help you get started with Genv.

.. note::

   This tutorial uses Genv locally on your GPU machine.
   If you want to work with one or more remote machines, check out the quick start tutorial of :doc:`remote features <../remote/overview>`.

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

First, you will need to :doc:`install <installation>` Genv.
You can choose your preferred way of installation: :ref:`using <Install Using pip>` :code:`pip` or :ref:`Conda <Install Using Conda>`.

Verify the installation by running the command:

.. code-block:: shell

   $ genv status
   Environment is not active

You can see that the terminal is not running in an active environment.

.. note::

   You can run :code:`genv` to see all the available commands.

Let's see device information:

.. code-block:: shell

   $ genv devices
   ID      ENV ID      ENV NAME        ATTACHED
   0
   1

We can see that we have two devices and that both of them are available.
This is because we don't have any GPU environment attached to any of them.

Let's now list the environments and we will see that there are no active environments yet:

.. code-block:: shell

   $ genv envs
   ID      USER            NAME            CREATED              PID(S)

Now, let's activate a new environment and give it a name:

.. code-block:: shell

   $ genv activate --name quick-start
   (genv) $

.. note::

   You can pass :code:`--no-prompt` to :code:`genv activate` to not change the shell prompt.

We can now rerun the :code:`genv envs` command and see our environment:

.. code-block:: shell

   $ genv envs
   ID      USER            NAME            CREATED              PID(S)
   13320   raz(1040)       quick-start     42 seconds ago       13320

Environments start detached from any GPUs when being first activated.
You can see this with the following command:

.. code-block:: shell

   $ nvidia-smi
   No devices were found

You can see that even though we have two GPUs on the machine, :code:`nvidia-smi` sees none of them.
Any `CUDA <https://developer.nvidia.com/cuda-toolkit>`__ application you will run will see no GPUs.

.. note::

   Genv sets an environment variable that controls the GPU indices CUDA uses to :code:`-1`.
   You can see this with the command:

   .. code-block:: shell

      $ echo $CUDA_VISIBLE_DEVICES
      -1

   However, :code:`nvidia-smi` is based on `NVML <https://developer.nvidia.com/nvidia-management-library-nvml>`__ and therefore is implemented differently in Genv using a :ref:`shim <Shims>`.
   You can see this with the command:

   .. code-block:: shell

      $ vim $(which nvidia-smi)

Let's now :ref:`attach <Attach an Environment to Devices>` devices to the environment.
We will :ref:`configure <Configure the Device Count>` the environment device count to 1 and let Genv pick the device index for us.

.. code-block:: shell

   $ genv config gpus 1
   $ genv attach

You can now run :code:`genv status` and see information about your activated environment.
Also, running :code:`nvidia-smi` will show us our single device:

.. code-block:: shell

   $ nvidia-smi
   ...
   |===============================+======================+======================|
   |   0  Tesla T4            Off  | 00000000:00:04.0 Off |                    0 |
   | N/A   52C    P8    17W /  70W |      0MiB / 15109MiB |      0%      Default |
   |                               |                      |                  N/A |
   +-------------------------------+----------------------+----------------------+
   ...

You can see the device index and its memory information.
In our case, it's device at index 0 that has just a bit less than 16GB of GPU memory.

Now, if we don't need all the memory of the GPU, we can configure the environment GPU memory capacity with the command:

.. code-block:: shell

   $ genv config gpu-memory 4g

Rerunning :code:`nvidia-smi` will now show the configured amount as the total memory of the device:

.. code-block:: shell

   $ nvidia-smi
   ...
   |===============================+======================+======================|
   |   0  Tesla T4            Off  | 00000000:00:04.0 Off |                    0 |
   | N/A   52C    P8    17W /  70W |      0MiB / 3814MiB  |      0%      Default |
   |                               |                      |                  N/A |
   +-------------------------------+----------------------+----------------------+
   ...

If you ran any GPU consuming application, you will see its used memory in the output of :code:`nvidia-smi` as well as its process.

If you also have more than a single device in your machine, you can attach the second device to your environment with the command:

.. code-block:: shell

   $ genv attach --index 1

Now, :code:`nvidia-smi` will show information on both devices.

That wraps the Genv quick start tutorial.

Where to Go Next
----------------
If you have more than a single GPU machine, it is recommended to follow the quick start tutorial of Genv :doc:`remote features <../remote/overview>`.

Additionally, you should check out the :doc:`usage guide <../usage/usage>` to learn more Genv features.
