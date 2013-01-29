# CLW Mailstore

Campbell-Lange Workshop's Mailstore is a way of copying incoming (and
potentially, outgoing) email messages. _Mailstore_ is more of an
approach than a specific technology as it uses a set of simple
procedures to achieve the following:

For each email moving in (and out, if desired) of the external SMTP
boundary:

* store a copy of the email header in an SQL database keyed against the
  SMTP daemon's mail ID (hereafter called `key`).
* store a copy of the email file in a specified location, in a directory
  named with the current date, under a filename with the unique key. The
  specified location can be considered the `store`.
* periodically generate md5sums or sha1sums of emails in the store to
  record against the associated row in the SQL database, using the key
  for association
* check the database against the SMTP logs for missing hashes
* delete email files from the store after a configurable period of time

Mailstore has been made open source with the assistance of Hopkins
Architects.

## Uses of Mailstore

Mailstore is useful for the following use cases, amongst others:

* easily read and resend/inject recently deleted email
* easily back up email using filesystem backup tools
* rapidly find general details of email correspondence using header
  information
* target retrievals of emails precisely when required for legal and
  similar purposes
* assuming the SQL database is backed up can also provide a useful
  verification of the veracity of a stored email file for legal and
  similar purposes.

Mailstore isn't likely to be useful for retrieving a user's entire
mailbox as it follows the flow of SMTP traffic over time. It is better
considered as an SMTP record for an entire organisation.

## Docs and Software used

Documentation is set out in the `docs` folder. 

Mailstore uses Exim, Postgresql and Python, together with some bash
scripts.

## Licence

This is released under the GPLv3.




