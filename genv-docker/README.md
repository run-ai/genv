# Genv Container Toolkit
The Genv container toolkit allows users to run containers as active GPU environments.

## Install
Add the Genv container runtime to `/etc/docker/daemon.json`.
Note that the file might not exist and you will have to create it yourself.

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

Restart the Docker daemon:
```
systemctl restart docker
```

## Usage
Specify the runtime in the argument `--runtime` to `docker run`.
For example:
```
docker run --runtime genv -it --rm ubuntu
```

## References
1. https://github.com/opencontainers/runtime-spec/blob/main/config.md
2. https://github.com/opencontainers/runtime-spec/blob/main/runtime.md
3. https://github.com/opencontainers/runtime-spec/blob/main/glossary.md
4. https://github.com/opencontainers/runc/blob/main/man/runc.8.md
5. https://github.com/opencontainers/runc/blob/main/man/runc-create.8.md
