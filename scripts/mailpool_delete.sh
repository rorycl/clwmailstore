#!/bin/bash

# Campbell-Lange Workshop Ltd.
# Simple script for deleting old mail in mailstore pools

# path to mailstore message pool
POOLS=/mailstore/
FIND=/usr/bin/find
# days to keep
DAYS=60

$FIND $POOLS -type f -mtime +${DAYS} -exec rm {} \;
$FIND $POOLS -depth -type d -empty -exec rmdir {} \;
