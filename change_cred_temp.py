#!/usr/bin/env python
#TODO Add error messaging throughout that goes out into the email in case of failure

import smtplib
import subprocess
import argparse
import sys
import string
import random
import os
import datetime

import psycopg2
import pexpect


CFG_NFO = "/home/{0}/.cfgnfo"
FILE_PATH = os.path.realpath(__file__)

# Will change
email_from = 'espa@espa.cr.usgs.gov'
email_to = ['klsmith@usgs.gov']
email_subject = "LSRD - Auto-credential changing"


class DBConnect(object):
    """
    Class for connecting to a postgresql database using a with statement
    """

    def __init__(self, dbhost='', db='', dbuser='', dbpass='', dbport=3306, autocommit=False):
        self.conn = psycopg2.connect(host=dbhost, database=db, user=dbuser,
                                     password=dbpass, port=dbport)
        try:
            self.cursor = self.conn.cursor()
        except psycopg2.Error:
            raise

        self.autocommit = autocommit
        self.fetcharr = []

    def execute(self, sql_str):
        try:
            self.cursor.execute(sql_str)
        except psycopg2.Error:
            raise

        if self.autocommit:
            self.commit()

    def select(self, sql_str):
        self.cursor.execute(sql_str)

        try:
            self.fetcharr = self.cursor.fetchall()
        except psycopg2.Error:
            raise

    def commit(self):
        try:
            self.conn.commit()
        except psycopg2.Error:
            raise

    def rollback(self):
        self.conn.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def __len__(self):
        return len(self.fetcharr)

    def __iter__(self):
        return iter(self.fetcharr)

    def __getitem__(self, item):
        if item >= len(self.fetcharr):
            raise IndexError
        return self.fetcharr[item]

    def __del__(self):
        self.cursor.close()
        self.conn.close()

        del self.cursor
        del self.conn


def get_cfg(user):
    """
    Retrieve the configuration information from the .cfgnfo file
    Will need to be made more robust if the file changes
    :return: dict
    """
    cfg_info = {}
    with open(CFG_NFO.format(user), 'r') as f:
        next(f)
        for line in f:
            key, val = line.split('=')
            cfg_info[key] = val

    return cfg_info


def send_email(sender, recipient, subject, body):

    smtp = smtplib.SMTP("localhost")
    smtp.sendmail(sender, recipient, body.as_string())
    smtp.quit()
    pass


def arg_parser():
    """
    Process the command line arguments
    """
    parser = argparse.ArgumentParser(description="Changes credentials supplied for\
     -u/--username and updated Django configuration table for ESPA admin site.  Right now it\
      needs to run on the same host where the postgres database lives for ESPA.  This script\
       will also auto-update a crontab for the user running this")

    parser.add_argument("-u", "--username", action="store", nargs=1, dest="username",
                        choices=['espa', 'espadev', 'espatst'],
                        help="Username to changed credentials for (e.g. [espa|espadev|espatst])")
    parser.add_argument("-f", "--frequency", action="store", type=int, default=60,
                        dest="frequency",
                        help="Frequency (in days) to change the following credentials")

    args = parser.parse_args()

    if len(sys.argv) - 1 == 0:
        parser.print_help()
        sys.exit(1)

    return args.username, args.frequency


def gen_password(length=16):
    """
    Generate a random string of characters to use as a password

    :param length: length of string
    :type length: int
    :return: password string
    """
    #TODO add check to make sure it meets requirements

    char_ls = [string.ascii_lowercase,
               string.ascii_uppercase,
               string.digits,
               string.punctuation]

    chars = ''.join(char_ls)
    paswrd = ''.join(random.SystemRandom().choice(chars) for _ in range(length))

    return paswrd


def update_db(passwrd, db_info):
    """
    Update the database with the new password

    :param passwrd: new password
    :type passwrd: string
    :param db_info: database connection information
    :type db_info: dict
    :return: exception message
    """
    sql_str = "update ordering_configuration set value = '{0}' where key = '{1}'".format(passwrd, 'landsatds.password')
    try:
        with DBConnect(**db_info) as db:
            db.execute(sql_str)
            db.commit()

        return None
    except Exception as e:
        return e


def current_pass(db_info):
    """
    Retrieves the current password from the  database

    :param db_info: database connection information
    :type db_info: dict
    :return: exception message
    """

    sql_str = "select value from ordering_configuration where key = 'landsatds.password'"

    try:
        with DBConnect(**db_info) as db:
            db.select(sql_str)
            curr = db[0]

        return curr
    except Exception as e:
        return e


def update_cron(user, freq=60, backdate=True):
    """
    Updates the crontab to run this script again with the same user and frequency

    :param user: user to update password for
    :type user: string
    :param freq: number days to set the next cron job for
    :param backdate:
    :return:
    """
    chron_file = 'chron.tmp'

    if backdate:
        freq -= 2

    new_date = datetime.date.today() + datetime.timedelta(days=freq)

    cron_str = "00 05 {0} {1} * /usr/local/bin/python {2} -u {3} -f {4}".format(new_date.month,
                                                                                new_date.day,
                                                                                FILE_PATH,
                                                                                user,
                                                                                freq)

    crons = subprocess.check_output(['crontab', '-l']).split('\n')

    for idx, line in enumerate(crons):
        if __file__ in line:
            crons[idx] = cron_str

    with open(chron_file, 'w') as f:
        f.write('\n'.join(crons))

    subprocess.call(['crontab', chron_file, '&&', 'rm', chron_file])


def change_pass(old_pass, new_pass):
    """
    Update the password in the linux environment

    :param old_pass: previous password
    :type old_pass: string
    :param new_pass: new password
    :type new_pass: string
    :return: exception message if fail
    """
    #TODO Process needs to be verified, especially the regex portions
    #TODO Needs to return new pass in case it had to generate a new one

    child = pexpect.spawn('passwd')
    child.expect('*[Pp]assword: ')
    child.sendline(old_pass)
    i = child.expect(['New password: ', '*Password incorrect: try again*'])

    if i == 1:
        return 'Password retrieve from DB is incorrect'

    i = 1
    while i:
        child.sendline(new_pass)
        i = child.expect(['Retype new password: ', 'BAD PASSWORD*'])
        if i:
            new_pass = gen_password()

    child.sendline(new_pass)


def run():
    # Written this way for ease of following the process flow in the future
    # and it doesn't really need to be anything fancy

    #TODO Add verification between steps and error message building for emailing
    username, freq = arg_parser()
    cfg_info = get_cfg(username)
    old_pass = current_pass(cfg_info)
    new_pass = gen_password()
    change_pass(old_pass, new_pass)
    update_db(new_pass, cfg_info)
    update_cron(username, freq)


if __name__ == '__main__':
    run()
