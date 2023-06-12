Python SDK
==========

.. contents::
   :depth: 3
   :backlinks: none

Overview
--------
The Python SDK is available at :code:`genv.sdk`.

This SDK can be used by Python applications to use Genv features such as activating environments, attaching and detaching devices, and locking over-subscribed devices.

Installing the SDK
~~~~~~~~~~~~~~~~~~
The Python SDK comes as part of the Genv :doc:`installation <../overview/installation>` out of the box.

Importing the SDK
~~~~~~~~~~~~~~~~~
To use the Python SDK, add the following :code:`import` command to your Python script:

.. code-block:: python

    import genv.sdk

Using Environments
------------------
If you are not familiar with the concept of environments in Genv, it is recommended to go over the shell usage :doc:`guide <./usage>`.

Activating an Environment
~~~~~~~~~~~~~~~~~~~~~~~~~
To activate an environment, use the method :code:`genv.sdk.activate`.

This method acts as a context manager and provides an easy way to activate a scoped Genv environment.
Upon entering, an environment will be created, and upon exiting, the environment will be deactivated.

You can also configure the environment straight from the :code:`genv.sdk.activate()` call by passing the argument :code:`config: genv.sdk.Env.Config`.

You can activate an environment for the entire script by wrapping your :code:`main`.
For example:

.. code-block:: python

    import genv.sdk

    def main():
        pass

    if __name__ == "__main__":
        with genv.sdk.activate(config=genv.sdk.Env.Config(gpus=1, gpu_memory="4g")):
            main()

You can also activate an environment for a specific method.
For example when using a `Ray task <https://docs.ray.io/en/latest/ray-core/tasks.html>`__:

.. code-block:: python

    import genv.sdk
    import ray

    @ray.remote
    def my_function():
        with genv.sdk.activate(config=genv.sdk.Env.Config(name="my-function", gpus=1)):
            pass

Configuring the Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can configure your environment after activating it using :code:`genv.sdk.configure`.
For example:

.. code-block:: python

    import genv.sdk

    with genv.sdk.activate():
        name = input("How should I call the Genv environment?\n")
        genv.sdk.configure(genv.sdk.Env.Config(name=name))

Querying the Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can query the configuration of your environment using :code:`genv.sdk.configuration`.
For example:

.. code-block:: python

    import os
    import genv.sdk

    with genv.sdk.activate(config=genv.sdk.Env.Config(name=str(os.getpid()))):
        print(genv.sdk.configuration())

Using Devices
-------------
If you are not familiar with the concept of device attachments in Genv environments, it is recommended to go over the shell usage :ref:`guide <Using Devices in an Environment>`.

Attach Devices
~~~~~~~~~~~~~~
When activating an environment, it will be attached to devices if its device count is configured.

For example, by specifying the environment configuration argument :code:`gpus`, Genv will attach this amount of devices to the newly activated environment:

.. code-block:: python

    import genv.sdk

    with genv.sdk.activate(config=genv.sdk.Env.Config(gpus=1)):
        print(genv.sdk.attached())

You can also attach devices later using :code:`genv.sdk.attach()`.
For example:

.. code-block:: python

    import genv.sdk

    with genv.sdk.activate():
        print(genv.sdk.attached())
        genv.sdk.configure(genv.sdk.Env.Config(gpus=1))
        genv.sdk.attach()
        print(genv.sdk.attached())

Reference
---------
.. py:function:: genv.sdk.active()

    Returns whether running in an active environment.

    :rtype: bool

.. py:function:: genv.sdk.activate(*, eid: Optional[str] = None, config: Optional[Env.Config] = None)

    A context manager for activating an environment for the current process.

    Configures the environment if configuration is specified.
    Attaches devices if device count is configured.

    Raises :code:`RuntimeError` if already running in an active environment.

    :param eid: Environment identifier
    :param config: Environment configuration
    :rtype: None

.. py:function:: genv.sdk.attached()

    Returns the indices of devices attached to the current environment.

    Indices are in host namespace even when running in a container.

    Raises :code:`RuntimeError` if not running in an active environment.

    :rtype: Iterable[int]

.. py:function:: genv.sdk.configuration()

    Returns the current environment configuration.

    Raises :code:`RuntimeError` if not running in an active environment.

    :rtype: Env.Config

.. py:function:: genv.sdk.configure(config: Env.Config)

    Configures the current environment.

    :param config: Environment configuration
    :rtype: None

.. py:function:: genv.sdk.eid()

    Returns the current environment identifier if running in an active environment.

    :rtype: Optional[str]

.. py:function:: genv.sdk.lock()

    A context manager for obtaining exclusive access to the attached devices.

    Does nothing if not running in an active environment or not attached to devices.

    :rtype: None
