Usage
=====

.. contents::
   :depth: 3
   :backlinks: none

Introduction
------------
The best way to run Genv containers is with :code:`genv-docker`.

:code:`genv-docker` is an wrapper executable for :code:`docker` commands.
It sets the container runtime to Genv and converts some command line arguments to environment variables, which are then respected by the Genv container runtime.

However, using :code:`genv-docker` is not mandatory, and everything achieved with it could also be achieved by using the Genv container runtime directly.

Throughout this page you will see :code:`genv-docker` commands as well as matching :code:`docker` commands that can be used if :code:`genv-docker` is not available.

Running Containers
------------------
To run containers with Genv, just use :code:`genv-docker` instead of :code:`docker`:

.. code-block:: shell

   genv-docker run ...

Here's the equivalent :code:`docker` command:

.. code-block:: shell

   docker run --runtime=genv ...

The Genv container runtime activates an environment for the container.
You can see it with :code:`genv envs`.

.. _Container Provisioning GPUs:

Provisioning GPUs
-----------------
Normally, when using the argument :code:`--gpus` with :code:`docker`, its value specifies the device indices to attach the container to.

With :code:`genv-docker`, the argument :code:`--gpus` is interpreted differently.
Instead of specifying the device indices to attach to the container, it specifies the device count, which is the amount of GPUs to attach to the container:

.. code-block:: shell

   genv-docker run --gpus 1 ...

Here's the equivalent :code:`docker` command:

.. code-block:: shell

   docker run --runtime=genv -e GENV_GPUS=1 ...

Then, Genv provisions this amount of GPUs to the container and attaches the devices to it.
You can see it with :code:`genv devices`.

Configure the GPU Memory Capacity
---------------------------------
By default, when running containers with :code:`genv-docker`, no GPU memory capacity is set to the environment.
But just like you can :ref:`configure <Configure the GPU Memory Capacity>` the GPU memory capacity for environments, you can do the same for containers.

To do so, pass the argument :code:`--gpu-memory` to :code:`genv-docker`:

.. code-block:: shell

   genv-docker run --gpu-memory 4g ...

Here's the equivalent :code:`docker` command:

.. code-block:: shell

   docker run --runtime=genv -e GENV_GPU_MEMORY=4g ...

.. note::

   Note that this de-facto has effect only when being used together with argument :code:`--gpus` or the equivalent environment variable :code:`GENV_GPUS`.

Configure the Environment Identifier
------------------------------------
By default, the Genv container runtime uses the container identifier as the environment identifier.
This de-facto creates a new environment for the newly created container.

It is possible to manually set the environment identifier for the container.
This allows, for example, running containers in already activated environments.

To do so, pass the argument :code:`--eid` to :code:`genv-docker`:

.. code-block:: shell

   genv-docker run --eid my-env ...

Here's the equivalent :code:`docker` command:

.. code-block:: shell

   docker run --runtime=genv -e GENV_ENVIRONMENT_ID=my-env ...

Dry Run
-------
For every :code:`genv-docker` command, you can see the underlying :code:`docker` command by adding the argument :code:`--dry-run` to the command:

.. code-block:: shell

   genv-docker run --dry-run ...

More Features
-------------
You can see all the available features of :code:`genv-docker` with the following command:

.. code-block:: shell

   genv-docker run --help
