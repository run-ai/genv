# GPU Environment Management

rnenv lets you easily configure your environment and allows you to control the GPU resources it uses.

## Development
Open a terminal in the project directory.

> We support `bash` terminals only at the moment. Query your shell using `echo $SHELL` and run `bash` if it is not your shell.

Then run the following commands to configure your terminal:
```
export PATH=$PWD/bin:$PATH
eval "$(rnenv init -)"
```

You can test it by running:
```
rnenv
```

> NOTE: If you are on a CPU machine, mock the amount of GPUs by setting the environment variable `RNENV_DEVICES`

## Reference
### Environment Variables
---
`RNENV_DEVICES`

Amount of GPUs that are managed by the coordinator.
By default it is queried using `nvidia-smi`.

---
`RNENV_TMPDIR`

Path of the temp directory where all state json files are stored.
Default is `/var/tmp/rnenv`.
