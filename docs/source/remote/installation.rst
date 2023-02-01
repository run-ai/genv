.. _Remote Installation:

Installation
============

.. contents::
   :depth: 2
   :backlinks: none

Overview
--------
Remote features in Genv are based on running :code:`genv` commands on remote hosts over SSH.
This means that Genv should be installed on all local and remote hosts, and that all local hosts should have SSH access to all remote hosts.

Genv uses commands similar to :code:`ssh <host>` for remote execution.
Therefore, authentication must not be interactive using passwords for example.
It is recommended to use SSH keys for authentication.

The identity file and login user should be configured in the SSH configuration file at :code:`~/.ssh/config` so that the :code:`ssh` commands Genv uses would work without additional arguments.

Genv :ref:`remote enforcement features <Remote Enforcement>` use commands similar to :code:`ssh <host> sudo` for querying the environment variables of processes or terminating processes.
Therefore, Linux users that want to use these features need to have passwordless :code:`sudo` permissions on all remote machines.

Genv also sends environment variables over SSH by passing :code:`-o SendEnv` to the :code:`ssh` command.
Those environment variables must be explicitly accepted on all remote hosts by modifying the SSH daemon configuration file.

Local Hosts
-----------
On local hosts, :ref:`install <Install in Terminal>` the terminal component of Genv in your preferred way if not already installed.
This is how you will run :code:`genv remote` commands.

Then, make sure you have SSH access to all remote hosts and that the SSH configuration is set properly.
You can verify that using commands similar to this:

.. code-block:: shell

   ssh <host>

.. warning::

   It is important that you verify the SSH access.
   If you can't access any of the remote hosts using a command similar to the one above, :code:`genv remote` commands will not work properly.

Remote Hosts
------------
On remote hosts, the terminal component of Genv should also be installed.
However, the installation directory on each of the remote hosts should be known and accessible to all users that will run :code:`genv remote` commands on local hosts.

There are two main ways to install Genv on remote hosts: :ref:`per-user <Per-User Installation>` and :ref:`system-wide <System-Wide Installation>` installations, which we will get to in a second.

SSH Daemon Configuration
~~~~~~~~~~~~~~~~~~~~~~~~
Regardless of the installation method of Genv on remote hosts, it is required to edit the configuration of the SSH daemon.

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

.. _Per-User Installation:

Per-User Installation (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Every user should install Genv :ref:`from source <Install in Terminal From Source>` in his or her home directory (i.e. :code:`$HOME/genv`) on all remote hosts.

This is the recommended way to install Genv on remote hosts for a few reasons:

#. All :code:`genv remote` commands assume Genv is installed at :code:`$HOME/genv` by default.
#. Some :code:`genv remote` commands like :code:`activate` expect :code:`genv` commands to work in the SSH session.

.. _System-Wide Installation:

System-Wide Installation
~~~~~~~~~~~~~~~~~~~~~~~~
It is also possible to install Genv from source in a system-wide location such as :code:`/opt/genv` on all remote hosts.

This could be done with the following command:

.. code-block:: shell

   git clone https://github.com/run-ai/genv.git /opt/genv

Note that when using system installation, users will need to specify the installation location by passing the argument :code:`--root` to :code:`genv remote` commands.

Also, if Genv is not installed in the :ref:`login script <Setting Up Your Shell>` of a user on a remote host, some :code:`genv remote` commands like :code:`activate` will not work because the SSH shell will not be properly set up.

.. note::

   It is recommended to install Genv on all remote hosts in the same way.
