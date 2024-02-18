Installation
============

.. contents::
   :depth: 3
   :backlinks: none

.. note::

   This page talks about installing Genv on a single machine.
   If you are interested in using Genv on a multi-machine cluster, check out the remote installation :doc:`guide <../remote/installation>`.

.. warning::

   If you installed Genv previously (versions <= 0.12.0), you will need to manually :ref:`remove the old version <Remove Old Version>` first.

.. _Install System Wide:

System Administrators
---------------------

Install Genv from `PyPI <https://pypi.org/project/genv/>`__ using :code:`sudo` with the following command:

.. code-block:: shell

   sudo pip install genv[admin]

.. note::

   Using :code:`sudo` ensures the installation is system wide so that all users on the machine and in the cluster can use Genv and that administrators will be able to use privileged Genv capabilities such as :doc:`monitoring <../usage/monitoring>` and :doc:`enforcing <../usage/enforcement>`.

Users will also need their shells to be initialized in order to use the terminal integration of Genv and commands like :code:`genv activate`.
Use the following command to set up their shells:

.. code-block:: shell

   sudo tee /etc/profile.d/genv.sh > /dev/null << EOF
   if command -v genv &> /dev/null
   then
      eval "\$(genv shell --init)"
   fi
   EOF

.. note::

   You can verify the installation with the command:

   .. code-block:: shell

      $ genv --help
      usage: genv [-h] SUBCOMMAND ...

Users
-----

If you do not have administrative permissions and can't install system-wide using :code:`sudo`, you can install Genv for your user using :code:`pip` and :code:`conda` depending on your environment..

.. warning::

   However, this method limits accessibility to other users on the machine or in the cluster and does not provide access to privileged capabilities such as :doc:`monitoring <../usage/monitoring>` and :doc:`enforcing <../usage/enforcement>`.

.. _Install Using pip:

Using :code:`pip`
~~~~~~~~~~~~~~~~~

Genv is available on `PyPI <https://pypi.org/project/genv/>`__ and is available for installation using :code:`pip` with the following command:

.. code-block:: shell

   pip install genv

.. warning::

   If you see a warning message similar to the following, add the specified directory to your :code:`$PATH` by editing your :code:`~/.bashrc` and restarting your shell:

   .. code-block:: shell

      WARNING: The script genv is installed in '$HOME/.local/bin' which is not on PATH.
      Consider adding this directory to PATH...

.. _Set Up Terminal:

To use the terminal integration of Genv and commands like :code:`genv activate`, add the following command to your :code:`~/.bashrc` or any other equivalent file:

.. code-block:: shell

   eval "$(genv shell --init)"

.. note::

   You can verify the installation with the command:

   .. code-block:: shell

      $ genv --help
      usage: genv [-h] SUBCOMMAND ...

   If you see :code:`genv: command not found` then your :code:`$PATH` is probably no set as explained above.

.. _Install Using Conda:

Using Conda
~~~~~~~~~~~
If you are using `Conda <https://docs.conda.io/en/latest/>`__, you can install the :code:`genv` `package <https://anaconda.org/conda-forge/genv>`__ from the channel `conda-forge <https://conda-forge.org/>`__:

.. code-block:: shell

   conda install -c conda-forge genv

.. _Integrations:

Integrations
------------

Visual Studio Code
~~~~~~~~~~~~~~~~~~
Installation is done from the `Visual Studio Marketplace <https://marketplace.visualstudio.com/items?itemName=run-ai.vscode-genv>`__.

For more information please refer to the project `repository <https://github.com/run-ai/vscode-genv>`__.

JupyterLab
~~~~~~~~~~
Installation is documented `here <https://github.com/run-ai/jupyterlab_genv#installation>`__.

For more information please refer to the project `repository <https://github.com/run-ai/jupyterlab_genv>`__.

PyCharm
~~~~~~~
Currently, there is no PyCharm plugin for Genv.
This is however part of the project roadmap.

In case you use PyCharm, please open an `issue <https://github.com/run-ai/genv/issues>`__ in the project repository.

This will help us prioritize this as well as suggest other ways to work with Genv in PyCharm in the meantime.

Docker
~~~~~~
To install the :code:`genv-docker` refer to the Genv container toolkit :doc:`installation <../docker/installation>` page.

Ray
~~~
To install the Ray integration of Genv read :ref:`here <Using Ray>`.

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
