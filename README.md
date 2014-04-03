# homebrew-cask-replacer

use homebrew cask to replace installed apps

![screenshot](screenshot.png)

## usage

```bash

pip install -r requirements.txt
python brew_cask_replacer.py

```
## how it works

* skip {application} from Appstore [-f turnoff]
* check http://raw.github.com/phinze/homebrew-cask/master/Casks/{application} is exist
<<<<<<< HEAD
* print application info and be sure you want to replace it with brew cask [-y turnoff]
=======
* print application info and check if you want to replace it with brew cask [-y yes to all]
>>>>>>> fd05faf2bc88c12348ea1b62a8722a933c386c79
* install application using 'brew cask install {application}'
* send {application_path} to trash (may fail)
