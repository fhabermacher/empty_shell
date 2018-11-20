# empty_shell
## Prerequisites:

1. python3 = python 3.5 (3.6 likely to not work)

2. Active System Environment Variable
`SAPO_TEST_DIR`
pointing to the directory (without final slash /) where the application resides, and where it can
read and write files & folders, e.g.
`/home/<yourusername>/empty_shell` where *<yourusername>* is the folder into which you cloned the *empty_shell* repo


## Setup:
```
cd py
./setup.sh
```

## Launching:
```	
cd py
source venv/bin/activate
./app.py
```
Then (ctrl-)click the indicated browser link (e.g. http://127.0.0.1:8050/) to open the app in the browser
	
Login credentials in browser app:
  User Name: test
  PW: yes


## Verifying current functionality remains intact after deployment:

1. File upload
   - *Drag or Browse File(s)* fields must allow to add files
   - Files added, must become selectable in the respective Dropdown on the left
2. Cookie functionality must make the last selected file from be pre-selected after restarting the app
3. *Launch* button must be or become active: at latest few sec after opening app in brwoser, or else after clicking *Activate* button
4. **This is the *core* part* *Click on *Launch* button must launch the simulation, running it for 10sec
   - You will see it progress in the text indication below the Launch button, right above the Plot button.
	 - After the successful run, you'll see sth like:
> "After running. Worked 94 units, with max 3 (requested 3) threads"
		
