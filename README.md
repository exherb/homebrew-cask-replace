# homebrew-cask--replacer

use homebrew cask to replace installed apps

![screenshot](screenshot.png)

## usage

```bash

pip install -r requirements.txt
python brew_cask_replacer.py

```
## how it works

* check is {application} from Appstore [-f turnoff]
* check http://raw.github.com/phinze/homebrew-cask/master/Casks/{application} is exist
* print application info and be sure you want to replace it with brew cask [-y turnoff]
* install application using 'brew cask install {application}'
* send {application_path} to trash (may fail)
