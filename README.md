# BuxSync

---

![](https://github.com/Joker-KP/buxfer-updater/workflows/BuxSync/badge.svg)


Set of scripts to login into bank account, download statement file and upload it to buxfer.com.
Useful for bank accounts not supported for sync in Buxfer.

# Environment preparation

## Tools you need to start

1. Virtual machine with some Debian based linux distribution, for example 
   [Ubuntu](https://ubuntu.com/download) 
   or [AntiX](https://antixlinux.com/download/) (both were tested with this code).
   You need a desktop OS (headless operations are not supported).
1. Python 3 and virtual environment 
   like [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
   or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
1. [Firefox](https://www.mozilla.org/firefox/download/) 
   and [UI.Vision RPA add-on](https://addons.mozilla.org/firefox/addon/rpa)   

## Configuration steps

1. Prepare Python environment
   ```
   conda create -n web python=3.9
   conda activate web
   pip install -r requirements.txt
   ```
1. Configure Firefox to start with empty tab and not to restore previous session. 
   [screen1] [screen2]
   Make sure download process does not ask for a filename as input [screen3].
1. (optional) Install [UI.Vision XModules](https://ui.vision/rpa/x/download).
   Set Home Folder of FileAccess.XModule to `uivision-data` in this repo.
   This will allow you to store your bank login macros on file system (HDD).
   If you wish to keep them in your browser (as local storage) you do not need it.

1. ...

# BuxSync configuration

1. Prepare UI.Vision add-on script to login and download statement from selected account.
   
   First, login to your bank account only with Firefox (within the virtual machine) 
   and make the browser a trusted devices for your bank (so that further logging in
   could be automated without 2FA). Then record all your steps (from logging in to 
   statement download), run and validate your macro manually within UI.Vision RPA add-on.

   Finally, make changes so that to macro could "communicate" with BuxSync.
   See examples in `uivision-data/macros/accounts` folder. Please mind the step that 
   prints out the name of file downloaded (`[echo] File downloaded: ...`) as it is important
   for further processing.

1. Prepare a proper folder for each account you wish to sync with buxfer
   ...

1. secrets.yaml -> auth data for buxfer; use --updated- ... to save obfuscated password.

1. config.yaml -> turn off files storage if no XModules are installed

# BuxSync running

Start it within your conda environment just like that:
```
python buxsync.py
```

# FAQ

1. Why don't you use Selenium for logging in and statement downloads?
   
   I wish I could. Some bank online services are secured from automation tools
   ... (link)
   
1. Is there a headless mode available?
   
   No...

1. How to make the script run when the virtual machine boots up?
   
   There is a script you could ues for that...
   See details in your distribution docs...
   
1. I moved the solution into another folder and now cannot login to Buxfer
   
   Simply recreate your obfuscated Buxfer password in secrets.yaml 
   (`python byxsync.py --up  my_password`).
   So as not to be surprised next time define `salt` in your config.yaml
   The default is the folder path where BuxSync is stored.