<p align="center">
  <img src="images/genv blade landscape black@4x.png#gh-light-mode-only" width="600" alt="genv"/>
  <img src="images/genv blade landscape white@4x.png#gh-dark-mode-only" width="600" alt="genv"/>
</p>

# genv (GPU Environment Management) [![Join the community at (https://discord.gg/zN3Q9pQAuT)](https://img.shields.io/badge/Discord-genv-7289da?logo=discord)](https://discord.gg/zN3Q9pQAuT) [![Join the chat at https://gitter.im/run-ai-genv/community](https://badges.gitter.im/run-ai-genv/community.svg)](https://gitter.im/run-ai-genv/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


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

## Documentation

Check out the genv [documentation site](https://run-ai.github.io/genv).

## 💨 Guide to the Roadmap

### **What is coming up soon?**

After gathering valuable feedback and comments from data scientists, we created the following short-term roadmap for genv:

**1. (Implemented) Environment specific information:** With this feature, you will be able to see the processes and machines specifically to your GPU environment when you type nvidia-smi

**2. (Implemented) Docker support:** Running Docker containers powered by the GPUs in your environment

**3. Configuring GPU memory:** Specifying the GPU memory that needs to be configured in an environment

**4. To be able to provision the GPU fractions**

**5. Support the extensions (VSCode, JupyterLab) with the new features above**


The long-term overview of the roadmap includes 3 main category;

- **EXTENSIONS**
    - Displaying
        - memory information of the GPUs
        - GPU specs
        - which environments are running on that GPU
        - CUDA version
        - icons at the bottom of the extensions to show the current status of the GPU memory consumption
- **CORE:**
    - Configuring GPU memory with config command (fractional GPUs)
        - Warning for exceeding the memory requests when the training uses more than the environment is assigned to
    - Installing with wrappers (e.g. For PyCharm)
    - Notification about resources when they get available
- **GPU PROVISIONING:**
    - Provisioning of fractional GPUs
    - Smart provisioning
    - Dynamical provisioning
        - Provisioning per user or per environment when new user joins
    - Pre-configuring of the environments
        - Admin mode to manage the environment

## 🏃🏻 Be an early runner in the AI Infrastructure Club!

[<img src="https://img.shields.io/badge/Discord-Join%20the%20community!-7289da?style=for-the-badge&logo=discord&logoColor=7289da" height="30" />](https://discord.gg/zN3Q9pQAuT)

Looking for a place to discuss best practices, discover new tools, and exchange ideas about how to make the most out of our GPUs without losing time? Join our Discord server with the creators of *genv* and [*rntop*](https://github.com/runai/rntop) - start building your models faster!

- Installation and setup support as well as best practice tips and tricks directly for your use-case
- Discuss possible features
- Monthly Beers with Engineers sessions with amazing guests
- Networking events 
- and many more...

## 🏆 Special Thanks for Runners

- You could be mentioned here! Submit a feature request to be featured here 💥

## License
The genv software is Copyright 2022 [Run.ai Labs, Ltd.].
The software is licensed by Run.ai under the AGPLv3 license.
Please note that Run.ai’s intention in licensing the software are that the obligations of licensee pursuant to the AGPLv3 license should be interpreted broadly.
For example, Run.ai’s intention is that the terms “work based on the Program” in Section 0 of the AGPLv3 license, and “Corresponding Source” in Section 1 of the AGPLv3 license, should be interpreted as broadly as possible to the extent permitted under applicable law.
