  The backup module implements the full functionality of creating backup copies of configurations, files, and databases for all instances managed by CLD. 

  The functionality allows you to independently determine the list of instances for backup, as well as determine the types of backups to be performed. In addition to a flexible management system, the user has the ability to set unique parameters, such as data for accessing databases, paths to backup directories, backup execution time, the number of backup copies to be stored, a list of files and extensions that should not be backed up.

  Backup is performed to a remote server, where the created copies are subsequently stored in accordance with the specified number of copies.
  The backup process is optimized so as not to create an increased load on the server.
  At the moment, the backup functionality of the following **database systems** has been implemented:
+ **MongoDB Backup**: flexible, customizable backup of databases of any size powered by MongoDB. The following options allow you to customize the MongoDB backup for your purposes:
  - `MONGO_HOST`: ip address of the server where the MongoDB database is located for backup
  - `MONGO_USER`: MongoDB user to backup
  - `MONGO_PASSWORD`: MongoDB user password
  - `KEEPLAST`: number of MongoDB copies to keep
  - `CRON`: backup task start time, the user can set any convenient backup start time.
  - `SERVER`: name of the server where the backup will be stored. By default, backups are performed to the first backup server in the list.
  - `SERVER_BACKUP_DIR`: directory on the backup server where completed backups will be stored. The default value is /backup

+ **ClickHouse Backup**: flexible custom backup of databases of any size managed by ClickHouse-Server. It has a similar set of parameters as MongoDB, but additionally implements the functionality of creating a new user in ClickHouse-Server to perform backups:
  - `CLICKHOUSE_USER`: the ClickHouse user that the backup will be performed with (most Clickhouse servers work without a password using the default user, we recommend that you protect yourself by limiting or deleting this user)
  - `CLICKHOUSE_PASSWORD`: ClickHouse user password
  - `KEEPLAST`: number of ClickHouse copies to keep
  - `CRON`: backup task start time, the user can set any convenient backup start time.
  - `SERVER`: name of the server where the backup will be stored. By default, backups are performed to the first backup server in the list.
  - `SERVER_BACKUP_DIR`: directory on the backup server where completed backups will be stored. The default value is /backup

+ **MySQL Backup**: flexible, customizable backup of databases of any size running MySQL. It has a similar set of parameters as MongoDB and ClickHouse, and also additionally implements the functionality of creating a new user in MySQL to perform backups. In addition, it is possible to perform local and remote backups:
  - `MYSQL_HOST`: external ip address of the MySQL server, specifying its backup will be performed remotely via mydumper, if remote backup is not possible (firewall \ nat), you can specify 127.0.0.1 (localhost) in this parameter - then the backup will be performed via SSH using mysqldump
  - `MYSQL_USER`: MySQL user with which the backup will be performed
  - `MYSQL_PASSWORD`: MySQL user password
  - `MYSQL_SOURCE`: ip address of the server from which the backup will be performed, the parameter can be commented out if a local backup is performed
  - `MYSQL_DATABASES`: list of MySQL databases to backup, to backup all databases, leave the parameter empty
  - `KEEPLAST`: number of MySQL copies to keep
  - `CRON`: backup task start time, the user can set any convenient backup start time.
  - `SERVER`: name of the server where the backup will be stored. By default, backups are performed to the first backup server in the list.
  - `SERVER_BACKUP_DIR`: directory on the backup server where completed backups will be stored. The default value is /backup

+ **PostgreSQL Backup**: flexible, customizable backup of databases of any size powered by PostgreSQL. The following options allow you to customize the PostgreSQL backup for your purposes:
  - `POSTGRE_HOST`: ip address of the server where the PostgreSQL database is located for backup
  - `POSTGRE_USER`: PostgreSQL user to backup
  - `POSTGRE_PASSWORD`: PostgreSQL user password
  - `KEEPLAST`: number of PostgreSQL copies to keep
  - `CRON`: backup task start time, the user can set any convenient backup start time.
  - `SERVER`: name of the server where the backup will be stored. By default, backups are performed to the first backup server in the list.
  - `SERVER_BACKUP_DIR`: directory on the backup server where completed backups will be stored. The default value is /backup

