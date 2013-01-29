# CLW's Mailstore

Campbell-Lange Workshop
January 2013

An overview to this project can be found in README.md in the directory
above this document.

This document sets out specifically how each part of Mailstore works and
how it is configured.

## Process of operation

First, a listing is provided of what happens to a single example email:

1. The email is received by Exim
2. If the email is accepted to the `acl_check_data` ACL check, it's
   headers will be recorded in the mailstore Postgresql database in the
   'log' table.
3. An Exim router copies the email to an Exim transport  
4. An Exim transport stores the email on disk in a unique file under a
   specified `mailstore` directory in a subdirectory with today's date
   in YYYY-MM-DD format. This is called "saving to the mailstore pool".
5. A Python checksumming programme sweeps the mailstore and update's the
   record for the email with the sha1sum of the file.
6. A shell auditing script ensures that the email (unless it is one of
   several failure states) is on disk, is in the database and has a
   checksum
7. A shell delete script removes the mail file from the pool when it is
   older than a specified period of time, say 60 days.
8. A shell script backs up and audits a database backup dump with the
   email record in it.
 
## Specific configuration steps

The following steps are required to set up the above process:

### Database

In this example, Postgresql is used, although other SQL databases or
SQLite can be used.

Please view `../db/schema.sql`. This sets out the structure of the `log`
table and also an optional `oversizemail` table. These can be simply
loaded into a new database by logging in and including the schema file.

E.g:

    (postgres) psql template1
    (postgres) # create user mailuser password '<password>';
    (postgres) # create database mailstore owner mailuser;
    (postgres) # \q

    # edit /etc/postgresql/<version>/main/pg_hba.conf with suitable
    # permissions

    psql -d mailstore -U mailuser
    # enter password
    mailstore=> \i schema.sql

### Exim

Please view the file `../exim/exim.txt`. This shows how configuration
blocks can be interjected into an Exim configuration. Such configuration
blocks can be easily set out into separate files and incorporated as
part of a split configuration arrangement such as the one used by the
exim4-daemon-heavy package in Debian.

Important aspects of the configuration include:

* The database connection is configured on line 7.
* On line 12 the SQL used for logging is set out
* On line 95 the header log call is made
* On line 120 and following the shadow router is defined
* On line 138 and following the shadow transport is defined

Various variables such as `CLW_SHADOWDIR` are used in some of the
configuration and need to be defined at the outset. These have not been
included in the header of the exim.txt file to keep it concise.

### Hash creation

The `../scripts/mailstore_summer.py` script is used to iterate over
files in the mailstore *pool* and to update the appropriate records in
the database with the calculated sha1sum. It does this by checking the
database with records with a false `b_processed` flag and then looking
to find the related file on the file system.

### Auditing

The audit process scans the Exim log file (in this example
`/var/log/exim4/mainlog.2.gz` is used, which is the log file from 2 days
previously) for mail unique ids to use for auditing. On line 29 a rather
simplistic pattern for excluding some ids from the audit is used,
including those related to a long retry time or marked as spam, amongst
others.

The script then checks that the id extracted in this way from the Exim
logs exists in both the database and on disk. It then checks if there
are any errors, and can be configured to post the results into a
monitoring system or email.

### Deletion of old email, database backup

The script `../scripts/mailpool_delete.sh` is used to -- very simply --
delete old mail files in the pool when their mtime is greater than a
certain amount.

The script `../scripts/db_backup.sh` can be used to dump postgres
databases reliably. Note that the database in question needs a schema
called audit with a table called audit, with a field tdata (DATE) for
this to operate.




