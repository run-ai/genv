Advanced Usage
==============

.. contents::
   :depth: 2
   :backlinks: none

Multiple Terminals
------------------
When you activate an environment by running :code:`genv activate` in your terminal, a new environment gets created and registered.

Every activated terminal runs within an environment.

genv supports running multiple terminals within the same environment.
This could be useful in many ways.
For example, when running an application in one terminal, and monitoring its GPU resources using :code:`nvidia-smi` in another terminal.

If you have an activated terminal and you want to open another terminal in the same environment, you need to first query the environment identifier using the command:

.. code-block:: shell

   echo $GENV_ENVIRONMENT_ID

Then, open another terminal and pass the argument :code:`--id` to your :code:`genv activate` command.
For example:

.. code-block:: shell

   genv activate --id 1667

Your terminal should now be activated in the same environment.
You could verify it by running :code:`nvidia-smi` and seeing information about the GPUs of your environment.

genv automatically configures the terminal with the environment configuration and attaches the terminal to the devices that are attached to the environment.

.. _Using sudo:

Using :code:`sudo`
------------------
Much of genv functionality is based on environment variables.
You can see this by running the following command from an activated environment:

.. code-block:: shell

   env | grep GENV_

By default, when using :code:`sudo`, environment variables are not preserved.
You can see this by running the same command from an activated environment:

.. code-block:: shell

   sudo env | grep GENV_

This means that all that would not work when using :code:`sudo` from an activated environment.

To fix this, pass :code:`-E` or :code:`--preserve-env` to the :code:`sudo` command.
For example:

.. code-block:: shell

   sudo -E env | grep GENV_

In addition to that, some genv functionality is implemented as shims.
When applications such as :code:`nvidia-smi` and :code:`docker` are being executed inside an activated environment, their respective shims get called instead.
genv modifies the environment variable :code:`PATH` to do so.

You can see this by running the following command from an activated environment:

.. code-block:: shell

   echo $PATH

When using :code:`sudo`, the environment variable :code:`PATH` is not preserved even when passing :code:`-E` or :code:`--preserve-env`.
You can see this by running the same command from an activated environment:

.. code-block:: shell

   sudo -E bash -c 'echo "$PATH"'

This means that shims would not be executed.

To solve this, you can explicitly preserve :code:`PATH` by passing :code:`env "PATH=$PATH"` after the :code:`sudo` command.
For example:

.. code-block:: shell

   sudo -E env "PATH=$PATH" bash -c 'echo "$PATH"'

Alternatively, if you don't want to preserve :code:`PATH`, you can just wrap the executed program with :code:`which`.
For example:

.. code-block:: shell

   sudo -E `which nvidia-smi`

.. note::

   Make sure that you also pass :code:`-E` to preserve all genv environment variables

Running Containers
------------------
When running containers using a :code:`docker run` command from an active environment, the :code:`docker` :ref:`shim <Shims>` is executed.

It is responsible for making the container accessible to devices attached to the environment, as well as propagating some of genv environment variables.

Thanks to these environment variables, processes running in such containers are marked as part of the active environment.
This is necessary when running :code:`nvidia-smi` in an active environment, as the :code:`nvidia-smi` :ref:`shim <Shims>` queries the environment variables of GPU consuming processes in order to identify the ones running in the same environment.

The problem is that containers can run as a different user than the shell they are executed in, and they typically run as root.

This means that permissions may be required in order to query processes running in containers, even when queried from the same shell that executed the container.
For example, when running :code:`nvidia-smi` from a non-root shell in an active environment, it will not be able to identify processes running in containers from the same environment if they run as root.

There are two ways to handle this issue.

The easiest way is to run :code:`nvidia-smi` with sufficient permissions :ref:`using <Using sudo>` :code:`sudo`:

.. code-block:: shell

   sudo -E `which nvidia-smi`

The other option is to run the container as non-root.
You can do that by passing :code:`--user $(id -u):$(id -g)` to the :code:`docker run` command, or by editing the Dockerfile.
