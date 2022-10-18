<p align="center">
  <img src="images/genv blade landscape black@4x.png#gh-light-mode-only" width="600" alt="genv"/>
  <img src="images/genv blade landscape white@4x.png#gh-dark-mode-only" width="600" alt="genv"/>
</p>

# genv (GPU Environment Management) [![Join the community at https://join.slack.com/t/genvcommunity/shared_invite/zt-1i70tphdc-DmFgK5yr3HFI8Txx1yFXBw](https://img.shields.io/badge/Slack-genv-ff007f?logo=slack)](https://join.slack.com/t/genvcommunity/shared_invite/zt-1i70tphdc-DmFgK5yr3HFI8Txx1yFXBw) [![Join the chat at https://gitter.im/run-ai-genv/community](https://badges.gitter.im/run-ai-genv/community.svg)](https://gitter.im/run-ai-genv/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


*genv* lets you easily control, configure and monitor the GPU resources that you are using.

It is intendend to ease up the process of GPU allocation for data scientists without code changes 💪🏻

This project was highly inspired by [pyenv](https://github.com/pyenv/pyenv) and other version, package and environment management software like [Conda](https://docs.conda.io/projects/conda/en/latest/), [nvm](https://github.com/nvm-sh/nvm), [rbenv](https://github.com/rbenv/rbenv).

![Example](images/example.png)

## 🔥 Why You Should use *genv*

Because with *genv*, you will:

- Easily share GPUs with your teammates
- Find available GPUs for you to use - on-prem or on cloud via remote access
- Switch between GPUs without code changes
- Reserve GPU resources for as long as you use them with no one else hijacking them
- Reproduce your experiment environment easily
- Save time while collaborating

Plus, it's 100% free and gets installed before you can say Jack Robinson.

## 🎉 Simple Integration & Usage with your fav IDE


Integration with VSCode [(Take me to the installation guide!)](https://github.com/run-ai/vscode-genv) | 
:-------------------------:|
<img src="images/overview.gif" width="800" alt="genv vscode"/> |  

<br />

Integration with JupyterLab [(Take me to the installation guide!)](https://github.com/run-ai/jupyterlab_genv) |
:-------------------------:|
<img src="images/overview_jupyterlab.gif" width="800" alt="genv jupyterlab"/> |



A PyCharm integration is also in our roadmap so stay tuned!

## 🏃🏻 Be an early runner in the genv community! 

[<img src="https://img.shields.io/badge/Slack-Join%20the%20community!-ff007f?style=for-the-badge&logo=slack&logoColor=ff007f" height="30" />](https://join.slack.com/t/genvcommunity/shared_invite/zt-1i70tphdc-DmFgK5yr3HFI8Txx1yFXBw)

Join our Slack channel with the creators of *genv* and start building your models faster!

- Installation and setup support as well as best practice tips and tricks directly for your use-case
- Discuss possible features
- Monthly coffee breaks to get to know the rest of the community

Looking forward to seeing you as a part of the community!

## 📂 Table of Contents
* [Installation](INSTALLATION.md#installation)
    * [Installation Guide for VSCode](https://github.com/run-ai/vscode-genv)
    * [Installation Guide for JupyterLab](https://github.com/run-ai/jupyterlab_genv)
    * [Installation Guide for Terminal Usage](INSTALLATION.md#from-source)
* [Features](FEATURES.md#features)
    * [Environment Status](FEATURES.md#environment-status)
    * [Activating an Environment](FEATURES.md#activating-an-environment)
    * [Configuring an Environment](FEATURES.md#configuring-an-environment)
        * [Device Count](FEATURES.md#configure-the-device-count)
        * [Name](FEATURES.md#configure-the-name)
        * [Printing the Configuration](FEATURES.md#printing-the-current-configuration)
        * [Clearing the Configuration](FEATURES.md#clearing-the-current-configuration)
        * [Configuration as Infrastructure-as-Code](FEATURES.md#managing-configuration-as-infrastructure-as-code)
            * [Saving](FEATURES.md#saving-configuration)
            * [Loading](FEATURES.md#loading-configuration)
    * [Attach an Environment to Devices](FEATURES.md#attach-an-environment-to-devices)
        * [Detaching](FEATURES.md#detaching-an-environment)
        * [Reattaching](FEATURES.md#reattaching-an-environment)
    * [List Environments](FEATURES.md#list-environments)
    * [List Devices](FEATURES.md#list-devices)
* [Advanced Features](FEATURES.md#advanced-features)
    * [Multiple Terminals](FEATURES.md#multiple-terminals)
* [Development](DEVELOPMENT.md#development)
    * [Setup](DEVELOPMENT.md#setup)
    * [Reference](DEVELOPMENT.md#reference)
* [License](#license)


## 🏆 Special Thanks for Runners

- You could be mentioned here! Submit a feature request to be featured here 💥

## License 
The genv software is Copyright 2022 [Run.ai Labs, Ltd.].
The software is licensed by Run.ai under the AGPLv3 license.
Please note that Run.ai’s intention in licensing the software are that the obligations of licensee pursuant to the AGPLv3 license should be interpreted broadly.
For example, Run.ai’s intention is that the terms “work based on the Program” in Section 0 of the AGPLv3 license, and “Corresponding Source” in Section 1 of the AGPLv3 license, should be interpreted as broadly as possible to the extent permitted under applicable law.
