# Installation

## Table of Contents

* [Installation Guide for VSCode](https://github.com/run-ai/vscode-genv)
* [Installation Guide for JupyterLab](https://github.com/run-ai/jupyterlab_genv)
* [Installation Guide for Terminal Usage](#from-source)
    * [Setting up Your Shell](#setting-up-your-shell)
    * [Dependencies](#dependencies)
    * [Uninstalling](#uninstalling)

## 💫 Installation Guide for VSCode

For the steps and more information about the usage, please refer to [this page](https://github.com/run-ai/vscode-genv)

## 💫 Installation Guide for JupyterLab

For the steps and more information about the usage, please refer to [this page](https://github.com/run-ai/jupyterlab_genv)

## 💫 Installation Guide for Terminal Usage

### From Source
It's super easy to get _genv_ as everything you need is to clone this Git repository into somewhere on your machine.
Your home directory is a great place to keep it:
```
git clone https://github.com/run-ai/genv.git ~/genv
```

#### Setting Up Your Shell
In order to use _genv_ you need to set up your shell environment with the following commands:
```
export PATH=$HOME/genv/bin:$PATH
eval "$(genv init -)"
```

You should add them to your `~/.bashrc` or any other equivalent file.

Afterward, for this to take effect, either reopen your terminal or restart your shell using the command:
```
exec $SHELL
```

To verify the installation worked, run the following command:
```
genv
```

You should be able to see all the available `genv` commands.

#### Dependencies
_genv_ uses Python 3 so make sure you have it also installed.

#### Uninstalling
To uninstall _genv_ simply remove the _genv_ directory:
```
rm -rf $(genv root)
```

You will also need to remove the commands you added to your `~/.bashrc` or any other equivalent file.
