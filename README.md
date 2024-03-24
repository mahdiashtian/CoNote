# CoNote

# Overview

conote is a simple and online notebook that allows you to save your notes, memories,... online and share them with others.

# System Features
- [x] Notification system : Creating and using a suitable structure according to the abstract factory design pattern to send email and SMS according to a specific structure
- [ ] Logging system : Use a logging system for troubleshooting
- [ ] Comment system and Webscoket: Using the ability to comment and notify comments online using the web socket protocol   
- [x] JWT Authentication : It uses JWT tokens to authenticate users, which works on platforms other than the web
- [x] Clear structure : The code is written in a way that is easy to understand and modify

# Application Features
- [x] Notification system : If you give someone access to view your notebook or vice versa, you will be informed about this through SMS and email
- [x] Permission submission system : You can allow other users to view your notebook and notes  
- [x] Comment system : You can post comments on your notes or other people's notes (if you have access)
- [x] Access at all times : You can access and comment on your notes and any notes you have access to view at any time.

# Getting Started

## Requirements

- Python 3.8 and above
- Postegras or any other database supported by django
- RabbitMq or any message broker

## Installation
1. Clone the repository<br/>
   ```git clone https://github.com/mahdiashtian/conote.git```
2. Navigate to the project directory<br/>
   ```cd conote```
3. Create and activate a virtual environment<br/>
    1. ```python -m venv venv```
    2. ```source venv/bin/activate``` (Linux)
       ```venv\Scripts\activate``` (Windows)
4. Install the requirements<br/>
   ```pip install -r requirements.txt```

## Configuration
To launch the project, you need to replace your project settings in the .env file with the default settings.
Required values:
```
SECRET_KEY=''
BROKER_PROTOCOL=''
BROKER_USERNAME=''
BROKER_PASSWORD=''
BROKER_HOST=''
BROKER_PORT=''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
SMS_FROM=''
SMS_USERNAME=''
SMS_PASSWORD=''
```
If you want to run the project in production mode, you must add variables related to the database
```
DB_NAME=''
DB_USER=''
DB_PASSWORD=''
DB_HOST=''
DB_PORT=''
```

## Usage
Using the following command in the command line, you can run the project as a demo version on the server:
```python manage.py runserver```<br/>
If you need and want, you can run the project tests with the following command:
```pytest```

# Contact
For any questions or suggestions, please contact [me](mailto:mahdiashtian.mo@gmail.com)
