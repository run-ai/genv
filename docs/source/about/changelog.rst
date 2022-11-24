Changelog
=========

Version 0.3.0
-------------
**Date:** November 24, 2022

Added
~~~~~
* Configuring environment GPU memory capacity
* GPU memory aware device provisioning
* Supporting device over allocation with multiple environments
* Documentation site

Changed
~~~~~~~
* :code:`docker` shim injects environment variable :code:`GENV_ENVIRONMENT_ID` to containers
* Renamed environment variable :code:`GENV_DEVICES` to :code:`GENV_MOCK_DEVICE_COUNT`

Fixed
~~~~~
* :code:`nvidia-smi` shim supports environment variables with :code:`=`
* :code:`docker` shim supports the case when argument :code:`--gpus` is not passed
* :code:`nvidia-smi` shim does not pass argument :code:`--id` in bypass mode

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
