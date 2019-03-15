# TDT4237-2019-group9


### Local setup

Clone this repo to the folder /srv/www-data/group09/.

If you wish, you may place it anywhere, but be sure to edit `nginx-configuration-file` as 
well as `group09.service` to reflect this change.

`git clone git@github.com:simenbkr/tdt4237-2019-group09.git /srv/www-data/group09`

Edit the setup.sh file to contain your correct `DOMAIN` and `PORT`, then run it (tested on Ubuntu18.04.02 LTS)

`./setup.sh`


### Possible issues with setup

Make sure that www-data has read/write access to `sec/db.sqlite3`, as well as read access to all files in the
directory.

Make sure that the domain is configured correctly. If unable to login, this may be due to not having the correct
domain set, or because of stale sessions. Run `source venv/bin/activate && python sec/manage.py clearsessions` to
fix this.

