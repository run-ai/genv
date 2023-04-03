Monitoring
==========

.. contents::
   :depth: 3
   :backlinks: none

Overview
--------
Before starting with remote monitoring features, it is highly recommended to go over the local monitoring features guide which is available :doc:`here <../usage/monitoring>`.

Genv :doc:`remote features <overview>` allow users and system administrators to provision GPU resources accross multiple machines.

Genv remote monitoring features allow users and system administrators to monitor the resources and usage accross multiple machines using the command :code:`genv remote monitor`.

.. figure:: monitoring-overview.png

   Genv remote monitoring overview

Quick start
-----------
This is a guide to get started with remote monitoring features in Genv.

Prerequisites
~~~~~~~~~~~~~
First, you will need to :doc:`install <installation>` Genv on your local machine and one or more remote hosts.

In my case, I have two remote machines: :code:`gpu-server-1` and :code:`gpu-server-2`.

Then, you will need to install the :code:`prometheus-client` `PyPI package <https://pypi.org/project/prometheus-client>`__ on your local machine:

.. code-block:: shell

   pip install prometheus-client

Running the monitoring service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Now, start the monitoring service using the following command:

.. code-block:: shell

   genv remote -H gpu-server-1,gpu-server-2 monitor

.. note::

   :code:`genv remote monitor` acts as a foreground daemon and runs until a :code:`Ctrl+C` is received.
   Therefore, you will need to keep the terminal running while monitoring the system.

Prometheus
~~~~~~~~~~
The Prometheus instructions are similar to the local monitoring instructions.
Follow them :ref:`here <Monitoring Prometheus>`.

Now, you can open your browser at http://localhost:9090 and access Genv metrics from all remote hosts.

Grafana
~~~~~~~
The Grafana instructions are similar to the local monitoring instructions.
Follow them :ref:`here <Monitoring Grafana>`.

Now, you can open your browser at http://localhost:3000 and see the Genv dashboard with metrics from all remote hosts.

Reference
---------
The Genv remote monitoring service exports the same metrics as the local monitoring service with the additional label :code:`hostname`.

You can check out all the available metrics :ref:`here <Metrics Reference>`.
