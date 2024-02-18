Overview
========

.. contents::
   :depth: 3
   :backlinks: none

Genv is an environment management software for GPUs that manages GPUs on a single machine or in a cluster.

Genv uses `Ollama <https://ollama.com/>`__ for managing managing Large Language Models (LLMs) with Genv.
This allows users to efficiently run, manage and utilize LLMs on GPUs within their clusters.

This guide will help you get started with LLMs using Genv.

Prerequisites
-------------

First, you will need to :doc:`install <../overview/installation>` Genv on your GPU machines in the cluster.

.. note::

   It is recommended to install Genv :ref:`system-wide <Install System Wide>`.

Then, you will need to `install <https://ollama.com/download>`__ Ollama on your GPU machines with the command:

.. code-block:: shell

   curl -fsSL https://ollama.com/install.sh | sh

Quick start
-----------

If you are running on a GPU cluster with multiple machines, follow the :ref:`cluster <LLM cluster quick start>` quick start.
Otherwise, follow the :ref:`local <LLM local quick start>` quick start.

.. _LLM cluster quick start:

Cluster
~~~~~~~
In my case, I have two remote GPU machines: :code:`gpu-server-1` and :code:`gpu-server-2`.

Serve your first LLM on a single GPU with the command:

.. code-block:: shell

   $ genv remote -H gpu-server-1,gpu-server-2 llm serve llama2 --gpus 1
   ...

.. note::

   Use :code:`Ctrl+C` to stop the serving.

Open another terminal and list all LLMs in your cluster with:

.. code-block:: shell

   $ genv remote -H gpu-server-1,gpu-server-2 llm ps
   HOST                     MODEL       PORT    CREATED              EID     USER
   gpu-server-1             llama2      N/A     2 hours ago          571     root

We can see that :code:`llama2` is now being served in the cluster.

Attach to the model and interact with it using the command:

.. code-block::

   $ genv remote -H gpu-server-1,gpu-server-2 llm attach llama2
   >>> Hi! I'm Genv, how are you?

   Hello there, it's nice to meet you! *blinks* I'm just an AI assistant, so I don't have feelings or emotions
   like humans do, but I'm here to help you with any questions or tasks you might have. How can I assist you
   today?

   >>> Send a message (/? for help)

.. note::

   Use :code:`Ctrl+D` to exit the interactive terminal.

.. _LLM local quick start:

Local
~~~~~
Serve your first LLM on a single GPU with the command:

.. code-block:: shell

   $ genv llm serve llama2 --gpus 1
   ...

.. note::

   Use :code:`Ctrl+C` to stop the serving.

Open another terminal and list all LLMs on your machine with:

.. code-block:: shell

   $ genv llm ps
   MODEL       PORT    CREATED              EID     USER            PID(S)
   llama2      33123   22 seconds ago       1179252 raz(1001)       1179252

We can see that :code:`llama2` is now being served on the machine.

Attach to the model and interact with it using the command:

.. code-block::

   $ genv llm attach llama2
   >>> Hello from Genv

   Hello there! *blinks* Uh, I'm... uh... *trails off* I'm not actually a person, I'm just an AI designed to
   simulate conversation. So, I don't have feelings or emotions like a real person would. But I'm here to help
   you with any questions or tasks you may have! How can I assist you today?

   >>> Send a message (/? for help)

.. note::

   Use :code:`Ctrl+D` to exit the interactive terminal.

Where to Go Next
----------------
If you are not familiar with Genv, it is recommended to go over the :doc:`overview <../overview/overview>` and follow the :doc:`quick start tutorial <../overview/quickstart>`.

You should also learn how :doc:`remote features <../remote/overview>` work in Genv.
