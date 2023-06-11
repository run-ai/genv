Installation
============

.. contents::
   :depth: 2
   :backlinks: none

.. note::

    Most of the installation steps require high permissions so you will probably need to run them with :code:`sudo`.

Install the container toolkit
-----------------------------
To use the Genv container toolkit, Genv needs be installed first as root :ref:`using <Install Using pip>` :code:`pip` with the following command:

.. code-block:: shell

   sudo pip install genv

.. note::

    This is because the container runtime, which is implemented in Python and imports Genv (i.e. :code:`import genv`) runs as root.

The :ref:`container toolkit <Container Toolkit Architecture>` is part of the Genv project `repository <https://github.com/run-ai/genv/tree/main/genv-docker>`__.

You will need to clone the project repository.
Your home repository is a great place to keep it:

.. code-block:: shell

    git clone https://github.com/run-ai/genv.git $HOME/genv

Then, you can then see the container toolkit components with the following command:

.. code-block:: shell

    ls -la $HOME/genv/genv-docker

Register the container runtime
------------------------------
Then, you will need to `register <https://docs.docker.com/engine/reference/commandline/dockerd/#docker-runtime-execution-options>`__ the Genv container runtime in the Docker daemon `configuration <https://docs.docker.com/config/daemon/>`__ file :code:`/etc/docker/daemon.json`.

Edit the file manually
~~~~~~~~~~~~~~~~~~~~~~
You can edit the Docker daemon configuration file :code:`/etc/docker/daemon.json` manually and add the Genv container runtime under :code:`runtimes`.
You should create the file if it does not exist.

Here is an example of the file:

.. code-block:: shell

    {
        "runtimes": {
            "genv": {
                "path": "/home/raz/genv/genv-docker/genv-container-runtime.py"
            }
        }
    }

.. note::

    You should use full absolute paths and avoid using environment variables like :code:`$HOME` because the path will be evaluated in a root context.

Then, restart the Docker daemon for the changes to take effect:

.. code-block:: shell

    systemctl restart docker

Pass as argument to :code:`dockerd`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can use the :code:`dockerd` argument :code:`--add-runtime` instead.

Here is an example:

.. code-block:: shell

    dockerd --add-runtime genv=$HOME/genv/genv-docker/genv-container-runtime.py

Install the :code:`docker` wrapper
----------------------------------
The best way to run Genv containers is with the :code:`docker` wrapper :code:`genv-docker`.

It is recommended to install it in a system-wide location such as :code:`/usr/local/bin`.
You can do this with the following command:

.. code-block:: shell

    cp -f $HOME/genv/genv-docker/genv-docker.sh /usr/local/bin/genv-docker

Now, you will be able to execute :code:`genv-docker` commands from any directory.

If you don't want to install :code:`genv-docker` in a system-wide location or don't have sufficient permissions, you can install it at :code:`$HOME/.local/bin`, or run it using its full path.

Verify installation
-------------------
You can verify the installation with the following command:

.. code-block:: shell

    genv-docker run --rm ubuntu env | grep GENV_

You should then see that the environment variable :code:`GENV_ENVIRONMENT_ID` is set.
