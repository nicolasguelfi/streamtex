---
title: StreamTeX
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: StreamTeX test space
---
## 🤖 Commandes d'installation et d'exécution StreamTeX

Pour installer les dépendances du projet et exécuter StreamTeX, voici les commandes de base à connaître :

### 1. Installation des dépendances (création d’un virtualenv et installation de tout)
Le fichier `.python-version` à la racine du projet fixe la version de Python (3.13.7). Le script `uvsync.sh` garantit un environnement reproductible sur **toutes les machines** : il met à jour **uv**, installe la bonne version de Python si nécessaire, puis synchronise les dépendances.

```bash
./uvsync.sh
```

> **Pourquoi `./uvsync.sh` plutôt que `uv sync` ?**
> Un simple `uv sync` peut échouer si la version de Python requise n’est pas disponible localement ou si **uv** est trop ancien pour la connaître. Le script s’en charge automatiquement.

### 2. Lancer un projet StreamTeX
(adapté à votre dossier projet)
```bash
uv run streamlit run projects/<votre_projet>/book.py
```

Pour lancer plusieurs projets en parallèle, spécifiez un port différent (le port par défaut est 8501) :
```bash
uv run streamlit run projects/<autre_projet>/book.py --server.port 8502
```

### 3. Lancer le projet de test/démonstration
```bash
uv run streamlit run tests/test_project/book.py
```

### 4. Lancer les tests unitaires
```bash
uv run pytest tests/ -v
```

> **Note importante :**
> - Toujours utiliser `uv run ...` au lieu des commandes `python`, `streamlit` ou `pytest` directement.
> - Si vous ajoutez une nouvelle dépendance :
>   - Pour une dépendance standard : `uv add <package>`
>   - Pour une dépendance de développement : `uv add --group dev <package>`
>   - Ensuite relancez `uv sync` pour mettre à jour l'environnement.
>

# StreamTeX

StreamTeX is a Python project that provides a modular "block"-based framework to dynamically generate HTML elements with customizable styles, specifically designed to enhance Streamlit applications. These elements rely on, and can be mixed, with native streamlit components.

## Contents
This github provides the following main folders: ```streamtex```, ```projects/```, and ```documentation/```.
The ```streamtex``` folder contains the source files for the StreamTeX library.
The ```projects/``` folder contains StreamTeX projects (e.g., ```projects/project_aiai18h``` is an example project).
The ```documentation/``` folder contains coding standards, cheatsheets, and the ```template_project``` which you can copy as a template to start any new project.

## Set up 
Create a folder for your StreamTeX projects. Download the ```streamtex``` folder into that folder.
Then, in your chosen python environment, run ```pip install -r requirements.txt```. This will install streamlit and all other dependencies.

StreamTeX is built on top of Streamlit, and thus uses a similar project structure, with some additions.
Inside the folder you created for your StreamTeX porjects, create a project folder using the following structure:

