#!/bin/bash

# Campbell-Lange Workshop Ltd
# Started by Veselin Kantsev
# Backup a mailstore database and audit it to check it is up-to-date

#output file location
BCKP=/mailstore/
#report file
RPT=/tmp/db_backup.rpt
ERR=/tmp/db_backup.err

rm $RPT 2>/dev/null
rm $ERR 2>/dev/null

for DB in clwmail ; do
# Insert the audit line into the database
 sudo -u postgres psql -d $DB -c "update audit.audit set tdate = current_date;" >/dev/null

# Dump the DB
 sudo -u postgres pg_dump $DB > $BCKP$DB.sql
  if [ $? -eq 0 ]; then
   echo "Database \"$DB\" backed up to \"$BCKP\" at `date '+%H:%M %d/%m/%Y'`" >>$RPT
  else
   echo "Backup of database \"$DB\" failed! PLEASE CHECK!" | tee -a $ERR >> $RPT
   continue
  fi 
 
 # Audit the DB
 AUDIT=`grep -A1 "COPY audit (tdate) FROM" $BCKP$DB.sql | tail -n1`
 DATE=`date +%Y-%m-%d`
  if [ $DATE == $AUDIT ]; then
   echo "AUDIT: SUCCESS! Audit date matches dump date" >> $RPT
  else
   echo "AUDIT: FAILED! Please check dumps" | tee -a $ERR >> $RPT
  fi

 # Send results to monitoring
 MONITOR="/home/it/bin/monitor/clwmonitor.py -c /home/it/bin/monitor/config/`hostname`.yaml"
  if [ -s $ERR ];
  then
  # report ok
  # cat $ERR | $MONITOR -s 25:00:00 -n "DBBKP" -r 1
  else
  # report failure
  # echo "Database $DB backup and audit for `hostname` completed successfully" | $MONITOR -s 25:00:00 -n "DBBKP" -r 0
  fi
done
