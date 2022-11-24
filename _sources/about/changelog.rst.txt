Changelog
=========

Version 0.2.0
-------------
**Date:** November 3, 2022

Added
~~~~~
* :code:`nvidia-smi` shim shows environment information only (i.e. memory, processes)
* :code:`docker` shim that exposes containers to devices attached to the environment
* Environment variable :code:`GENV_BYPASS` bypasses shims

Changed
~~~~~~~
* :code:`nvidia-smi` shim converted from Bash script to Python

Version 0.1.0
-------------
**Date:** September 22, 2022

Added
~~~~~
* Activating and deactivating environment
* Querying environment status
* Configuring environment name and device count
* Clearing and printing environment configuration
* Saving and loading environment configuration to and from disk
* Attaching environment to devices and detaching from them
* Listing active environments
* Listing devices
* :code:`nvidia-smi` shim that shows information about attached devices only
