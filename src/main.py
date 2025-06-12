from db import Phone
from tracker import DeviceTracker
import logging
logger = logging.getLogger(__name__)

'''
A very simple script to track your phone using Google Find My Device.
it logs in db.json the phone location every hour or every 5 minutes if the phone location changes.
if location changes, this script will play an alarm sound to alert you that your phone has moved, very usefull if you lost your phone or if it was stolen adn you are sleeping ahah.

Make sure you didn't activate 2FA on your Google account, otherwise it won't work. Especially with passkey 2FA

first, you need to download the "Chrome for Testing" browser and set its path "CFT_BIN_PATH"
    You can download it from here: https://github.com/GoogleChromeLabs/chrome-for-testing?tab=readme-ov-file
btw this script will automatically download the ChromeDriver for you. (it is anoter thing required in addition to Chrome for Testing and Selenium)

then you need to create a new Chrome profile for this script:
1. Open Chrome for Testing
2. click on the profile icon in the top right corner then click on manage chrome profiles
3. create a NEW profile, DO NOT use the "Default" profile
4. log in to your Google account in this new profile

go to the url chrome://version/ and copy the end of "Profile Path" value withut the user data directory, it should look like this: "Profile 1"
set CFT_PROFILE_NAME to this value

if necessary change CFT_BIN_PATH value

set CFT_USER_DATA_PATH to the user data directory of your Chrome for Testing profile, it should look like this: r"C:\Users\myself\AppData\Local\Google\Chrome for Testing\User Data"

configure the phone name and id in the main function.

configure dependencies in requirements.txt, then run this script with Python 3.10 or higher.
```sh
python -m venv .venv

# then activate the environment with on of the scripts in ./.venv./Scripts/

pip install -r requirements.txt
```

'''


CFT_PROFILE_NAME: str = None # example: "Profile 1" # experience tells me that the "Default" profile folder doesn't work well, **you should CREATE A NEW CHROME PROFILE**

CFT_BIN_PATH: str = None # example: r"C:\Program Files\Google\Chrome for Testing\137.0.7151.68\chrome.exe"
CFT_USER_DATA_PATH: str = None # example: r"C:\Users\myself\AppData\Local\Google\Chrome for Testing\User Data"


def main():
    my_phone = Phone(
        name_id="an id for the logs in db.json", # in case your phone changes name in Google Find My Device, it is identified by an Id in db.json
        fmp_name="your phone name here as in Google Find my Device"
        )
    
    tracker = DeviceTracker(
        phone=my_phone,
        cft_bin_path=CFT_BIN_PATH,
        cft_user_data_path=CFT_USER_DATA_PATH,
        profile_folder=CFT_PROFILE_NAME,
        phone_url="https://www.google.com/android/find/?login=&device=0&rs=1"
        )
    
    # by default the tracker refresh every 1 hour, if it detects a change in the phone location, it will temporarily refresh every 5 minute
    # every location change is logged in db.json file and in the console
    
    # settings can be adjusted to your liking in tracker.py
    tracker.run()
    

if __name__ == "__main__":
    main()