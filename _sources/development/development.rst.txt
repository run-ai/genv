Development
===========

.. contents::
   :depth: 3
   :backlinks: none

Prerequisites
-------------

Start by cloning the project `repository <https://www.github.com/run-ai/genv>`__:

.. code-block:: shell

    git clone https://github.com/run-ai/genv.git

Setup
-----

Local
~~~~~
Open a terminal in the project directory.

.. warning::

   We support :code:`bash` terminals only at the moment. Query your shell using :code:`echo $SHELL` and run :code:`bash` if it is not your shell, or use a :ref:`Docker <Docker>` setup instead.

Install the Python package in editable mode with the following command:

.. code-block:: shell

    pip install -e .

Then run the following commands to configure your terminal:

.. code-block:: shell

    eval "$(genv shell --init)"

You can test it by running:

.. code-block:: shell

    $ genv
    usage: genv [-h] SUBCOMMAND ...

    Query and control Genv on this machine or in a cluster
    ...

To uninstall the package, use the following command:

.. code-block:: shell

    pip uninstall -y genv

.. _Docker:

Docker
~~~~~~
You can also use a container for the development.
This is useful if you are using macOS as Genv is developed for Linux systems and some things are not available in macOS (e.g. :code:`/proc` filesystem).

First, build the Docker image :code:`genv:devel` with the following command:

.. code-block:: shell

    docker build -t genv:devel -f devel/Dockerfile devel

Now, run a development container using the following command from the root directory of the project:

.. code-block:: shell

    docker run -it --rm --name genv \
        -v $PWD:/root/genv \
        -w /root/genv \
        genv:devel

.. TODO(raz): document how to use real GPUs

.. note::

    Pass :code:`-v /var/tmp:/var/tmp --pid host` if you want to share the state with the host machine or with other containers and :code:`-v $HOME/.ssh:/root/.ssh` if you want to use remote features as well.

To open another terminal inside the container use:

.. code-block:: shell

    docker exec -it genv bash

CPU-Only Setup
~~~~~~~~~~~~~~
Some Genv features rely on executing :code:`nvidia-smi` commands.
Those commands will not work if you are developing on a machine without GPUs.

Here is what you will probably see if you will try running :code:`nvidia-smi`:

.. code-block:: shell

    $ nvidia-smi
    bash: nvidia-smi: command not found

In such cases, it is recommended to use the mock shim of :code:`nvidia-smi`.
Set up your shell with the following command:

.. code-block:: shell

    export PATH=$PATH:$PWD/devel/shims

.. note::

    If you are using a :ref:`Docker <Docker>` development setup, your shell should already be set.

Now, execute :code:`nvidia-smi` once again.
This time it should work and you should see an :code:`nvidia-smi`-like output printed to the screen.

.. _Mock Devices:

~~~~~~~~~~~~
Mock Devices
~~~~~~~~~~~~
You can control the mock devices by executing a command similar to the following and specifying the supported :code:`GENV_MOCK_*` :ref:`environment variables <Environment Variables>`:

.. code-block:: shell

    GENV_MOCK_DEVICE_COUNT=4 GENV_MOCK_DEVICE_TOTAL_MEMORY=8g genv devices --reset

~~~~~~~~~~~~~~~
Remote Features
~~~~~~~~~~~~~~~
If you are working on :doc:`remote features <../remote/overview>`, you might want to test them on a few remote machines.

However, many times you will not have as many GPU machines as you would like, or SSH access to them.
You might also want to work on remote features using only your single CPU machine.

For this case, you can use the :code:`genv:sshd` Docker image that acts as a remote machine over SSH.

First, build the :ref:`Docker image <Docker>` :code:`genv:devel` as it is the base image of :code:`genv:sshd` and then build the Docker image :code:`genv:sshd` with the following command:

.. code-block:: shell

    docker build -t genv:sshd -f devel/sshd.Dockerfile devel

Now, run a container using the following command from the root directory of the project:

.. code-block:: shell

    docker run -d --rm \
        --name genv-server-1 \
        -p 2221:22 \
        -v $PWD:/root/genv \
        genv:sshd

.. TODO(raz): document how to use real GPUs

This command runs a container in the background that is named :code:`genv-server-1` and accepts SSH connections on port 2221.

You can rerun this command as many times as you want to simulate more remote machines.
Make sure to change the host port each time and also rename the container (or have the container unnamed by omitting the flag :code:`--name` entirely).

You can open a terminal in such a container using a command similar to the following:

.. code-block:: shell

    docker exec -it genv-server-1 bash

To terminate such a container, use a command similar to the following:

.. code-block:: shell

    docker kill genv-server-1

Then, because of how remote features :doc:`work <../remote/installation>`, you will have to edit the SSH configuration on the host machine to allow simple SSH commands that :code:`genv remote` uses.

Edit the SSH configuration file by running the following command on the host machine:

.. code-block:: shell

    vim ~/.ssh/config

Add the following configuration for each of the containers.
Make sure to set the correct port for every container:

.. code-block:: shell

    Host genv-server-1
        Port 2221
        Hostname 127.0.0.1
        User root

Then, test the SSH connectivity using the command:

.. code-block:: shell

    ssh genv-server-1

.. warning::

    You might need to approve the SSH key of the container on the first time.
    Type :code:`yes` if you see a message similar to :code:`Are you sure you want to continue connecting (yes/no)?`.

.. note::

    You can also control the mock devices by running over SSH what is described :ref:`here <Mock Devices>`.

After setting up all containers, test your setup with a command similar to the following:

.. code-block:: shell

    genv remote -H genv-server-1,genv-server-2 devices

Docs
----

Setup
~~~~~
.. code-block:: shell

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install sphinx
    python -m pip install -r docs/requirements.txt

.. note::

    You might need to use :code:`python3` instead of :code:`python`

Build
~~~~~
.. code-block:: shell

    make -C docs/ html

Python Package
--------------

Build
~~~~~
.. code-block:: shell

    python setup.py sdist bdist_wheel

.. note::

    You might need to upgrade :code:`wheel` using :code:`pip install wheel==0.31.0`

Publish to PyPI
~~~~~~~~~~~~~~~
.. code-block:: shell

    python -m twine upload dist/*

.. note::

    You might need to :code:`pip install twine`
