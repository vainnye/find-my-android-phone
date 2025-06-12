# A very simple script to track your phone using Google Find My Device

- it logs in db.json the phone location every hour or every 5 minutes if the phone location changes.
- if location changes, this script will play an alarm sound to alert you that your phone has moved. Very usefull if you lost your phone or if it was stolen and you are sleeping atm ahah.

> /!\ Make sure you didn't activate 2FA on your Google account, otherwise it won't work. Especially with passkey 2FA

## dependencies

download dependencies in requirements.txt.

```sh
python -m venv .venv

# then activate the environment with on of the scripts in ./.venv./Scripts/

pip install -r requirements.txt
```

## setting up and running the script

first, you need to **download the "Chrome for Testing" browser** and set its path "CFT_BIN_PATH"
> You can download it from here: <https://github.com/GoogleChromeLabs/chrome-for-testing?tab=readme-ov-file>

btw this script will automatically download the ChromeDriver for you (using webdriver-manager python library). (it is anoter thing required in addition to Chrome for Testing and Selenium)

then you need to **create a *new* Chrome profile** for this script:
    1. Open Chrome for Testing
    2. click on the profile icon in the top right corner then click on manage chrome profiles
    3. create a NEW profile, DO NOT use the "Default" profile
    4. log in to your Google account in this new profile

go to the url chrome://version/ and copy the end of "Profile Path" value withut the user data directory, it should look like this: "Profile 1"
**set CFT_PROFILE_NAME** to this value

if necessary **change CFT_BIN_PATH** value

**set CFT_USER_DATA_PATH** to the user data directory of your Chrome for Testing profile, it should look like this: r"C:\Users\myself\AppData\Local\Google\Chrome for Testing\User Data"

configure the *phone name* and *id* in the main function.

change the *phone_url* if necessary (it is the url of the Find my Device page showing your phone on the map), for me it was: `"https://www.google.com/android/find/?login=&device=0&rs=1"`

**Now you can run it!**

if the page asks to enter your phone PIN, you will get a prompt in the console

> Hope you didn't get your phone stolen too :'(
