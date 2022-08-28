# BuxSync configuration

1. Create `secrets.yaml` in main folder of this repository. Use a template provided.
   The login vale is your email registered within your Buxfer account (edit the file and put it there). 
   Password value in `secrets.yaml` is obfuscated.
   Use `--updated-buxfer-password` parameter of `buxsync.py` script to create and save a proper value:
   ```sh
   python buxsync --updated-buxfer-password my_super_password
   ```   

1. Take a look at `config.yaml` and update it if needed. You can find description of all values inside.\
   NOTES. If you have decided not to use XModules of UI.Vision add-on (keep macros in browser local storage),
   set `uivision.use_file_storage` to `false`. Providing a custom browser binary 
   (only Firefox is supported), you must also provide its default download location
   (procedure to automatically locate it in user profile may not work then). 


TODO develop better description of things below

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