**Attention!** We recommend creating a separate database user for performing backups.
When creating a database backup configuration, heredoc is most often present, which allows you to generate commands to create a specified user. Once created, the heredoc data can be deleted as is no longer required for the backup script to work.

In addition to the database backup functionality, CLD implements convenient configuration and backup of configurations, files, and file directories. Similar to database backup - various options for fine-tuning the backup process are available for selection.
At the moment, configuration backups are available in `/etc/` as a whole, as well as backups of files at the specified path:

+ **ETC Backup**: backup of configuration files located in the `/etc/` directory as well as directories of variables specified in the parameters:
  - `DIR_LIST`: comma-separated list of configuration directories for backup. The parameter has a default value of `/etc/`
  - `EXCLUDE_LIST`: list of files, extensions or directories to exclude from the backup process. Files, directories and extensions will not be included in the backup. By default, the parameter is empty.
  - `KEEPLAST`: number of configuration copies to keep.
  - `CRON`: backup task start time, the user can set any convenient backup start time.
  - `SERVER`: name of the server where the backup will be stored. By default, backups are performed to the first backup server in the list.
  - `SERVER_BACKUP_DIR`: directory on the backup server where completed backups will be stored. The default value is /backup

+ **Files Backup**: backup files and entire file directories, allows you to quickly and conveniently configure the backup of the necessary elements:
  - `DIR_LIST`: comma-separated list of configuration directories for backup. If the variable is empty - the backup task will not be started, the backup will not be performed.
  - `EXCLUDE_LIST`: list of files, extensions or directories to exclude from the backup process. Files, directories and extensions will not be included in the backup. By default, the parameter is empty.
  - `KEEPLAST`: number of backup copies of the specified files and directories.
  - `CRON`: backup task start time, the user can set any convenient backup start time.
  - `SERVER`: name of the server where the backup will be stored. By default, backups are performed to the first backup server in the list.
  - `SERVER_BACKUP_DIR`: directory on the backup server where completed backups will be stored. The default value is /backup

When configuring the backup schedule, pay special attention to the start time of backups, this affects the performance and speed of backups. Try not to allow a large number of backups to run simultaneously - this can lead to increased load on both the system being backed up and the server where the backup files are being loaded.
It is best to create a schedule in such a way that the tasks start sequentially and do not overlap in time as much as possible.

The **BackupReport** utility is part of the **CLD Backup** module and implements the following functionality for generating reports and monitoring:
  - a list of created instance backup tasks
  - performing backups of specified methods, such as `mysql/mongo/postgresql/clickhouse/files/etc`
  - the number of stored copies and compliance with the given `KEEPLAST` parameter
  - relevance and daily performance, putting down statuses in reports by type: `OK/OUTDATED/FAIL`

An example of the daily report of the **BackupReport** utility (generated daily, automatically and can be sent to Telegram, MatterMost, Slack, Discord and other):
```
Backup report 2022-01-19:
----------------------------
Instances:

nginx.server.com_x.x.x.x_22_root
etc: 2022-01-19 - 7 - 5.3M - OK

frontend.server.com_x.x.x.x_22_root
etc: 2022-01-19 - 7 - 5.6M - OK
files: 2022-01-19 - 7 - 12G- OK

mysql.server.com_x.x.x.x_22_root
etc: 2022-01-19 - 7 - 1.1M - OK
mysql: 2022-01-19 - 7 - 63G - OK
...
```


Below is a list of the Backup-module initial variables.

| Variable | Description |
| :------- | :----------- |
| BACKUPMODULE | variable responsible for initializing the Backup module. |
| BACKUP_SERVER_SET | a mandatory parameter for the initialization and operation of the Backup module, specifying the server where backups will be performed (subsequently, the parameter can be updated, additional backup servers can be added) |
