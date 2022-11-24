Reference
=========

.. contents::
   :depth: 2
   :backlinks: none

Environment Variables
---------------------

:code:`GENV_BYPASS`

Bypass shim behaviors and use similar behavior to the original applications.
Default is :code:`0`.

----

:code:`GENV_MOCK_DEVICE_COUNT`

A mock for device count.
By default, it is queried using :code:`nvidia-smi`.
This is mainly for development environments on CPU machines where :code:`nvidia-smi` is not available.
----

:code:`GENV_MOCK_DEVICE_MEMORY`

A mock for device memory.
By default, it is queried using :code:`nvidia-smi`.
This is mainly for development environments on CPU machines where :code:`nvidia-smi` is not available.

----

:code:`GENV_TMPDIR`

Path of the temp directory where all state JSON files are stored.
Default is :code:`/var/tmp/genv`.

----

:code:`GENV_ALLOW_DEVICE_OVER_ALLOCATION`

Support attaching environments to a device even if memory cannot be guaranteed.
Default is :code:`0`.

.. _Shims:

Shims
-----

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
