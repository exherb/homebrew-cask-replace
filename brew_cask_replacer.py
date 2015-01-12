#!/usr/bin/env python
# coding=utf-8

import sys
import os
import argparse
import commands
import urllib2
import json
import string
from send2trash import send2trash

try:
    input = raw_input
except NameError:
    pass

_CASKS_HOME = 'http://raw.github.com/caskroom/homebrew-cask/master/Casks/'
_PROPERTY_NAMES = ['url', 'homepage', 'name', 'version', 'app', 'pkg']
_DIGITAL_TO_ENGLISH_ = {
    0: 'zero',
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine'
}


def is_installed_by_appstore(application_path):
    cmd = 'codesign -dvvv "{0}"'.format(application_path)
    output = commands.getoutput(cmd)
    return output.find('Authority=Apple Mac OS Application Signing') > 0


def format_application_name(application_name):
    name = '-'.join([x for x in application_name.split()]).lower()
    if name[0].isdigit():
        name = _DIGITAL_TO_ENGLISH_[int(name[0])] + name[1:]
    return name.strip(string.digits)


def replace_application_in(applications_dir,
                           always_yes=False,
                           skip_app_from_appstore=True):
    ignores = set()
    ignore_file_path = os.path.join(os.path.dirname(__file__), 'ignore.txt')
    if os.path.exists(ignore_file_path):
        with open(ignore_file_path, 'r') as f:
            for line in f:
                if not line:
                    continue
                if line[0] == '#':
                    continue
                ignores.add(line.strip())
    not_founded = []
    installed_failed = []
    send2trash_failed = []
    applications = os.listdir(applications_dir)
    for application in applications:
        if application in ignores:
            continue
        application_path = os.path.join(applications_dir, application)
        if skip_app_from_appstore and\
           is_installed_by_appstore(application_path):
            print('Skip {0} from Appstore'.format(application))
            continue
        application_name, ext = os.path.splitext(application)
        if ext.lower() != '.app':
            continue

        application_name = format_application_name(application_name)
        try:
            cask_url = _CASKS_HOME + application_name + '.rb'
            application_info_file = urllib2.urlopen(cask_url, timeout=3)
        except Exception as e:
            not_founded.append(application)
            if isinstance(e, urllib2.HTTPError):
                if e.code == 404:
                    continue
            print('Get {0} info failed with {1}'.format(application,  e))
            continue
        application_info = {}
        for line in application_info_file:
            line = line.strip()
            key_value = line.split()
            if len(key_value) != 2:
                continue
            key = key_value[0]
            if key not in _PROPERTY_NAMES:
                continue
            application_info[key] = key_value[1].strip('\'\":')
        print('{0} -> {1}'.format(application, json.dumps(application_info,
                                  indent=4, separators=(',', ': '))))
        if not always_yes:
            replace_it = input('Replace It(Y/n):')
            replace_it = replace_it.lower()
            if len(replace_it) > 0 and replace_it != 'y' and\
               replace_it != 'yes':
                continue
        status = os.system('brew cask install {0}'.format(application_name))
        if status != 0:
            installed_failed.append(application)
        else:
            try:
                send2trash(os.path.join(applications_dir, application))
            except Exception as e:
                send2trash_failed.append(os.path.join(applications_dir,
                                                      application))
    for x in not_founded:
        print('Not replaced: {0}'.format(x))
    for x in installed_failed:
        print('Installed failed: {0}'.format(x))
    for x in send2trash_failed:
        print('Send to trash failed: {0}'.format(x))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('appdir', nargs='?', default='/Applications',
                        help='''the applications directory to search
                        (/Applications by default)''')
    parser.add_argument('-y', '--always-yes', action='store_true',
                        help='replace all with homebrew-cask')
    parser.add_argument('-f', '--include-appstore', action='store_true',
                        help='include apps in the Mac App Store')
    args = parser.parse_args(argv)
    applications_dir = args.appdir
    always_yes = args.always_yes
    skip_app_from_appstore = not args.include_appstore
    replace_application_in(applications_dir, always_yes,
                           skip_app_from_appstore)


if __name__ == '__main__':
    main(sys.argv[1:])
