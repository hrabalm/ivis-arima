#!/usr/bin/env fish

set DB ivislocal

curl -XDELETE 'localhost:9200/*' # Deletes ALL elastic search indices
set TABLES (sudo mysql $DB -e 'SHOW TABLES;' | awk '{ print $1 }' | grep -v '^Tables')

for table in $TABLES
	sudo mysql $DB -e "SET FOREIGN_KEY_CHECKS=0; DROP TABLE IF EXISTS $table; SET FOREIGN_KEY_CHECKS=1;"
end
