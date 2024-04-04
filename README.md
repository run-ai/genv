<p align="center">
  <img src="images/genv blade landscape black@4x.png#gh-light-mode-only" width="600" alt="genv"/>
  <img src="images/genv blade landscape white@4x.png#gh-dark-mode-only" width="600" alt="genv"/>
</p>

# Genv - GPU Environment and Cluster Management
[![Join the community at (https://discord.gg/zN3Q9pQAuT)](https://img.shields.io/badge/Discord-genv-7289da?logo=discord)](https://discord.gg/zN3Q9pQAuT)
[![Docs](https://img.shields.io/badge/docs-genv-blue)](https://docs.genv.dev/)
[![PyPI](https://img.shields.io/pypi/v/genv)](https://pypi.org/project/genv/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/genv?label=pypi%20downloads)](https://pypi.org/project/genv/)
[![Conda](https://img.shields.io/conda/v/conda-forge/genv?label=conda)](https://anaconda.org/conda-forge/genv)
[![Conda - Downloads](https://img.shields.io/conda/dn/conda-forge/genv?label=conda%20downloads)](https://anaconda.org/conda-forge/genv)

Genv is an open-source environment and cluster management system for GPUs.

Genv lets you easily control, configure, monitor and enforce the GPU resources that you are using in a GPU machine or cluster.

It is intendend to ease up the process of GPU allocation for data scientists without code changes 💪🏻

Check out the Genv [documentation site for more details](https://docs.genv.dev) and [the website](https://genv.dev/) for a higher-level overview of all features.

This project was highly inspired by [pyenv](https://github.com/pyenv/pyenv) and other version, package and environment management software like [Conda](https://docs.conda.io/projects/conda/en/latest/), [nvm](https://github.com/nvm-sh/nvm), [rbenv](https://github.com/rbenv/rbenv).

![Example](images/example.png)

## :question: Why Genv?

- Easily share GPUs with your teammates
- Find available GPUs for you to use: on-prem or on cloud via remote access
- Switch between GPUs without code changes
- Save time while collaborating
- Serve and manage local LLMs within your team’s cluster

Plus, it's 100% free and gets installed before you can say Jack Robinson.

## :raising_hand: Who uses Genv? 
### Data Scientists & ML Engineers, who:
- Share GPUs within a research team
  - Pool GPUs from multiple machines (see [here](images/Pool_resources.gif)), and allocate the available machine without SSH-ing every one of them 
  - Enforce GPU quotas for each team member, ensuring equitable resource allocation (see [here](images/Enforcement.gif))
  - Reserve GPUs by creating a Genv environment for as long as you use them with no one else hijacking them (see [here](images/Fractions.gif))
- Share GPUs between different projects
  - Allocate GPUs across different projects by creating distinct Genv environments, each with specific memory requirements 
  - Save environment configurations to seamlessly resume work and reproduce experiment settings at a later time (see [here](images/Infra_as_Code.gif))
- Serve local open-source LLMs for faster experimentation within the whole team
  - Deploy local open-source LLMs for accelerated experimentation across the entire team
  - Efficiently run open-source models within the cluster

### Admins, who:
- Monitor their team’s GPU usage with Grafana dashboard (see the image below)
- Enforce GPU quotas (number of GPUs and amount of memory) to researchers for a fair game within the team (see [here](images/Enforcement.gif))
  

<img src="images/Genv_grafana.png" alt="genv grafana dashboard"/>

## Ollama 🤝 Genv
Ready to create an LLM playground for yourself and your teammates? 

Genv integrates with Ollama for managing Large Language Models (LLMs). This allows users to efficiently run, manage, and utilize LLMs on GPUs within their clusters.
```
$ genv remote -H gpu-server-1, gpu-server-2 llm serve llama2 --gpus 1
```
Check out our [documentation](https://docs.genv.dev/llms/overview.html) for more information.

## 🏃 Quick Start
Make sure that you are running on a GPU machine:
```
$ nvidia-smi
Tue Apr  4 11:17:31 2023
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 470.161.03   Driver Version: 470.161.03   CUDA Version: 11.4     |
|-------------------------------+----------------------+----------------------+
...
```
1. Install Genv

- Using pip
```
pip install genv
```
- Using conda
```
conda install -c conda-forge genv
```
2. Verify the installation by running the command:
```
$ genv status
Environment is not active
```
3. Activate an environment (in this example, we activate an environment named <em>my-env</em> that contains <em>1 GPU</em> and will have <em>4GB</em> of memory)
```
$ genv activate –-name my-env —-gpus 1
(genv:my-env)$ genv config gpu-memory 4g
(genv:my-env)$ genv status
Environment is active (22716)
Attached to GPUs at indices 0

Configuration
   Name: my-env
   Device count: 1
   GPU memory capacity: 4g
```
4. Start working on your project!

## :scroll: Documentation

Check out the Genv [documentation site](https://docs.genv.dev) for more details.


## :dizzy: Simple Integration & Usage with your fav IDE


Integration with VSCode [(Take me to the installation guide!)](https://github.com/run-ai/vscode-genv) |
:-------------------------:|
<img src="images/overview.gif" width="800" alt="genv vscode"/> |

<br />

Integration with JupyterLab [(Take me to the installation guide!)](https://github.com/run-ai/jupyterlab_genv) |
:-------------------------:|
<img src="images/overview_jupyterlab.gif" width="800" alt="genv jupyterlab"/> |



A PyCharm integration is also in our roadmap so stay tuned!



## 🏃🏻 Join us in the AI Infrastructure Club

[<img src="https://img.shields.io/badge/Discord-Join%20the%20community!-7289da?style=for-the-badge&logo=discord&logoColor=7289da" height="30" />](https://discord.gg/zN3Q9pQAuT)

We love connecting with our community, discussing best practices, discovering new tools, and exchanging ideas with makers about anything around making & AI infrastructure. So we created a space for all these conversations. Join our Discord server for:

- Genv Installation and setup support as well as best practice tips and tricks directly for your use-case
- Discussing possible features for Genv (we prioritize your requests) 
- Chatting with other makers about their projects & picking their brain up when you need help
- Monthly Beers with Engineers sessions with amazing guests from the research and industry ([Link to previous session recordings](https://www.youtube.com/@runai_/search?query=beers%20with%20engineers))


## License
The Genv software is Copyright 2022 [Run.ai Labs, Ltd.].
The software is licensed by Run.ai under the AGPLv3 license.
Please note that Run.ai’s intention in licensing the software are that the obligations of licensee pursuant to the AGPLv3 license should be interpreted broadly.
For example, Run.ai’s intention is that the terms “work based on the Program” in Section 0 of the AGPLv3 license, and “Corresponding Source” in Section 1 of the AGPLv3 license, should be interpreted as broadly as possible to the extent permitted under applicable law.
