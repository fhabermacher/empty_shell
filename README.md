# empty_shell
## Prerequisites

1. Ubuntu 16.04 (this is where some of the code was written on)
2. python3 = python 3.5 (3.6 likely to not work)

## Setup
#### 1. Create System Environment Variable

`SAPO_TEST_DIR`

pointing to

`/home/<yourusername>/empty_shell`

i.e. the directory (without final slash /) where the app resides (with rw premission), i.e. with

*\<yourusername\>* = folder with your *empty_shell* clone

*Don't forget possible system restart for the system variable to be recognized*

#### 2. Set up virtualenv with its requirements etc.
Starting within the repo folder, e.g. `/home/<yourusername>/empty_shell`:
```
cd py
./setup.sh
```

## Launching
Again from the repo folder, e.g. `/home/<yourusername>/empty_shell`:
```	
cd py
source venv/bin/activate
./app.py
```
Then (ctrl-)click the indicated browser link (e.g. http://127.0.0.1:8050/) to open the app in the browser
	
Login credentials in browser app:
* User Name: test
* PW: yes


## Verifying current functionality remains intact after deployment

1. File upload
   - *Drag or Browse File(s)* fields must allow to add files
   - Files added, must become selectable in the respective Dropdown on the left
2. Cookie functionality must make the last selected file from be pre-selected after restarting the app
3. *Launch* button must be or become active: at latest few sec after opening app in brwoser, or else after clicking *Activate* button
4. **This is the *core* part** Click on *Launch* button must launch the simulation, running it for 10sec
   - You will see it progress in the text indication below the Launch button, right above the Plot button.
	 - After the successful run, you'll see sth like:
> After running. Worked 94 units, with max 3 (requested 3) threads
		
