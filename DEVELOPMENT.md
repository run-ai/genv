# Development

## Table of Contents
* [Setup](#setup)
* [Reference](#reference)


### Setup
Open a terminal in the project directory.

> We support `bash` terminals only at the moment. Query your shell using `echo $SHELL` and run `bash` if it is not your shell.

Then run the following commands to configure your terminal:
```
export PATH=$PWD/bin:$PATH
eval "$(genv init -)"
```

You can test it by running:
```
genv
```

> NOTE: If you are on a CPU machine, mock the amount of GPUs by setting the environment variable `GENV_DEVICES`

#### Docker
You can also use a container for the development.
This is useful if you are using macOS as _genv_ is developed for Linux systems and some things are not available in macOS (e.g. `/proc` filesystem).

Use the following command:
```
docker run -it --rm --name genv \
    -v $PWD:/genv \
    -v /var/tmp:/var/tmp \
    python \
    bash --rcfile /genv/.bashrc
```

### Reference
#### Environment Variables
---
`GENV_DEVICES`

Amount of GPUs that are managed by _genv_.
By default, it is queried using `nvidia-smi`.
This is mainly for development environments on CPU machines where `nvidia-smi` is not available.

---
`GENV_TMPDIR`

Path of the temp directory where all state JSON files are stored.
Default is `/var/tmp/genv`.

#### Shims
---
`nvidia-smi`

By default, `nvidia-smi` shows information about all GPUs.

It is configurable by passing the argument `--id` and specifying GPU indices.
It is also good to note that `nvidia-smi` ignores the environment variable `CUDA_VISIBLE_DEVICES` as it uses NVML and not CUDA.

This shim passes this argument to `nvidia-smi` and specifies the attached device indices.
