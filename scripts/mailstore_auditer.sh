#!/bin/bash

# Campbell-Lange Workshop Ltd
# Started by Mark Adams
# Mailstore audit : check all Exim mail other than those explicitly
# excluded exists on disk and in the mailstore SQL log

# Cronjob to be scheduled as follows:
# Mailstore Audit
# 00 07 * * * /root/bin/mailstore_auditer.sh >/dev/null

MAILSTORE=/mailstore/
DB=<dbname>
DBUSER=<username>
TMP1=/tmp/mailstoreaudit_tmpfile1
TMP2=/tmp/mailstoreaudit_tmpfile2
# MONITOR="/home/it/bin/monitor/clwmonitor.py -c /home/it/bin/monitor/config/`hostname`.yaml"
FAILLOG=/tmp/mailstoreaudit_fail.log

# clear the fail log
> $FAILLOG

# Send all spam, bounces, retry...exceeded and frozen messages then list
# ID's in temp file
/bin/zgrep "retry timeout exceeded\|SPAM\|U=Debian-exim\|U=mailusers\|frozen\|U=it\|U=root" /var/log/exim4/mainlog.2.gz | awk {'print $3'} > $TMP1

# exclude the mails in the first temp file to generate id's to check in
# a new temp file
/bin/zgrep -v -f $TMP1 /var/log/exim4/mainlog.2.gz | grep "Completed" | awk {'print $3'} > $TMP2

# Check they exist in the mailstore
for II in `cat $TMP2`;
do
/usr/bin/find $MAILSTORE -type f -name $II
    if [ $? -eq 1 ];
        then
        echo "ID $II does not exist in mailstore" >> $FAILLOG
        else
        echo "OK"
    fi
done

# Check they exist in the DB
for III in `cat $TMP2`;
do
sudo -u postgres /usr/bin/psql clwmail -c "select t_sha1sum from log where t_message_id='$III'" | grep "1 row"
    if [ $? -eq 1 ];
        then
        echo "ID $III missing sha1sum" >> $FAILLOG
        else
        echo "OK"
    fi
done

# See if there are any errors, then send results to monitoring
if [ -s $FAILLOG ];
    then
	# send ok to mail or monitoring
    # cat $FAILLOG | $MONITOR -s 25:00:00 -n "MAILSTORE" -r 1
    else
	# send failure message to mail or monitoring
    # echo "Mailstore audit completed successfully" | $MONITOR -s 25:00:00 -n "MAILSTORE" -r 0
fi;
exit 0
if
