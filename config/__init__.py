from .Config import Config, Production, Development
from .DynamicConfiguration import Configuration

import os
import json
from rich.console import Console

UPLOAD_USER_FOLDER = 'user'
UPLOAD_SPONSOR_FOLDER = 'sponsor'
UPLOAD_CHALLENGE_FOLDER = 'challenge'
DOWNLOAD_CTF_FOLDER = 'ctf'

console = Console(color_system='truecolor')

basedir = os.path.abspath(os.path.dirname('config'))

with open(os.path.join(basedir, 'config', 'config.json')) as f:
    config_data:dict = json.load(f)

    if not config_data:
        console.print('[red]No previous data is saved.[/red]')
        configuration = Configuration()
        done = configuration.setup()
        if not done: console.print('[yellow]Exiting...[/yellow]')
        exit()

if 'SQLALCHEMY_DATABASE_URI' in config_data:
    if 'sqlite' in config_data['SQLALCHEMY_DATABASE_URI']:
        config_data.update({ 'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(basedir, 'config', 'zerotemp.db') })

if 'PORT' in config_data:
    PORT = config_data.get('PORT')
    config_data.pop('PORT')
else: PORT = 5000

if 'CTF_NAME' in config_data:
    CTFNAME = config_data.get('CTF_NAME')
    config_data.pop('CTF_NAME')
else: CTFNAME = 'ZEROTEMP'

for key, value in config_data.items():

    if any([value == 'True', value == 'true', value == 'TRUE']): value = True
    elif any([value == 'False', value == 'false', value == 'FALSE']): value = False
    if key == 'PERMANENT_SESSION_LIFETIME': 
        try: value = int(value)
        except:
            console.print('[red]"PERMANENT_SESSION_LIFETIME" must be "Integer". Default value will be set: 2592000[/red]')
            value = 2592000
            
    setattr(Production, key, value)