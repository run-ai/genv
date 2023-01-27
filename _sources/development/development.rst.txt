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

Then run the following commands to configure your terminal:

.. code-block:: shell

   export PATH=$PWD/bin:$PATH
   eval "$(genv init -)"

You can test it by running:

.. code-block:: shell

   genv

.. _Docker:

Docker
~~~~~~
You can also use a container for the development.
This is useful if you are using macOS as Genv is developed for Linux systems and some things are not available in macOS (e.g. :code:`/proc` filesystem).

Use the following command:

.. code-block:: shell

    docker run -it --rm --name genv \
        -v $PWD:/genv \
        -v /var/tmp:/var/tmp \
        -w /genv \
        python \
        bash --rcfile /genv/devel/.bashrc

.. note::

    You can pass :code:`-v $HOME/.ssh:/root/.ssh` if you want to use remote features as well

To open another terminal inside the container use:

.. code-block:: shell

    docker exec -it genv bash --rcfile /genv/devel/.bashrc

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

    export PATH=$PWD/devel/shims:$PATH

Now, execute :code:`nvidia-smi` once again.
This time it should work and you should see an :code:`nvidia-smi`-like output printed to the screen.

Also, you will need to manually initialize :code:`devices.json` with a made up device count using the environment variable :code:`GENV_MOCK_DEVICE_COUNT`.
Run the following command and can configure how many GPUs you want to have:

.. code-block:: shell

    GENV_MOCK_DEVICE_COUNT=4 genv devices

.. note::

    You can also control the amount of GPU memory with the environment variable :code:`GENV_MOCK_DEVICE_MEMORY`

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
