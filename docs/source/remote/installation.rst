.. _Remote Installation:

Installation
============

.. contents::
   :depth: 2
   :backlinks: none

.. _Remote Installation Overview:

Overview
--------
Remote features in Genv are based on running :code:`genv` commands on remote hosts over SSH.
This means that Genv should be installed on all local and remote hosts, and that all local hosts should have SSH access to all remote hosts.

Genv uses commands similar to :code:`ssh <host>` for remote execution.
Therefore, authentication must not be interactive using passwords so that the :code:`ssh` commands Genv uses would work without additional arguments.

You can follow `this <https://superuser.com/a/8110>`__ to set up your SSH so you don't have to type passwords.
It is recommended to use SSH keys.
The identity file and login user should be configured in the SSH configuration file at :code:`~/.ssh/config`.

Some of Genv remote features like :doc:`monitoring <./monitoring>` and :doc:`enforcement <./enforcement>` require privileges and use commands similar to :code:`ssh <host> sudo`.
Therefore, system administrators that want to use these features need to have passwordless :code:`sudo` permissions on all remote machines.

Genv also sends environment variables over SSH by passing :code:`-o SendEnv` to the :code:`ssh` command.
Those environment variables must be explicitly accepted on all remote hosts by :ref:`configuring <SSH Daemon Configuration>` the SSH daemon on the remote hosts.

Local Hosts
-----------
On local hosts, Genv should be :doc:`installed <../overview/installation>` so you could run :code:`genv remote` commands.

Then, make sure you have SSH access to all remote hosts and that the SSH configuration is set properly.
You can verify that using a command similar to this:

.. code-block:: shell

   ssh <host> nvidia-smi

.. note::

   If you want to use privileged capabilities like :doc:`monitoring <./monitoring>` and :doc:`enforcement <./enforcement>` you can verify that :code:`ssh <host> sudo nvidia-smi` works.

.. warning::

   It is important that you verify the SSH access.
   If you can't access any of the remote hosts using a command similar to the one above, :code:`genv remote` commands will not work properly.

Remote Hosts
------------
On remote hosts, Genv must be installed :ref:`system-wide <Install System Wide>`.

You can verify the setup by running a command similar to this from your local machine:

.. code-block:: shell

   $ ssh <host> sudo genv -h
   usage: genv [-h] SUBCOMMAND ...
   ...

.. _SSH Daemon Configuration:

SSH Daemon Configuration
~~~~~~~~~~~~~~~~~~~~~~~~
Afterward, it is required to edit the configuration of the SSH daemon.

Genv uses SSH for communication, and relies on sending environment variables from local hosts to remote hosts by passing :code:`-o SendEnv` to the :code:`ssh` command.

Those environment variables must be explicitly accepted on all remote hosts by modifying the SSH daemon configuration file.

First, add :code:`GENV_*` to field :code:`AcceptEnv` in :code:`/etc/ssh/sshd_config`.
You can do this with the following command (you will probably need to use :code:`sudo` here):

.. code-block:: shell

   sed -i "/^AcceptEnv/s/$/ GENV_*/" /etc/ssh/sshd_config

You can verify that it worked using the command:

.. code-block:: shell

   grep GENV /etc/ssh/sshd_config

Then, restart the SSH daemon using the following command (you will probably need to use :code:`sudo` here as well):

.. code-block:: shell

   systemctl restart ssh

You can then test that everything is set up properly by running the following command from a local host:

.. code-block:: shell

   GENV_TEST="ilovegpus" ssh -o SendEnv=GENV_TEST <host> env | grep GENV
