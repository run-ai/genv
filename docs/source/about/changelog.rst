Changelog
=========

Version 0.11.0
--------------
**Date:** May 15, 2023

Added
~~~~~
* Introducing the Genv CLI :code:`genvctl`
* Added CLI subcommand :code:`genvctl lock` for locking over-subscribed devices as access control
* Supporting over-subscription in container toolkit with :code:`genv-docker` flag :code:`--over-subscribe`
* Added :code:`genv.sdk.env` SDK package for the active environment
* Supporting locking multiple devices in :code:`genv.core.devices.lock`

Changed
~~~~~~~
* Renamed :code:`genv.sdk.lock_devices` to :code:`genv.sdk.lock`

Version 0.10.1
--------------
**Date:** May 11, 2023

Fixed
~~~~~
* Fixed :code:`genv lock`

Version 0.10.0
--------------
**Date:** May 7, 2023

Added
~~~~~
* Using global lock around critical sections instead of locking per module
* Enriched core entities with more fields
* Python package does not run executables in subprocesses anymore
* Supporting cleaning up entities in place with :code:`.cleanup()`
* Bug fix in serialization of :code:`Report` objects

Changed
~~~~~~~
* Major restructure in project directory
* Renamed :code:`Snapshot` entities
* Renamed :code:`genv.env` to :code:`genv.sdk`

Removed
~~~~~~~
* Removed methods from :code:`genv.envs` and :code:`genv.devices`

Version 0.9.0
-------------
**Date:** May 1, 2023

Added
~~~~~
* Over-subscribe devices with new flag :code:`-o --over-subscribe` to :code:`genv attach`
* New Python SDK at :code:`genv.env`
* Control access to over-subscribed devices with :code:`genv lock` and :code:`genv.env.lock_devices()`
* Added fields and actions to :code:`genv.devices.Device` and :code:`genv.devices.Snapshot`

Changed
~~~~~~~
* Renamed previous command :code:`genv-devices query` to :code:`genv-devices find`
* Using :code:`genv.devices.Snapshot` instead of plain JSON in :code:`genv-devices` and :code:`devices.json` (backwards compatible)

Removed
~~~~~~~
* Removed environment variable :code:`GENV_ALLOW_DEVICE_OVER_ALLOCATION`

Version 0.8.0
-------------
**Date:** April 13, 2023

Added
~~~~~
* Introduced Genv container toolkit: :code:`genv-docker` and the Genv container runtime
* Flags :code:`--count` and :code:`--index` are optional in :code:`genv-devices attach`; if none passed, :code:`genv-devices attach` uses the configured device count if set
* Added :code:`genv.devices.attach()`
* Added :code:`genv.envs.gpus()`
* Added :code:`genv.envs.activate()`
* Added :code:`genv.envs.configure()`

Changed
~~~~~~~
* :code:`nvidia-smi` shim prints warning message when missing information about processes
* :code:`nvidia-smi` shim supports the case when environment variable :code:`CUDA_VISIBLE_DEVICES` is not set
* :code:`nvidia-smi` shim fails if no other :code:`nvidia-smi` executable found

Version 0.7.0
-------------
**Date:** April 4, 2023

Added
~~~~~
* Added monitoring features with Prometheus and Grafana using :code:`genv monitor` and :code:`genv remote monitor`

Version 0.6.0
-------------
**Date:** February 14, 2023

Added
~~~~~
* Added enforcement rule :code:`env-devices`
* Added enforcement rule :code:`env-memory`
* Added command :code:`genv remote query`
* Added flag :code:`-t --timeout` to :code:`genv remote` to set SSH connection timeout
* Added flag :code:`-e --exit-on-error` to :code:`genv remote` to exit on SSH connection issues
* Added flag :code:`-q --quiet` to :code:`genv remote` to ignore SSH connection issues
* Added flag :code:`--no-prompt` to :code:`genv remote activate` to not change shell prompt
* Ignoring commented lines in hostfile used in :code:`genv remote`
* Added query :code:`uid` to :code:`genv-envs query`
* Set up Google Analytics for documentation site

Changed
~~~~~~~
* :code:`genv remote` does not exit on SSH connection issues by default
* Refactor entities and snapshots in :code:`genv` Python package
* Refactor remote capabilities in :code:`genv.remote` Python subpackage
* Combined enforcement rules code under :code:`genv.enforce.rules`
* Improved development setup and in particular :code:`nvidia-smi` development shim and CPU-only setup for remote features

Version 0.5.0
-------------
**Date:** January 27, 2023

Added
~~~~~
* Introduced local and remote enforcement features with two enforcement rules: non environment processes and max devices per user
* Added :code:`genv-usage` executable for taking snapshots and executing enforcement reports
* Supporting querying environment usernames
* Added flag :code:`--quiet` to :code:`genv-devices detach`
* Created :code:`devel` directory and :code:`nvidia-smi` mock shim
* Added environment variable :code:`GENV_TERMINATE_PROCESSES` to allow not terminating processes
* Added environment variable :code:`GENV_MOCK_NVIDIA_SMI_PIDS` to set process identifiers in the :code:`nvidia-smi` mock shim

Changed
~~~~~~~
* Created Python package :code:`genv`
* Major refactor to Python code by adding logic layers (e.g. :code:`genv.envs`) and entities (e.g. :code:`genv.envs.Env`)
* Supporting encoding and decoding entities as JSON
* Supporting sending standard input to SSH commands
* Supporting running SSH commands with :code:`sudo`

Version 0.4.0
-------------
**Date:** December 22, 2022

Added
~~~~~
* Listing active environments on remote hosts with :code:`genv remote envs`
* Showing device information on remote hosts with :code:`genv remote devices`
* Activating an environment on a remote host with :code:`genv remote activate`

Changed
~~~~~~~
* Formatting Python code with black
* Linting Python code with flake8

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
