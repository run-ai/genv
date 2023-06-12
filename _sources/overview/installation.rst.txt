Installation
============

.. contents::
   :depth: 3
   :backlinks: none

.. note::

   This page talks about installing Genv on a single machine.
   If you are interested in using Genv on a multi-machine cluster, check out the remote installation :doc:`guide <../remote/installation>`.

.. _Install Using pip:

Using :code:`pip`
-----------------
.. warning::

   If you installed Genv previously (versions <= 0.12.0), you will need to manually :ref:`remove the old version <Remove Old Version>` first.

Genv is available on `PyPI <https://pypi.org/project/genv/>`__ and is available for installation using :code:`pip`.

If you want to use :doc:`enforcement <../usage/enforcement>` capabilities or you are installing on a remote worker machine, you will need to be able to run :code:`genv` commands with :code:`sudo`.
Therefore, you will need to install Genv as root by adding :code:`sudo` to the :code:`pip install` commands.

Generally speaking, you should install Genv as a user if you are a user, and as root if you are a system administrator.

.. note::

   If you want to run as root but can't *install* using :code:`sudo pip install` for some reason, check out the workaround described :ref:`here <Install Without sudo>`.

Install Genv with the following command:

.. code-block:: shell

   pip install genv

.. note::

   As described above, run :code:`sudo pip install genv` if you want to install Genv as root.

If you want monitoring capabilities, you can use the following command to install relevant dependencies as well:

.. code-block:: shell

   pip install genv[monitor]

.. warning::

   If you see a warning message similar to the following, add the specified directory to your :code:`$PATH` by editing your :code:`~/.bashrc` and restarting your shell:

   .. code-block:: shell

      WARNING: The script genv is installed in '/home/raz/.local/bin' which is not on PATH.
      Consider adding this directory to PATH...

You can verify the installation with the command:

.. code-block:: shell

   genv --help

If you see :code:`genv: command not found`, then your :code:`$PATH` is probably no set as explained above.

.. _Set Up Terminal:

Set Up Terminal
~~~~~~~~~~~~~~~
To use the terminal integration of Genv, add the following command to your :code:`~/.bashrc` or any other equivalent file:

.. code-block:: shell

   eval "$(genv shell --init)"

.. _Install Using Conda:

Using Conda
-----------
If you are using `Conda <https://docs.conda.io/en/latest/>`__, you can install the :code:`genv` `package <https://anaconda.org/conda-forge/genv>`__ from the channel `conda-forge <https://conda-forge.org/>`__:

.. code-block:: shell

   conda install -c conda-forge genv

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

.. _Remove Old Version:

Remove Old Version
------------------
If you installed Genv previously (versions <= 0.12.0) and *not* from Conda, you will need to manually remove the old version first.

You can check it by running the following command:

.. code-block:: shell

   genv root >& /dev/null && echo old version installed

If you see :code:`old version installed`, you have an old version installed and you need to remove it.

First, remove the commands you added to your :code:`~/.bashrc` or any other equivalent file.
They should look like this:

.. code-block:: shell

   export PATH=$HOME/genv/bin:$PATH
   eval "$(genv init -)"

Afterward, remove the previous installation directory with the following command:

.. code-block:: shell

   rm -rf $(genv root)

Then, restart your terminal.
