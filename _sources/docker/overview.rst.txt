Overview
========

.. contents::
   :depth: 2
   :backlinks: none

Genv Container Toolkit
----------------------
The Genv container toolkit is the integration of Genv with containers and tools like :code:`docker`.
It brings GPU environment capabilities to containers such as :ref:`GPU memory capacity <Configure the GPU Memory Capacity>` (i.e. GPU fractions), :doc:`enforcement <../usage/enforcement>`, :doc:`monitoring <../usage/monitoring>` and more.

.. _Container Toolkit Architecture:

Architecture
------------
The container toolkit consists of two main components: a container runtime (i.e. :code:`genv-container-runtime.py`, :code:`genv-container-runtime-hook.py`) and a wrapper for :code:`docker` commands (i.e. :code:`genv-docker`).

Where to Go Next
----------------
If you are not familiar with Genv, it is recommended to go over the :doc:`overview <../overview/overview>` and follow the :doc:`quick start tutorial <../overview/quickstart>` before starting with containers.

To install the container toolkit on your machine, visit the :doc:`installation page <installation>`.

Then, follow the :doc:`quick start tutorial <quickstart>`, and if you want to know how to do specific things, check out the :doc:`usage guide <usage>`.
