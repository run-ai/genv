Usage
=====

.. contents::
   :depth: 3
   :backlinks: none

Environment Status
------------------
When using genv, you will be running inside environments.

You can see the status of your environment using the command:

.. code-block:: shell

   genv status

When not running in an active environment, you will see the following message:

.. code-block:: shell

   $ genv status
   Environment is not active

When running in an :ref:`active <Activating an Environment>` environment, you will see more information about your environment, like its identifier, attached GPUs and configuration.

Here's an example:

.. code-block:: shell

   $ genv status
   Environment is active (22716)
   Attached to GPUs at indices 0,1

   Configuration
      Name: my-environment
      Device count: 2

nvidia-smi
~~~~~~~~~~
When running :code:`nvidia-smi` from an activated environment, you will see information relevant only to the environment.

You will see information only about devices that are attached to the environment.
Their used GPU memory will show the GPU memory that is used only by processes from the environment.

You will also see only processes from the environment.

.. _Activating an Environment:

Activating an Environment
-------------------------
In order to use genv, you need to activate the environment using the command:

.. code-block:: shell

   genv activate

When activating an environment, it first gets detached from all GPUs on the machine.

You could see this by running :code:`nvidia-smi` and seeing the following output:

.. code-block:: shell

   $ nvidia-smi
   No devices were found

You will later :ref:`configure <Configuring an Environment>` the environment device count and :ref:`attach <Attach an Environment to Devices>` devices to it.

.. note::
   To see all available options run :code:`genv activate --help` from a non-activated terminal

To deactivate an environment use the following command:

.. code-block:: shell

   genv deactivate

.. _Configuring an Environment:

Configuring an Environment
--------------------------
After :ref:`activing <Activating an Environment>` your environment, you need to configure it.

.. note::

   To see all available options and configuration fields run :code:`genv config --help`

.. _Configure the Device Count:

Configure the Device Count
~~~~~~~~~~~~~~~~~~~~~~~~~~
Configuring the environment device count determines how many GPUs should be accessible to it when attaching devices.

This is done with the following command:

.. code-block:: shell

   genv config gpus <count>

Configure the Name
~~~~~~~~~~~~~~~~~~
Configuring the environment name is not mandatory, but it helps a lot when querying the active environments and devices, and is considered a good practice.

This is done with the following command:

.. code-block:: shell

   genv config name <name>

Printing the Current Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can print the current configuration of any field by running the same command as if you want to configure it, just without specifying any value.

For example, the following command would print you the environment name:

.. code-block:: shell

   genv config name

You can also print the entire configuration by not specifying any field name:

.. code-block:: shell

   genv config

Clearing the Current Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can clear the configuration by passing the argument :code:`--clear` to the configuration command.

This works both for field-specific configuration and for the entire configuration.

For example, the next command would clear the environment name:

.. code-block:: shell

   genv config name --clear

While the following command would clear the entire configuration:

.. code-block:: shell

   genv config --clear

Managing Configuration as Infrastructure-as-Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
genv lets you manage the GPU resources as infrastructure-as-code by letting you save and load environment configurations to and from the disk.

In your project root, create a directory named :code:`.genv` using the command:

.. code-block:: shell

   mkdir -p .genv

.. note::

   The :code:`-p` argument just causes the command to not fail in case the directory already exists

You can verify genv recognizes the directory by running:

.. code-block:: shell

   genv home

~~~~~~~~~~~~~~~~~~~~
Saving Configuration
~~~~~~~~~~~~~~~~~~~~
You can save the configuration to the disk by running:

.. code-block:: shell

   genv config --save

You can also keep your saved configuration up to date by adding the argument :code:`--save` whenever you reconfigure the environment or clear the configuration.

.. _Loading Configuration:

~~~~~~~~~~~~~~~~~~~~~
Loading Configuration
~~~~~~~~~~~~~~~~~~~~~
You can load the configuration from the disk by running:

.. code-block:: shell

   genv config --load

Note that genv will automatically load the saved configuration when you activate an environment from your project root directory (as long as you don't pass :code:`--no-load` to :code:`genv activate`).

.. _Attach an Environment to Devices:

--------------------------------
Attach an Environment to Devices
--------------------------------
After :ref:`activing <Activating an Environment>` an environment and :ref:`configuring <Configuring an Environment>` its device count, you need to attach GPUs to it.

This is done using the command:

.. code-block:: shell

   genv attach

genv will look for available GPUs for your environment.

If there are not enough GPUs available, or the configured device count is greater than the number of devices in the machine, an error message will be printed to the screen and your environment will be detached.

If there are enough GPUs available, genv will attach them to the environment and make them unavailable for other environments.

You can verify that the environment is attached to GPUs by running :code:`nvidia-smi`.
It will show information only about the GPUs that are attached to your environment.

Note that in case your environment configuration gets :ref:`loaded <Loading Configuration>` upon activation, genv will also automatically try to attach devices to your environment (as long as you don't pass :code:`--no-attach` to :code:`genv activate`).

Detaching an Environment
~~~~~~~~~~~~~~~~~~~~~~~~
As long as your environment is active and attached to devices, no one else can use them.

In case you want to stop using the attached devices, and release them for someone else to use, you need to detach your environment from them using the following command:

.. code-block:: shell

   genv detach

You can verify that your environment is detached by running :code:`nvidia-smi` and seeing the following output:

.. code-block:: shell

   $ nvidia-smi
   No devices were found

Reattaching an Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~
In case you :ref:`reconfigure <Configure the Device Count>` the device count of your environment, you need to reattach your environment by rerunning the :code:`genv attach` command.

List Environments
-----------------
To see information about all active environments use the following command:

.. code-block:: shell

   genv envs

.. note::

   To see all available options run :code:`genv envs --help`

The information includes:

* Environment identifier
* Linux username and user identifier
* Environment name (if configured)
* Creation time
* Identifiers of all root processes in this environment

Here's a sample output:

.. code-block:: shell

   $ genv envs
   ID      USER            NAME            CREATED              PID(S)
   1573    paul(1004)      Yesterday       27 minutes ago       1573
   12167   john(1005)      Norwegian Wood  7 hours ago          12167

List Devices
------------
To see information about all devices use the following command:

.. code-block:: shell

   genv devices

.. note::

   To see all available options run :code:`genv devices --help`

The information includes:

* Device index
* Environment identifier of the attached environment
* Environment name of the attached environment (if configured)
* Attachment time

Here's a sample output:

.. code-block:: shell

   $ genv devices
   ID      ENV ID      ENV NAME        ATTACHED
   0       1573        Yesterday       25 minutes ago
   1       12167       Norwegian Wood  7 hours ago
