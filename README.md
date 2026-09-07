# Z3apps
Apps made for the RG35xx Family

Might work on other handhelds too, Output uses linux framebuffer so it is compatible with any linux installation.
The framework is robust and modular, and can be used to build further apps. Feel free to contribute or fork this repository to make your own apps. Dont foget to give credit though!

## Installation/Updating The App

1. Copy the [install-Z3apps.sh](https://github.com/Z3R0C1PH3R/Z3apps/releases/latest/download/install-Z3apps.sh) file into your Roms/APPS folder and run it from the APPS menu after making sure that you are on the latest firmware(tested on 240822), the **WIFI is connected**, the **correct time** is set in settings.
3. After a few minutes your device would restart which means the install/update was successful, you may remove the install-Z3apps.sh file. If it doesnt restart and just exits then the install probably failed, check the log files.

NOTE: The app uses a default API Key, but it has a limited Quota so the app might not work then, To fix this, you can make your own YouTube API Key and place it in the Roms/APPS/Z3apps/youtube-api-v3.key file after step 1. Refer [Step By Step Guide to Generate a Key](https://github.com/Z3R0C1PH3R/Z3apps/wiki/Adding-your-own-API-Key).

## Usage

1. You can use the YouTube-Z3 app in the APPS menu to start the YouTube Search, a keyboard pops up
2. Use the Dpad to navivgate around, press A to enter the character.
3. Select the ✓ button to continue, The search result window opens where you can select the video you like, use the Left and Right buttons on the Dpad to see details about the different results and press A on any of them to play that video, Press B to go back.
4. While the video is playing you have the following controls:

| Button          | Function                      |
|-----------------|-------------------------------|
| A               | Pause/Play                    |
| B               | Go Back                       |
| X               | Mute/Unmute                   |
| Y               | Show Progress                 |
| Dpad Right/Left | Seek 10s forward or backwards |
| Dpad Up/Down    | Control Volume by 10%         |
| Volume +/-      | Control Volume by 2%          |
| Select          | Go to start of video          |
| Start           | Go to end of video            |
| L1/R1           | Seek 10% forward or backward  |
| Menu            | Exit                          |

Enjoy :)

## Recent Changes (v0.3)

1. No numpy, and no pip installs at all. Everything the app needs is already on the stock firmware, so installing is much faster and no longer fails when pip does.
1. The installer shows its progress on screen from the very beginning instead of after the dependencies are done.
1. Drawing is done with plain byte writes to the framebuffer, pixel for pixel the same as before.

## Older Changes (v0.2)

1. Installation Script now Displays progress.
1. UI is much faster (Using numpy)


## Older Changes (v0.1)
   
1. B Works as a back button now.
1. Fixed video stuck on buffering bug.
1. Thumbnails were added.
1. Fixed bugs (blank screen sometimes when started).
1. Added Loading and Searching screens.

## Known Issues

~1. Live streams take really long to load and then freeze up.~ (Seems to be fixed after the latest update)

##### If you like my work and want to say thanks, or encourage me to do more, you can [buy me a coffee](https://buymeacoffee.com/z3r0c1ph3r) or a [ko-fi!](https://ko-fi.com/z3r0c1ph3r)