```md
your-project-folder/
├── .streamlit/
│   └── config.toml 
├── blocks/ 
│   └── __init__.py
├── static/
│   └── images/ # and other folders for all kinds of assets like videos if needed
├── custom/
│   ├── themes.py
│   └── styles.py
├── book.py
└── setup.py

```
The ```.streamlit``` folder contains the streamlit configuration. Inside that folder, the config.toml file should have ```enableStaticServing = true``` (You can just copy the config.toml file into your own project's ```.streamlit``` folder). 
The ```blocks``` folder should contain all block python files (see the Blocks section below). This folder must contain a `__init__.py` file with the same code as the `documentation/template_project/blocks/__init__.py`. This allows referencing blocks more easily.
The ```static``` folder contains the statically-served files, such as images. You may NOT rename the ```static``` or ```images``` folders.
The ```custom``` folder contains the project specific files, specifically user-created custom styles and themes. You may rename these folders and files.
The ```book.py``` file is the main entry of your web page. This is where the ```st_book()``` function is called, creating the whole page.
The ```setup.py``` file is required to be imported at the top of ```book.py```. It sets up the PATH so that streamtex is usable inside any project folder. 


In the command line, navigate to your project's folder and, run ```streamlit run book.py```.


## book.py

This file should always start with these lines:
``` python
import streamlit as st 
import setup
```
This imports streamlit and adds the parent folder to the python path. This is essential for the project to be able to access the```streamtex``` folder.

After this, you can import StreamTeX (```import streamtex as sx```), your custom styles and your block files, set up your streamlit page through ```st.set_page_config()``` and other streamlit code. 
The final line should be ```sx.st_book(module_list)```, where ```module_list``` is a list of the block modules to include in your Streamlit web book in the order of appearance.

## Blocks

These python files define the modular parts of your streamlit web book. 
These must always contain a ```build()``` function, returning nothing, that defines the content of the block using either streamlit functions, StreamTeX's `st_*` helper functions using (possibly custom) styles, or both. For an example, look in ```documentation/template_project/blocks/show_off.py``` (this file also shows all st_* functions and the different ways they can be used). To start any new block, it is recommended to just make a copy of ```documentation/template_project/blocks/base.py```. 

## Styles

The StreamTeX st_* functions allow for an extensive variety in styling through its style parameters. These parameters accept an object of the ```Style``` class, a wrapper class for css styles which allows for easily combining styles. For lists, there's a ```ListStyle``` subclass of ```Style``` which defines the icons of the bullet points used for lists. Each style also has an id, which is used for themes. Additionally, the st_grid function, which serves as a partioned container of multiple blocks, can use a ```StyleGrid``` class object, which represents a list/matrix of styles. 
The StreamTeX librabry already provides an extensive array of atomic styles in ```streamtex.styles```.


### Themes

Users may create theme dictionaries which can be used to replace the look of certain styles using the styles' ids. For an example, see ```documentation/template_project/custom/themes.py```.


### Custom Styles
In ```custom/styles.py```, you may define a new Custom class, which will hold all new styles you may want to create and not available through StreamTeX. At the end of the python file, define a new class Styles, a subclass of ```streamtex.styles.StreamTeX_Styles```, with a new property referencing your new custom styles class. For reference, see ```documentation/template_project/custom/styles.py``` or ```tests/test_project/custom/styles.py```

Example:
```python 
class Styles(StreamTeX_Styles):
    project = Custom
```

## Table of Contents

A table of contents may be generated by using ```st_write()```'s ```toc_lvl``` and ```label``` parameters. A ToC will then appear on the side bar. In the ```book.py``` file, the user may also define where (if at all) a larger ToC should appear on the web book as part of the ```st_book()```'s ```toc_config``` parameter.

## Configuration
In ```book.py```, you may change the library's configuration, such as chosen style theme dictionary and table of contents settings (positioning in the page, titles, styles, etc). See ```documentation/template_project/book.py``` for an example.


## Additional Features

### Ctrl + L to show block path
When hovering your mouse over a section of the page, you may press Ctrl+L to show a tooltip with the relative path in the project of the block you're hovering over. This also copies the relative path to your clipboard.

### Zoom
In the sidebar, a dropdown menu is available to rescale the page to different sizes, from 10% to 200% of base size. It is set to "fit" by default, and it is recommended to leave it as such.

# Streamlit Version
This project was last updated with streamlit version 1.54, and as such later updates of streamlit may cause conflicts or unexpected behavior.

# Deployment

## Docker with HuggingFace 

### Create a Python environment

### Git and LFS
- make sure git and lfs are installed: 
  - In MacOS, run ```brew install git git-lfs```
- Update both of them: ```git lfs install``

### Get HuggingFace token
- Make sure to have ran ```pip install -r requirements.txt``` so that the huggingface cli is installed.
- In your HuggingFace profile, go Settings → Access Tokens → New token; select "Write" scope.
- locally (in your python env), run ```hf auth login```, input your huggingface token when prompted. Accept to add token as git credential.
- cd to your local repo
- add your huggingface space as a remote repo by running ```git remote add hf https://huggingface.co/spaces/<user-or-org>/<space-name>```
- Optionally, add large binary files to lsf: ```git lfs track "*.png" "*.jpg" "*.webp" "*.mp4" "*.gif" ```
- Done!


## Ansible in GCP

### Pre-requisites
- A local machine capable of running Linux (for Windows machines, make sure WSL is set up), and with the GCloud CLI installed.
- A Google Cloud Account with billing enabled.
- A GitHub repository with your StreamTeX project folder, and the ```streamtex``` folder.

### 1. Create a VM instance in GCP
- Under Compute Engine > VM instances, create a new Instance, and name it (ex. ```streamtex-vm```). 
- Choose a Region and Zone.
- Choose a Linux boot disk (ex. Ubuntu 22.04).
- Choose a machine type (for most StreamTeX projects, ```e2-micro``` is enough.)
- Allow HTTP/HTTPS traffic.
- Create the instance and note down its External IP (ex. 12.34.56.78)


### 2. Enable SSH access
- On your local machine (WSL if windows), generate an SSH key with ```ssh-keygen -t ed25519 -C "your-email@example.com"```. Press enter.
- Then ```cat ~/.ssh/id_ed25519.pub```, copy the output.
- In GCP, under Computer Engine > Metadata > SSH Keys, click "Add SSH Key" and paste the copied SSH key.
- Test the ssh access with ```ssh -i ~/.ssh/id_ed25519 your-user@your-vm-external-ip```. Type `exit` to go back.


### 3. Install Ansible
- Inside local machine (WSL if windows), run ```sudo apt update && sudo apt install -y ansible```
- run ```ansible --version``` to verify your installation.

### 4. Configuring Ansible
- In your local machine, create an `inventory.ini` file:
```ini
[webserver]
your-vm-external-ip ansible_user=your-user ansible_ssh_private_key_file=~/.ssh/id_ed25519

[webserver:vars]
ansible_become=True
ansible_python_interpreter=/usr/bin/python3
```
- Then create a  `deploy.yml` file:
```yaml
- name: Deploy StreamTeX App on Google Cloud VM
  hosts: webserver
  become: yes  # Run tasks as root

  vars:
    project_dir: "/home/your-user/streamtex_app"
    venv_dir: "/home/your-user/streamtex_env"
    streamtex_script: "/home/your-user/streamtex_app/your-project-folder/book.py"
    repo_url: "git@github.com:your-github-username/your-github-repo.git"
    user: "your-user"

  tasks:

    - name: Update and upgrade system packages
      apt:
        update_cache: yes
        upgrade: dist
        cache_valid_time: 3600

    - name: Install required system packages
      apt:
        name:
          - python3.11
          - python3.11-venv
          - python3-pip
          - git  # Needed to clone the repo
        state: present

    - name: Ensure project directory exists
      file:
        path: "{{ project_dir }}"
        state: directory
        mode: "0755"
        owner: "{{ user }}"
        group: "{{ user }}"

    - name: Clone the GitHub repository (Private Repo)
      git:
        repo: "{{ repo_url }}"
        dest: "{{ project_dir }}/repo"
        version: main
        force: yes
      environment:
        GIT_SSH_COMMAND: "ssh -i /home/your-user/.ssh/id_ed25519 -o StrictHostKeyChecking=no"

    - name: Copy only `your-project-folder` folder from the repo
      command: cp -r "{{ project_dir }}/repo/your-project-folder" "{{ project_dir }}/"

    - name: Copy only `streamtex` folder from the repo
      command: cp -r "{{ project_dir }}/repo/streamtex" "{{ project_dir }}/"

    - name: Create virtual environment
      command:
        cmd: "python3.11 -m venv {{ venv_dir }}"
        creates: "{{ venv_dir }}/bin/activate"

    - name: Install dependencies inside virtual environment
      pip:
        virtualenv: "{{ venv_dir }}"
        name:
          - streamtex==1.54.0
          - beautifulsoup4>=4.10.0
          - google-api-python-client>=2.155.0
          - watchdog

    - name: Create a systemd service for StreamTeX
      copy:
        dest: /etc/systemd/system/streamtex.service
        content: |
          [Unit]
          Description=StreamTeX Web Book
          After=network.target

          [Service]
          ExecStart={{ venv_dir }}/bin/python3 -m streamlit run {{ streamtex_script }} --server.port 8501 --server.headless true --server.enableCORS false --server.enableXsrfProtection false --server.address 0.0.0.0
          Restart=always
          User={{ user }}
          WorkingDirectory={{ project_dir }}/your-project-folder

          [Install]
          WantedBy=multi-user.target

    - name: Reload systemd
      command: systemctl daemon-reload

    - name: Enable and start StreamTeX service
      command: systemctl enable --now streamtex
```

### 5. Deploy Ansible Playbook
- In your local machine (or WSL) run ```ansible-playbook -i inventory.ini deploy.yml```
- SSH into the vm, and then run ```sudo systemctl status streamtex``` to check if it is running
- Open the web book in a browser at ```http://your-vm-external-ip:8501```.


### Maintenance
- Whenever you change the files in your github repository, you just need to do ```ansible-playbook -i inventory.ini deploy.yml``` in your local machine to update the VM.