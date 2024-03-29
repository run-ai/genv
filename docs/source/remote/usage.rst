Usage
=====

All remote features of Genv are available as a subcommand to the command :code:`genv remote`.

.. contents::
   :depth: 2
   :backlinks: none

List Environments
-----------------
You can list active environments on all remote hosts using the command :code:`envs`.
For example:

.. code-block:: shell

   $ genv remote -H gpu-server-1,gpu-server-1 envs
   HOST               ID      USER            NAME            CREATED
   gpu-server-1       31739   raz(1003)       project-1       42 minutes ago
   gpu-server-2       13811   john(1002)      project-2       2 hours ago

   Total 2 environments on 2 hosts

Device Information
------------------
You can see device information and availability on all remote hosts using the command :code:`devices`.
For example:

.. code-block:: shell

   $ genv remote -H gpu-server-1,gpu-server-1 devices
   HOST                     TOTAL    AVAILABLE
   core-server-1            1        0
   core-server-2            2        1

   Total 3 devices with 1 available on 2 hosts

Activating an Environment
-------------------------
You can activate an environment on a remote host using the command :code:`activate`.

You can also specify GPU resource requirements such as device count.
Genv will then look for a remote host with enough available resources, connect to it with SSH and automatically create and configure an environment there.
For example:

.. code-block:: shell

   $ genv remote -H gpu-server-1,gpu-server-2 activate --gpus 1 --name my-env
   ...
   (genv) gpu-server-2 $

If Genv can't find a remote host with enough available resources, the :code:`genv remote activate` command will fail with the following message:

.. code-block:: shell

   $ genv remote -H gpu-server-1,gpu-server-2 activate --gpus 4
   Cannot find a host with enough available resources

.. note::

   You can see all available resource specification options with the command :code:`genv remote activate --help`

Enforcement
-----------
Genv supports enforcement features on multiple hosts.
Check out :doc:`this <./enforcement>` document for more information.

Monitoring
-----------
Genv supports monitoring features on multiple hosts.
Check out :doc:`this <./monitoring>` document for more information.

Specifying Remote Hosts
-----------------------
:code:`genv remote` commands connect to multiple remote hosts and run :code:`genv` commands on them.
You can specify the remote hosts in two ways: using explicit hostnames or using a hostfile.

You can pass multiple hostnames and IP addresses using a comma-separated string to the argument :code:`-H` or :code:`--host`.
For example:

.. code-block:: shell

   genv remote -H gpu-server-1,gpu-server-2,192.168.1.42 envs

Alternatively, you can create a text file with the hostnames and IP addresses.
For example:

.. code-block:: shell

   $ cat /etc/genv/hostfile
   gpu-server-1
   gpu-server-2
   192.168.1.42

Then you can pass it to the argument :code:`--hostfile`.
For example:

.. code-block:: shell

   genv remote --hostfile /etc/genv/hostfile envs

Specifying User Names
---------------------
It is possible to specify usernames for the SSH connections.

If you are using the same username for all machines pass it as the argument :code:`-l` or :code:`--username`.
For example:

.. code-block:: shell

   genv remote -l root -H gpu-server-1,gpu-server-2,192.168.1.42 envs

If you are using different usernames for different machines you can pass them as part of the hostname.
For example:

.. code-block:: shell

   genv remote -H root@gpu-server-1,user@gpu-server-2,192.168.1.42 envs

.. note::

   You can use the :code:`user@hostname` syntax in hostfiles as well.
