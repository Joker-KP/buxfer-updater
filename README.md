# BuxSync <a href="https://www.buymeacoffee.com/jokerKP" target="_blank"><img align="right" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 45px !important;width: 163px !important;" ></a>


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

1. **Environment**
   * You need a virtual machine with linux, Python 3 and Firefox + UI.Vision add-on.
   * Install Python packages and make your Firefox uses empty session each time it is launched.
   
   Check all details here: [**Environment preparation**](docs/prepare_environment.md) 
   (list of tools to install, and their settings that matter).
  
1. **BuxSync**\
   Configure BuxSync to use your credentials and customize macros to connect to you bank account(s).\
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

1. How to start the browser maximized? Sometimes an element on page cannot be found
   by UI.Vision add-on because of different window size. If the browser could start
   maximized, it would help a lot.
   
   > You can use an additional [Firefox add-on](https://addons.mozilla.org/en-US/firefox/addon/maximize-all-windows-minimal/) for that.

1. How to make the script run when the virtual machine boots up?
   
   > There is a script in root folder you could use for that purpose: `go.sh`.
   > Please make any necessary adjustments to it before using 
   > (for instance: update name of your Python environment).
   > 
   > In Antix Linux (assuming you have _roxterm_ installed), you can make the script a startup application by
   > adding this line to `~/.desktop-session/startup` file:
   > ``` 
   > roxterm -e path_to_buxsync_folder/go.sh &
   > ```
   > For other distributions look for a similar way in their documentation.
 
1. I moved the solution into another folder and now the script cannot 
   log in to my Buxfer account. How to fix it?
   
   > Simply recreate your obfuscated Buxfer password in secrets.yaml 
   (`python buxsync --updated-buxfer-password my_super_password`).
   So as not to be surprised next time in the same scenario: 
   define `salt` in your `config.yaml` (before recreating obfuscated password). 
   The default value is the folder path where BuxSync is stored.

1. Why don't you use Selenium for logging in and statement downloads?
   
   > I wish I could. Many bank transaction services can detect bots and web-scrapping 
   > operations. This is all to protect your money. However, that makes it more difficult
   > to automate the process of downloading statements with Selenium. There are several
   > services ([Distil Networks](http://www.distilnetworks.com/), e.g.) that can influence/block 
   > your activity when they suspect webdriver usage. For example, trying to log in to 
   > Citibank PL with Selenium will always result "Invalid credentials" message, even if your
   > login and password are correct.
   > 
   > On the other hand there are some workarounds to minimize the chance of being detected
   > (changing name of crucial variables, using your own build of webdriver, etc.). 
   > Still it is like arms race. The only reliable and hopefully long-lasting option
   > is to use a web browser as you would do _normally_, and this is how UI.Vision RPA add-on works.
   > 
   > If you need more details on webdriver detection and workarounds, start here:  
   > [Can a webiste detect when you are using Selenium](https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver)
   
1. Is there a headless mode available?
   
   > No. UI Vision addon needs a desktop. It can be a tiny Linux desktop OS, 
   > but some kind of desktop is required.

1. Can I use another web browser than Firefox?
   
   > Well, it should work. UI Vision RPA is also available for Chrome or Edge.
   > However, it was not tested with other browsers than Firefox.
   > If you want to try another browser, you need to provide full data in `browser` 
   > configuration section of `config.yaml`.