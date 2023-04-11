# Genv Container Toolkit
The Genv container toolkit allows users to run Genv containers.
It consists of two main components: a container runtime and a wrapper for `docker` commands.

## Install
Here are the instructions of how to install the Genv container runtime.

Note that most of the installation steps require high permissions so you will probably need to run them with `sudo`.

### Container runtime
First, you have to install the Genv container runtime by registering it in the file `/etc/docker/daemon.json`.
Here is an example of the file:
```
{
    "runtimes": {
        "genv": {
            "path": "/home/raz/genv/genv-docker/genv-container-runtime.py"
        }
    }
}
```

> Note that the file might not exist and you will have to create it yourself.

Then, restart the Docker daemon for the changes to take effect:
```
systemctl restart docker
```

### Docker wrapper
The best way to run Genv containers is with the `docker` wrapper `genv-docker`.

It is recommended to install it in a system-wide location such as `/usr/local/bin` with the following command:
```
cp -f genv-docker.sh /usr/local/bin/genv-docker
```

If you don't want to install `genv-docker` in a system-wide location, you can run it using its full path instead.

### Verify installation
You can verify the installation with the following command:
```
genv-docker run ubuntu bash -c "env | grep GENV_"
```

You should then see that the environment variable `GENV_ENVIRONMENT_ID` is set.

## Using the Docker wrapper
Use `genv-docker` to run Genv containers.

It automatically sets the container runtime to Genv (i.e. `--runtime genv`).

It also provides additional options to the `genv-docker run` command with are not available for `docker run`.

> You can see all the available options with `genv-docker run --help`

#### `--gpus`
This argument is converted to environment variable [`GENV_GPUS`](#genv_gpus).

#### `--gpu-memory`
This argument is converted to environment variable [`GENV_GPU_MEMORY`](#genv_gpu_memory).

## Using the container runtime directly
You can directly use the container runtime even without `genv-docker` by specifying it in the argument `--runtime` to `docker run`.

For example:
```
docker run --runtime genv -it --rm ubuntu
```

### Environment variables (OCI spec)
The following environment variables are the API for passing arguments to the Genv container runtime when creating containers.

#### `GENV_GPUS`
Configures the container environment device count and attaches devices to the container.

The attached devices are picked by Genv with respect to the device count specified here.

#### `GENV_GPU_MEMORY`
Configures the container environment GPU memory capacity.

## References
1. https://github.com/opencontainers/runtime-spec/blob/main/config.md
2. https://github.com/opencontainers/runtime-spec/blob/main/runtime.md
3. https://github.com/opencontainers/runtime-spec/blob/main/glossary.md
4. https://github.com/opencontainers/runc/blob/main/man/runc.8.md
5. https://github.com/opencontainers/runc/blob/main/man/runc-create.8.md
6. https://github.com/NVIDIA/nvidia-container-runtime
