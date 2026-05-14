## TGSaneBot

This bot has been created to help me with managing personal activities.

### How to start using this:

##### 1. Clone repository to your machine and go the project folder:

```
git clone https://github.com/saneness/tgsanebot.git
cd tgsanebot/
```

##### 2. Copy config_example.py to config.py and update all the required fields:

```
cp config_example.py config.py
```

##### 3. Create virtual environment:

```
python -m venv venv/
source venv/bin/activate
```

##### 4. Install dependancies:

```
pip install -r requirements.txt
```

##### 5. Run the main script:

```
python main.py
```

### Example of systemd service:

```
[Unit]
Description=tgsanebot
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/path/to/project/tgsanebot
ExecStart=/path/to/project/tgsanebot/venv/bin/python /path/to/project/tgsanebot/main.py
Restart=on-failure
User=user
Group=group

[Install]
WantedBy=multi-user.target
```
