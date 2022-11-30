Development
===========

.. contents::
   :depth: 3
   :backlinks: none

Prerequisites
-------------

All you need is to clone the project `repository <https://www.github.com/run-ai/genv>`__.

Setup
-----

Local
~~~~~
Open a terminal in the project directory.

.. warning::

   We support :code:`bash` and :code:`zsh` terminals only at the moment. Query your shell using :code:`echo $SHELL` and run :code:`bash` if your shell is not supported, or use a :ref:`Docker <Docker>` setup instead.

Then run the following commands to configure your terminal:

.. code-block:: shell

   export PATH=$PWD/bin:$PATH
   eval "$(genv init -)"

You can test it by running:

.. code-block:: shell

   genv

.. note::

   If you are on a CPU machine, mock the amount of GPUs by setting the environment variable :code:`GENV_MOCK_DEVICE_COUNT`

.. _Docker:

Docker
~~~~~~
You can also use a container for the development.
This is useful if you are using macOS as genv is developed for Linux systems and some things are not available in macOS (e.g. :code:`/proc` filesystem).

Use the following command:

.. code-block:: shell

    docker run -it --rm --name genv \
        -v $PWD:/genv \
        -v /var/tmp:/var/tmp \
        python \
        bash --rcfile /genv/.bashrc

To open another terminal inside the container use:

.. code-block:: shell

    docker exec -it genv bash --rcfile /genv/.bashrc

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
