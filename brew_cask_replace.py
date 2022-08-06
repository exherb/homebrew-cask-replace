#!/usr/bin/env python
# coding=utf-8
import sys
import os
import argparse
import commands
import urllib2
import subprocess
from send2trash import send2trash

try:
    input = raw_input
except NameError:
    pass
_CASKS_HOME = 'http://raw.github.com/caskroom/homebrew-cask/master/Casks/'


def parse_ignores(ignore_file_path):
    ignores = set()
    if os.path.exists(ignore_file_path):
        with open(ignore_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line[0] == '#':
                    continue

                ignores.add(line)
    return ignores

def parse_ignorescask(ignorecask_file_path):
    ignorescask = set()
    if os.path.exists(ignorecask_file_path):
        with open(ignorecask_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line[0] == '#':
                    continue

                ignorescask.add(line)
    return ignorescask


def is_installed_by_appstore(application_path):
    cmd = 'codesign -dvvv "{0}"'.format(application_path)
    output = commands.getoutput(cmd)
    return output.find('Authority=Apple Mac OS Application Signing') > 0


def generate_cask_token(application_path, application_name):
    cask_token = None
    p = subprocess.Popen(
        ['brew', '--repository'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    brew_location, err = p.communicate()
    brew_location = brew_location.strip()
    if len(brew_location):
        p = subprocess.Popen(
            [
                brew_location +
                '/Library/Taps/homebrew/' +
                'homebrew-cask/developer/bin/' +
                'generate_cask_token',
                application_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = p.communicate()
        for line in out.split('\n'):
            key, value = line.split(':')
            key = key.strip()
            if key == 'Proposed token':
                cask_token = value.strip()
                break

    if not cask_token:
        cask_token = '-'.join([x for x in application_name.split()]).lower()
    return cask_token


def replace_application_in(
    applications_dir, always_yes=False, skip_app_from_appstore=True
):
    os.system('brew list --cask > ignorecask.txt')
    ignores = parse_ignores(os.path.join(os.path.dirname(__file__), 'ignore.txt'))
    ignorescask = parse_ignorescask(os.path.join(os.path.dirname(__file__), 'ignorecask.txt'))
    not_founded = []
    installed_failed = []
    send2trash_failed = []
    try:
        applications = os.listdir(applications_dir)
        for application in applications:
            if application in ignores:
                continue

            application_path = os.path.join(applications_dir, application)
            if skip_app_from_appstore and is_installed_by_appstore(application_path):
                print('Skip {0} from Appstore'.format(application))
                continue

            application_name, ext = os.path.splitext(application)
            if ext.lower() != '.app':
                continue
            application_name = generate_cask_token(application_path, application_name)
            try:
                cask_url = _CASKS_HOME + application_name + '.rb'
                application_info_file = urllib2.urlopen(cask_url, timeout=3)
            except Exception:
                not_founded.append(application)
                continue

            application_info = application_info_file.read()

            cask = application_info[application_info.find("'")+1:].split()[0]
            caskapp = cask.strip('\'"')

            if caskapp in ignorescask:
                continue

            print('{0} -> {1}'.format(application, application_info))
            if not always_yes:
                replace_it = input('Replace It(Y/n):')
                replace_it = replace_it.lower()
                if len(replace_it) > 0 and replace_it != 'y' and replace_it != 'yes':
                    continue

                try:
                    send2trash(os.path.join(applications_dir, application))
                except OSError as e:
                    send2trash_failed.append(
                        os.path.join(applications_dir, application)
                    )
                    print('\n{0} replace failed \n'.format(application_name))
                else:
                    print('\n{0} successfully sent to trash, now reinstalling via brew \n'.format(application_name))
                    status = os.system('brew install --cask {0}'.format(application_name))
                    if status != 0:
                        installed_failed.append(application)
                        print(
                            '{0} brew installation failed. Please try to install using the command:\n"brew install --cask {0}".\nIf that fails please reinstall manually'.format(application_name)
                        )
                    else:
                        print('{0} successfully reinstalled with cask.\n'.format(application_name))
    finally:
        for x in not_founded:
            print('Not found: {0}'.format(x))
        for x in installed_failed:
            print('Installed fail: {0}'.format(x))
        for x in send2trash_failed:
            print('Send to trash fail: {0}'.format(x))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'appdir',
        nargs='?',
        default='/Applications',
        help='''the applications directory to search
                        (/Applications by default)''',
    )
    parser.add_argument(
        '-y', '--always-yes', action='store_true', help='replace all with homebrew-cask'
    )
    parser.add_argument(
        '-f',
        '--include-appstore',
        action='store_true',
        help='include apps in the Mac App Store',
    )
    args = parser.parse_args(argv)
    replace_application_in(args.appdir, args.always_yes, not args.include_appstore)


if __name__ == '__main__':
    main(sys.argv[1:])
