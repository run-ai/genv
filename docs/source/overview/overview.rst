Overview
========

.. contents::
   :depth: 2
   :backlinks: none

What is Genv
------------
.. note::

   You can jump directly to the quick start toturial :doc:`here <quickstart>`.

Genv is an open-source project that brings environment management to GPUs.

If you are not familiar with the concept of environments, you can check out the documentation of projects like `venv <https://docs.python.org/3/library/venv.html>`__, `pyenv <https://github.com/pyenv/pyenv>`__ and `Conda <https://docs.conda.io/projects/conda/en/stable/>`__ as a reference.

At its core, Genv is a `Python package <https://pypi.org/project/genv>`__ that manages GPUs and keeps its state as :ref:`files <Files>`.

On top of this core layer, Genv has :doc:`integrations <../usage/installation>` with many common tools and environments such as terminal, Visual Studio Code, JupyterLab and PyCharm.

.. figure:: overview.png

   GPU environments with Genv

Architectures
-------------
Genv supports two main architectures: local and :doc:`remote <../remote/overview>`.

Local
~~~~~
.. figure:: architecture-local.png

   Genv local architecture

When running in local mode, Genv manages the GPUs on the local machine where Genv is running.
This is mostly relevant for the case of a single user with GPUs in his or her machine, or the case of multiple users that share a single GPU machine.

Remote
~~~~~~
.. figure:: architecture-remote.png

   Genv remote architecture

When running in remote mode, Genv manages the GPUs on one or more remote machines over SSH.
This is mostly relevant for the case when multiple users share multiple GPU machines.

For more information, see :doc:`here <../remote/overview>`.

Where to Go Next
----------------
If you are not familiar with Genv, it is recommended to follow the :doc:`quick start tutorial <quickstart>`.

If you are looking for how to install Genv, visit the :doc:`installation page <../usage/installation>`, and if you want to know how to do specific things, check out the :doc:`usage guide <../usage/usage>`.
