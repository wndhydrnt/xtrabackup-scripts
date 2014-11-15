#!/usr/bin/env python3

"""Xtrabackup script

Usage:
  backup-fs.py <repository> --user=<user> [--password=<pwd>] [--tmp-dir=<tmp>] [--log-file=<log>] [--backup-threads=<threads>] 
  backup-fs.py (-h | --help)
  backup-fs.py --version


Options:
  -h --help                   Show this screen.
  --version                   Show version.
  --user=<user>               MySQL user.
  --password=<pwd>            MySQL password.
  --tmp-dir=<tmp>             Temp folder [default: /tmp].
  --log-file=<log>            Log file [default: /tmp/backup.log].
  --backup-threads=<threads>  Threads count [default: 1].

"""
import datetime
import subprocess
from docopt import docopt
from system import *


def prepare_archive(repository_path):
    date = datetime.datetime.now()
    ts = date.strftime("%Y%m%d_%H%M")
    date_fmt = date.strftime("%Y%m%d")
    archive_name = 'backup_' + ts + '.tar.gz'
    archive_repository = repository_path + '/' + date_fmt
    archive_path = archive_repository + '/' + archive_name
    mkdir_p(archive_repository, 0o755)
    return archive_path


def exec_backup(arguments):
    if arguments['--password']:
        subprocess.check_call(['innobackupex', '--user=' + arguments['--user'],
                               '--password=' + arguments['--password'],
                               '--parallel=' + arguments['--backup-threads'],
                               '--no-lock',
                               '--no-timestamp',
                               arguments['--tmp-dir'] + '/backup'])
    else:
        subprocess.check_call(['innobackupex', '--user=' + arguments['--user'],
                               '--parallel=' + arguments['--backup-threads'],
                               '--no-lock',
                               '--no-timestamp',
                               arguments['--tmp-dir'] + '/backup'])


def exec_backup_apply(tmp_folder):
    subprocess.check_call(['innobackupex', '--apply-log', tmp_folder])


def exec_tar(tmp_folder):
    subprocess.check_call(['tar',
                           'cpfvz',
                           tmp_folder + '/backup.tar.gz',
                           '-C',
                           tmp_folder + '/backup', '.'])


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')
    # print(arguments)

    # Check for required binaries
    check_binary('innobackupex')
    check_binary('tar')

    # Check for backup repository existence
    check_folder(arguments['<repository>'])

    # Create tmp folder
    mkdir_p(arguments['--tmp-dir'], 0o755)

    # Prepare archive name and create timestamp folder in repository
    archive_path = prepare_archive(arguments['<repository>'])

    # Exec backup
    exec_backup(arguments)

    # Apply phasis
    exec_backup_apply(arguments['--tmp-dir'] + '/backup')

    # Exec tar
    exec_tar(arguments['--tmp-dir'])

    # Move backup from tmp folder to repository
    shutil.move(arguments['--tmp-dir'] + '/backup.tar.gz', archive_path)

    # Remove tmp folder
    shutil.rmtree(arguments['--tmp-dir'] + '/backup')

    exit(0)
