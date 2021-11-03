The module is designed to backup configurations by archiving the `/etc` directory on all or selected instances to the network storage.

The etcbackup module is a handy tool for additional backup of configuration files located in the `/ etc /` directory. The main task of this module is to regularly backup all configuration files in the `/ etc /` directory, which allows, if necessary, to quickly restore one or several files, as well as track their changes over a period of time. The module can be useful for urgent restoration of configuration files without resorting to a full restore from a backup or snapshot. It is possible to configure the backup of the `/ etc /` directories on all instances controlled by the CLD, or, at your own discretion, define a list of instances where the backup will be performed. In addition, the module implements the function of checking the status of backups, which can be extremely useful for generating reports on backup of configuration files and monitoring the success of backup processes.
The main functionality of this module is:
- Convenient and flexible configuration of the list of instances for backing up configuration files in the directory `/ etc /`.
- Setting up tasks for checking the status of backups with the ability to send reports to Telegram.
Below is a list of the etcbackup-module initial variables.
| Variable | Description |
| ------ | ----------- |
| ETCBACKUP | variable responsible for initializing the ETCBACKUP module. |
| ETC_STORAGE_NAME | the name of the repository where the backup files will be located. |
| ETC_BACKUP_PATH | the path where the backups / etc / of the instance configuration files will be created and stored. |
| TELEGRAM_BOT_TOKEN | Telegram bot token, for the functionality of sending reports to the telegram channel. |
