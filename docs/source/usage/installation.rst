Installation
============

.. contents::
   :depth: 2
   :backlinks: none

Terminal
--------

From Source
^^^^^^^^^^^
It's super easy to get genv as everything you need is to clone its `repository <https://www.github.com/run-ai/genv>`__.
Your home directory is a great place to keep it:

.. code-block:: shell

   git clone https://github.com/run-ai/genv.git ~/genv

^^^^^^^^^^^^^^^^^^^^^
Setting Up Your Shell
^^^^^^^^^^^^^^^^^^^^^
In order to use genv you need to set up your shell environment with the following commands:

.. code-block:: shell

   export PATH=$HOME/genv/bin:$PATH
   eval "$(genv init -)"

You should add them to your :code:`~/.bashrc` or any other equivalent file.

Afterward, for this to take effect, either reopen your terminal or restart your shell using the command:

.. code-block:: shell

   exec $SHELL

To verify the installation worked, run the following command:

.. code-block:: shell

   genv

You should be able to see all the available genv commands.

^^^^^^^^^^^^
Dependencies
^^^^^^^^^^^^
genv uses Python 3 so make sure you have it also installed.

^^^^^^^^^^^^
Uninstalling
^^^^^^^^^^^^
To uninstall genv simply remove the genv directory:

.. code-block:: shell

   rm -rf $(genv root)

You will also need to remove the commands you added to your :code:`~/.bashrc` or any other equivalent file.

Visual Studio Code
------------------
Installation is done from the `Visual Studio Marketplace <https://marketplace.visualstudio.com/items?itemName=run-ai.vscode-genv>`__.

For more information please refer to the project `repository <https://github.com/run-ai/vscode-genv>`__.

JupyterLab
----------
Installation is documented `here <https://github.com/run-ai/jupyterlab_genv#installation>`__.

For more information please refer to the project `repository <https://github.com/run-ai/jupyterlab_genv>`__.

PyCharm
-------
Currently, there is no PyCharm plugin for genv.
This is however part of the project roadmap.

In case you use PyCharm, please open an `issue <https://github.com/run-ai/genv/issues>`__ in the project repository.

This will help us prioritize this as well as suggest other ways to work with genv in PyCharm in the meantime.
