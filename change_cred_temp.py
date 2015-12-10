#!/usr/bin/env python
#TODO Add error messaging throughout that goes out into the email in case of failure

import smtplib
from email.mime.text import MIMEText
import subprocess
import argparse
import sys
import string
import random
import os
import datetime

import pexpect
from dbconnect import DBConnect


CFG_NFO = "/home/{0}/.cfgnfo"
FILE_PATH = os.path.realpath(__file__)

# Will change
EMAIL_FROM = 'espa@espa.cr.usgs.gov'
EMAIL_TO = ['klsmith@usgs.gov']
EMAIL_SUBJECT = "LSRD - Auto-credential {0}"


class CredentialException(Exception):
    pass


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
    """
    Send out an email to give notice of success or failure

    :param sender: who the email is from
    :type sender: string
    :param recipient: list of recipients of the email
    :type recipient: list
    :param subject: subject line of the email
    :type subject: string
    :param body: success or failure message to be passed
    :type body: string
    :return:
    """
    # This does not need to be anything fancy as it is used internally,
    # as long as we can see if the script succeeded or where it failed
    # at, then we are good to go
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    smtp = smtplib.SMTP("localhost")
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()


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
    At least 1 lower case, 1 upper case, 1 number, and 1 special

    :param length: length of string
    :type length: int
    :return: password string
    """

    char_ls = [string.ascii_lowercase,
               string.ascii_uppercase,
               string.digits,
               string.punctuation]

    chars = ''.join(char_ls)

    i = 0
    while i < len(char_ls):
        i = 0

        paswrd = ''.join(random.SystemRandom().choice(chars) for _ in range(length))

        for char_set in char_ls:
            if set(char_set).intersection(set(paswrd)):
                i += 1

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
    with DBConnect(**db_info) as db:
        db.execute(sql_str)
        db.commit()


def current_pass(db_info):
    """
    Retrieves the current password from the  database

    :param db_info: database connection information
    :type db_info: dict
    :return: exception message
    """

    sql_str = "select value from ordering_configuration where key = 'landsatds.password'"

    with DBConnect(**db_info) as db:
        db.select(sql_str)
        curr = db[0]

    return curr


def update_cron(user, freq=60, backdate=True):
    """
    Updates the crontab to run this script again with the same user and frequency

    :param user: user to update password for
    :type user: string
    :param freq: number days to set the next cron job for
    :type freq: int
    :param backdate: change the password ahead of time
    :type backdate: bool
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


def change_pass(old_pass):
    """
    Update the password in the linux environment

    :param old_pass: previous password
    :type old_pass: string
    :param new_pass: new password
    :type new_pass: string
    :return: exception message if fail
    """
    #TODO Process needs to be verified, especially the regex portions
    child = pexpect.spawn('passwd')
    child.expect('*[Pp]assword: ')
    child.sendline(old_pass)
    i = child.expect(['New password: ', '*Password incorrect: try again*'])

    if i == 1:
        raise CredentialException('Password retrieved from DB is incorrect')

    i = 1
    new_pass = gen_password()
    while i:
        child.sendline(new_pass)
        i = child.expect(['Retype new password: ', 'BAD PASSWORD*'])
        if i:
            new_pass = gen_password()

    child.sendline(new_pass)

    return new_pass


def run():
    """
    Change the password for a user and set up a cron job
    to change it again based on the frequency
    """
    # Since this is mostly a fire and forget script it needs
    # broad exception handling so whatever traceback gets generated
    # is sent out in the email
    msg = ''
    success = ''
    try:
        username, freq = arg_parser()
        cfg_info = get_cfg(username)
        old_pass = current_pass(cfg_info)
        new_pass = change_pass(old_pass)
        update_db(new_pass, cfg_info)
        update_cron(username, freq)
        msg = 'User: {0} password has been updated'.format(username)
        success = 'Successful'
    except Exception as e:
        msg = e
        success = 'Failure'
    finally:
        send_email(EMAIL_FROM, EMAIL_TO, EMAIL_SUBJECT.format(success), msg)


if __name__ == '__main__':
    run()
