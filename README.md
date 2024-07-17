# Flask CMS


flask-cms is a scalable administrator dashboard developed using Python Flask, Tailwind CSS, and SQLite3. Designed with flexibility in mind, this CMS can be extended with various extensions to suit different requirements.

## Features

- Lightweight and Fast: Utilizes SQLite3 for a lightweight and fast database solution.
- Easy to Use: Simple setup and intuitive admin dashboard.
- Modern UI: Built with Tailwind CSS for a clean and responsive interface.

## Installation

Download Gunicorn into your system
```
git clone https://github.com/tadiyusss/flask-cms
cd flask-cms
pip3 install -r requirements.txt
```

### Running the script
You can use the command below to run the script. However this is not recommended in production.
```
python3 app.py
```

### Running with Gunicorn

Install gunicorn in your system
```
sudo apt install gunicorn
```
Running flask-cms with gunicorn
```
gunicorn app:app
```

### Creating flask-cms as a Service

To run flask-cms as a service, you can use a process manager like systemd. 

Open your terminal and navigate to the systemd directory
```
cd /etc/systemd/system/
```

Create a new service file using nano
```
sudo nano flask-cms.service
```
Add the following content to the service file
```
[Unit]
Description=flask-cms Service
After=network.target

[Service]
User=<your_username>
WorkingDirectory=/path/to/flask-cms
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```
Replace `WorkingDirectory` with your actual path to flask-cms


Reload systemd to load the new service file
```
sudo systemctl daemon-reload
```
Enable flask-cms service to start on boot
```
sudo systemctl enable flask-cms
```
Start the flask-cms 
```
sudo systemctl start flask-cms
```
Check the status of the flask-cms service:
```
sudo systemctl status flask-cms
```
Now, flask-cms will be automatically started as a service whenever your system boots up.