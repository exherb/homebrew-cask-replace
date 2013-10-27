#!/usr/bin/env python
# coding=utf-8

import sys
import os
import urllib2
import json
from send2trash import send2trash

_CASKS_HOME = 'http://raw.github.com/phinze/homebrew-cask/master/Casks/'
_PROPERTY_NAMES = ['url', 'homepage', 'version', 'link']

def collect_applications(applications_dir):
    applications = os.listdir(applications_dir)
    for application in applications:
        application_name, ext = os.path.splitext(application)
        if ext.lower() != '.app':
            continue
        application_name = application_name.lower()
        application_name = '-'.join(application_name.split())
        try:
            application_info_file = urllib2.urlopen(_CASKS_HOME + application_name + '.rb')
        except Exception, e:
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
            application_info[key] = key_value[1]
        print('{0} -> {1}'.format(application, json.dumps(application_info,
            indent=4, separators=(',', ': '))))
        replace_it = raw_input('Replace It(Y/n):')
        replace_it = replace_it.lower()
        if len(replace_it) > 0 and replace_it != 'y' and replace_it != 'yes':
            continue
        status = os.system('brew cask install {0}'.format(application_name))
        if status != 0:
            print('Install {0} fail'.format(application))
        send2trash(os.path.join(applications_dir, application))

def main():
    applications_dir = '/Applications'
    if len(sys.argv) > 1:
        applications_dir = sys.argv[1]
    collect_applications(applications_dir)

if __name__ == '__main__':
    main()
