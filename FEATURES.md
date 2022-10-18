# Features

## Table of Contents

* [Environment Status](#environment-status)
* [Activating an Environment](#activating-an-environment)
* [Configuring an Environment](#configuring-an-environment)
    * [Device Count](#configure-the-device-count)
    * [Name](#configure-the-name)
    * [Printing the Configuration](#printing-the-current-configuration)
    * [Clearing the Configuration](#clearing-the-current-configuration)
    * [Configuration as Infrastructure-as-Code](#managing-configuration-as-infrastructure-as-code)
        * [Saving](#saving-configuration)
        * [Loading](#loading-configuration)
* [Attach an Environment to Devices](#attach-an-environment-to-devices)
    * [Detaching](#detaching-an-environment)
    * [Reattaching](#reattaching-an-environment)
* [List Environments](#list-environments)
* [List Devices](#list-devices)
* [Advanced Features](#advanced-features)
    * [Multiple Terminals](#multiple-terminals)


### Environment Status
When using _genv_, you will be running inside environments.

You can see the status of your environment using the command:
```
genv status
```

When not running in an active environment, you will see the following message:
```
$ genv status
Environment is not active
```

When running in an [active](#activating-an-environment) environment, you will see more information about your environment, like its identifier, attached GPUs and configuration.

Here's an example:
```
$ genv status
Environment is active (22716)
Attached to GPUs at indices 0,1

Configuration
    Name: my-environment
    Device count: 2
```

### Activating an Environment
In order to use _genv_, you need to activate the environment using the command:
```
genv activate
```

When activating an environment, it first gets detached from all GPUs on the machine.

You could see this by running `nvidia-smi` and seeing the following output:
```
$ nvidia-smi
No devices were found
```

You will later [configure](#configuring-an-environment) the environment device count and [attach](#attach-an-environment-to-devices) devices to it.

> To see all available options run `genv activate --help` from a non-activated terminal

To deactivate an environment use the following command:
```
genv deactivate
```

### Configuring an Environment
After [activating](#activating-an-environment) your environment, you need to configure it.

> To see all available options and configuration fields run `genv config --help`

#### Configure the Device Count
Configuring the environment device count determines how many GPUs should be accessible to it when attaching devices.

This is done with the following command:
```
genv config gpus <count>
```

#### Configure the Name
Configuring the environment name is not mandatory, but it helps a lot when querying the active environments and devices, and is considered a good practice.

This is done with the following command:
```
genv config name <name>
```

#### Printing the Current Configuration
You can print the current configuration of any field by running the same command as if you want to configure it, just without specifying any value.

For example, the following command would print you the environment name:
```
genv config name
```

You can also print the entire configuration by not specifying any field name:
```
genv config
```

#### Clearing the Current Configuration
You can clear the configuration by passing the argument `--clear` to the configuration command.

This works both for field-specific configuration and for the entire configuration.

For example, the next command would clear the environment name:
```
genv config name --clear
```

While the following command would clear the entire configuration:
```
genv config --clear
```

#### Managing Configuration as Infrastructure-as-Code
_genv_ lets you manage the GPU resources as infrastructure-as-code by letting you save and load environment configurations to and from the disk.

In your project root, create a directory named `.genv` using the command:
```
mkdir -p .genv
```
> The `-p` argument just causes the command to not fail in case the directory already exists

You can verify _genv_ recognizes the directory by running:
```
genv home
```

##### Saving Configuration
You can save the configuration to the disk by running:
```
genv config --save
```

You can also keep your saved configuration up to date by adding the argument `--save` whenever you reconfigure the environment or clear the configuration.

##### Loading Configuration
You can load the configuration from the disk by running:
```
genv config --load
```

Note that _genv_ will automatically load the saved configuration when you activate an environment from your project root directory (as long as you don't pass `--no-load` to `genv activate`).

### Attach an Environment to Devices
After [activating](#activating-an-environment) an environment and [configuring](#configuring-an-environment) its device count, you need to attach GPUs to it.

This is done using the command:
```
genv attach
```

_genv_ will look for available GPUs for your environment.

If there are not enough GPUs available, or the configured device count is greater than the number of devices in the machine, an error message will be printed to the screen and your environment will be detached.

If there are enough GPUs available, _genv_ will attach them to the environment and make them unavailable for other environments.

You can verify that the environment is attached to GPUs by running `nvidia-smi`.
It will show information only about the GPUs that are attached to your environment.

Note that in case your environment configuration gets [loaded](#loading-configuration) upon activation, _genv_ will also automatically try to attach devices to your environment (as long as you don't pass `--no-attach` to `genv activate`).

#### Detaching an Environment
As long as your environment is active and attached to devices, no one else can use them.

In case you want to stop using the attached devices, and release them for someone else to use, you need to detach your environment from them using the following command:
```
genv detach
```

You can verify that your environment is detached by running `nvidia-smi` and seeing the following output:
```
$ nvidia-smi
No devices were found
```

#### Reattaching an Environment
In case you [reconfigure](#configure-the-device-count) the device count of your environment, you need to reattach your environment by rerunning the `genv attach` command.

### List Environments
To see information about all active environments use the following command:
```
genv envs
```

> To see all available options run `genv envs --help`

The information includes:
* Environment identifier
* Linux username and user identifier
* Environment name (if configured)
* Creation time
* Process identifiers of all [terminals](#multiple-terminals) in this environment

Here's a sample output:
```
$ genv envs
ID      USER            NAME            CREATED              PID(S)
1573    paul(1004)      Yesterday       27 minutes ago       1573
12167   john(1005)      Norwegian Wood  7 hours ago          12167
```

### List Devices
To see information about all devices use the following command:
```
genv devices
```

> To see all available options run `genv devices --help`

The information includes:
* Device index
* Environment identifier of the attached environment
* Environment name of the attached environment (if configured)
* Attachment time

Here's a sample output:
```
$ genv devices
ID      ENV ID      ENV NAME        ATTACHED
0       1573        Yesterday       25 minutes ago
1       12167       Norwegian Wood  7 hours ago
```

## Advanced Usage
### Multiple Terminals
When you activate an environment by running `genv activate` in your terminal, a new environment gets created and registered.

Every activated terminal runs within an environment.

_genv_ supports running multiple terminals within the same environment.
This could be useful in many ways.
For example, when running an application in one terminal, and monitoring its GPU resources using `nvidia-smi` in another terminal.

If you have an activated terminal and you want to open another terminal in the same environment, you need to first query the environment identifier using the command:
```
echo $GENV_ENVIRONMENT_ID
```

Then, open another terminal and pass the argument `--id` to your `genv activate` command.
For example:
```
genv activate --id 1667
```

Your terminal should now be activated in the same environment.
You could verify it by running `nvidia-smi` and seeing information about the GPUs of your environment.

_genv_ automatically configures the terminal with the environment configuration and attaches the terminal to the devices that are attached to the environment.
