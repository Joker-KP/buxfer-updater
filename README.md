# BuxSync

---

![](https://github.com/Joker-KP/buxfer-updater/workflows/BuxSync/badge.svg)


Automatically log in to your bank account, download statement file and upload it to
[buxfer.com](https://www.buxfer.com/). Useful for bank accounts not supported for sync in Buxfer.

# Overview

[Buxfer](https://www.buxfer.com/) is an online money management software for tracking expenses, budgets, etc.
It can automatically sync your accounts by connecting to your bank or credit card and downloading transactions
and balances. Over 20,000 banks are supported all across the world. Still...

There are many bank accounts not available for sync in Buxfer. For these ones, you can only manually enter your
transactions or upload a statement (set of transactions) in a format that Buxfer understands.

...and here comes **BuxSync**

It can use browser add-on (UI.Vision RPA) to replay your login procedure and statement download
for any bank you wish. Then it can convert it to the format that is known by Buxfer API,
and upload the updated transactions to your Buxfer account.

**It can make ALL your accounts sync automatically with Buxfer!**

# Configuration

1. You need a virtual machine with linux, Python 3 and Firefox + UI.Vision add-on.\
   Check details: [Environment preparation](docs/prepare_environment.md).
2. Install Python packages and make your Firefox uses empty session each time it is launched.\
   Check details: [Environment preparation](docs/prepare_environment.md) (list of tools to install and their settings that matter).
3. Configure BuxSync to use your credentials and customize macros to connect to you bank account(s).\
   See details in [**BuxSync configuration**](docs/buxsync_configuration.md) document.

# Running BuxSync

Start it within your conda environment just like that:
```sh
python buxsync.py
```

There are several additional parameters you may provide:

| Parameter&nbsp;name&nbsp;     | Argument needed     | Description                                                                                                                                                                        |
|-------------------------------|:-------------------:|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--updated-buxfer-password`   |         yes         | Encodes your Buxfer account password provided<br> as an argument and writes it to `secrets.yaml`<br> in obfuscated form.                                                           |
| `--no-download`               |          no         | Do not download statements from bank account.<br> Useful for testing upload functionality (assuming<br> you provide a manually downloaded files<br> in a proper `data` sub-folder. |
| `--no-upload`                 |          no         | Do not upload statements to Buxfer account.<br> Useful while testing the download<br> and conversion process only.                                                                 |
| `--folder-filter`             |         yes         | Process only folders that include value<br> passed as argument here (an inclusive filter).                                                                                         |


# FAQ

1. Why don't you use Selenium for logging in and statement downloads?
   
   > I wish I could. Some bank online services are secured from automation tools
   TODO... (link)
   
1. Is there a headless mode available?
   
   > No... TODO

1. How to make the script run when the virtual machine boots up?
   
   > There is a script you could ues for that...
   See details in your distribution docs... TODO
   
1. I moved the solution into another folder and now the script cannot 
   log in to my Buxfer account. How to fix it?
   
   > Simply recreate your obfuscated Buxfer password in secrets.yaml 
   (`python buxsync --updated-buxfer-password my_super_password`).
   So as not to be surprised next time in the same scenario: 
   define `salt` in your `config.yaml` (before recreating obfuscated password). 
   The default value is the folder path where BuxSync is stored.
   
1. How to start the browser maximized? Sometimes an element on page cannot be found
   by UI.Vision add-on because of different window size. If the browser could start
   maximized, it would help a lot.
   
   > You can use an additional [Firefox add-on](https://addons.mozilla.org/en-US/firefox/addon/maximize-all-windows-minimal/) for that.