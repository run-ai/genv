Reference
=========

.. contents::
   :depth: 2
   :backlinks: none

.. _Files:

Files
-----

Genv uses JSON files to keep its state.
These files are queried and modified by :code:`genv` commands.

You can take a look at the files using the command:

.. code-block:: shell

   cat ${GENV_TMPDIR:-/var/tmp/genv}/*.json

.. note::

   These state files are saved under :code:`/var/tmp/genv` by default.
   This can be configured with the environment variable :code:`GENV_TMPDIR`.

These files are created by Genv on the first use as well as the temp directory.
Genv makes sure that any Linux user would have permissions to these files.

This can be seen with the following command:

.. code-block:: shell

   ls -la ${GENV_TMPDIR:-/var/tmp/genv}

You can see that the directory was created with :code:`rwxrwxrwx` and the files with :code:`rw-rw-rw`.

----

envs.json
~~~~~~~~~

Information about active environments and their configuration.

----

devices.json
~~~~~~~~~~~~

Information about device attachments.

.. _Environment Variables:

Environment Variables
---------------------

:code:`GENV_BYPASS`

Bypass shim behaviors and use similar behavior to the original applications.
Default is :code:`0`.

----

:code:`GENV_TERMINATE_PROCESSES`

Control whether to actually terminate enforced processes or not.
Default is :code:`1`.

----

:code:`GENV_MOCK_COMPUTE_APPS_GPU_MEMORY`

Used GPU memory for compute apps in the :code:`nvidia-smi` mock shim.
Default is :code:`42mi`.

----

:code:`GENV_MOCK_COMPUTE_APPS_PROCESS_NAME`

Name of processes to be considered as compute apps in the :code:`nvidia-smi` mock shim.
Default is :code:`sleep` (e.g. :code:`sleep infinity`).

----

:code:`GENV_MOCK_DEVICE_COUNT`

Device count in the :code:`nvidia-smi` mock shim.
Default is :code:`2`.

----

:code:`GENV_MOCK_DEVICE_TOTAL_MEMORY`

Total device memory in the :code:`nvidia-smi` mock shim.
Default is :code:`16g`.

----

:code:`GENV_MOCK_DEVICE_USED_MEMORY`

Used device memory in the :code:`nvidia-smi` mock shim.
Default is :code:`10mi`.

----

:code:`GENV_TMPDIR`

Path of the temp directory where all state JSON files are stored.
Default is :code:`/var/tmp/genv`.

----

:code:`GENV_ALLOW_DEVICE_OVER_SUBSCRIPTION`

Support attaching environments to a device even if memory cannot be guaranteed.
Default is :code:`0`.

.. _Shims:

Shims
-----

A shim [#]_ is a small application that runs instead of the originally intended one and acts as a middleware.
It manipulates the input and output of the real application, and provides an easy way to de-facto change the behavior of the original application.

----

:code:`docker`

This shim modifies the argument :code:`--gpus` if passed.

When :code:`all` is passed, this shim passes the indices of all the devices that are attached to the environment.
When a device count is passed (e.g. :code:`--gpus 2`), this shim passes indices of this amount of devices that are attached to the environment.
Any other value is not supported at the moment.

----

:code:`nvidia-smi`

By default, :code:`nvidia-smi` shows information about all GPUs and processes.

It supports showing information about some of the devices by passing the argument :code:`--id` and specifying GPU indices.
It is also good to note that :code:`nvidia-smi` ignores the environment variable :code:`CUDA_VISIBLE_DEVICES` as it uses NVML and not CUDA.

This shim passes the argument :code:`--id` to :code:`nvidia-smi` and specifies the device indices that are attached to this environment.

It also filters out processes that are not from the current environment, and shows GPU memory information that is relevant only for this environment, by summing the used GPU memory of all processes in this environment.

.. [#] `Shim (computing) - Wikipedia <https://en.wikipedia.org/wiki/Shim_(computing)>`_
