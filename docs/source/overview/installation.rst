Installation
============

.. contents::
   :depth: 3
   :backlinks: none

.. note::

   This page talks about installing Genv on a single machine.
   If you are interested in using Genv on a multi-machine cluster, check out the remote installation :doc:`guide <../remote/installation>`.

.. _Install Core:

Core
----

The core components of Genv are part of the Genv `Python package <https://pypi.org/project/genv/>`__.
Install it with the following command:

.. code-block:: shell

   pip install genv

.. warning::

   If you see a warning message similar to the following, add the specified directory to your :code:`$PATH` by editing your :code:`~/.bashrc` and restarting your shell:

   .. code-block:: shell

      WARNING: The script genvctl is installed in '/home/raz/.local/bin' which is not on PATH.
      Consider adding this directory to PATH...

.. note::

   Genv needs Python 3.7 or higher so make sure you have it installed.

The Python package should also install the Genv control CLI and SDK CLI.
Verify the installation with the command:

.. code-block:: shell

   genvctl --help

.. warning::

   If you see :code:`genvctl: command not found`, your :code:`$PATH` is probably no set as explained above.

.. _Install Terminal:

Terminal
--------
To use Genv in your shell, you will need to install the terminal components of Genv.

.. note::

   Before installing the terminal components, make sure you have the :ref:`core <Install Core>` components of Genv installed.

You can install the terminal components of Genv in several ways.

Conda
~~~~~
If you are using `Conda <https://docs.conda.io/en/latest/>`__, you can install the :code:`genv` `package <https://anaconda.org/conda-forge/genv>`__ from the channel `conda-forge <https://conda-forge.org/>`__:

.. code-block:: shell

   conda install -c conda-forge genv

.. _Install Terminal From Source:

From Source
~~~~~~~~~~~
If you are not using Conda, you can clone the Genv `repository <https://www.github.com/run-ai/genv>`__ to your home directory:

.. code-block:: shell

   git clone https://github.com/run-ai/genv.git $HOME/genv

Then, you will need to set up your shell by adding the following commands to your :code:`~/.bashrc` or any other equivalent file:

.. code-block:: shell

   export PATH=$HOME/genv/bin:$PATH
   eval "$(genv init -)"

Afterward, for this to take effect, either reopen your terminal or restart your shell using the command:

.. code-block:: shell

   exec $SHELL

To verify the installation, run the following command:

.. code-block:: shell

   genv

You should be able to see all the available Genv commands.

~~~~~~~~~~~~
Uninstalling
~~~~~~~~~~~~
To uninstall the terminal components of Genv, remove the commands you added to your :code:`~/.bashrc` or any other equivalent file.

Then, remove its root directory:

.. code-block:: shell

   rm -rf $(genv root)

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
Currently, there is no PyCharm plugin for Genv.
This is however part of the project roadmap.

In case you use PyCharm, please open an `issue <https://github.com/run-ai/genv/issues>`__ in the project repository.

This will help us prioritize this as well as suggest other ways to work with Genv in PyCharm in the meantime.

Docker
------
To install the :code:`genv-docker` refer to the Genv container toolkit :doc:`installation <../docker/installation>` page.
