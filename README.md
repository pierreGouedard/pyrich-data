# pyrich-data

### Server setup:

* connect via password
* add puclic key to .ssh/authorized_keys
* update ssh config to disable password auth
* `sudo nano /etc/ssh/sshd_config` and the `[INCLUDE]` to remove password auth or edit ssh.socket using: `sudo systemctl edit ssh.socket`
* change port by default to a random 1 between 10000 and 99999
* edit ssh `host.allow` & `host.deny` to allow only some IP to access via ssh the machine.
* configure iptables for even more security

Once ssh config are done, restart it:
```commandline
# restart ssh 
sudo systemctl restart ssh
sudo systemctl restart sshd
sudo systemctl daemon-reload
sudo systemctl restart ssh.service
```

### python set-up 

place yourself at the root dir of the project:

```commandline
# Install venv
sudo apt install python3.12-venv

# Create virtual env
python3 -m venv venv

# Activate virtual env
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Set up the crontab
crontab -e

# copy paste the following
* * * * * . ~/pyrich-data/venv/bin/activate && python ~/pyrich-data/src/scripts/prod/get_xtb_latest_ticks.py
1 0 * * 1 . ~/pyrich-data/venv/bin/activate && python ~/pyrich-data/src/scripts/prod/get_xtb_calendar.py
1 1 * * 1 . ~/pyrich-data/venv/bin/activate && python ~/pyrich-data/src/scripts/prod/get_xtb_history_data.py
* 0 * * * . ~/pyrich-data/venv/bin/activate && python ~/pyrich-data/src/scripts/prod/clean_files.py 
```