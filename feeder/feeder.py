from app.app import create_app as app
from base64 import b64encode
from rich.console import Console
from rich.prompt import Prompt, Confirm
import os
import json
from werkzeug.datastructures import FileStorage

console = Console(color_system='truecolor')


class Feeder:

    def warning(self) -> bool:
        console.print('[yellow]Warning! Populate removes actual data from Database.[/yellow]')
        option = Confirm.ask('Do you want to continue?', default=True)
        return option
    
    def __init__(self) -> None:
        
        self.user = Prompt.ask('Admin user')
        self.password = Prompt.ask(f'Password for {self.user}', password=True)

    def upload_challenges(self) -> bool:

        if not self.warning(): 
            return False

        self.file = ''
        while not os.path.exists(self.file):
            self.file = Prompt.ask('Absolute path to JSON file')
        
        try:
            open(self.file, 'rb')
        except:
            console.print(f'[red]The "{self.file}" file cannot be opened.[/red]')
            exit(-1)

        creds = b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('utf-8')
        with app().test_client() as client:

            headers = { 'Authorization': f'Basic {creds}', 'Content-Type': 'multipart/form-data' }

            with open(self.file, 'rb') as ufile:
                file = FileStorage(ufile)
                try:
                    res = client.post('/api/import', data={'import': file}, headers=headers)
                    console.print(f'[red]{res.json}[/red]' if res.json is not None else f'[green]Finished.[/green]')
                    return True
                except:
                    console.print('[red]An error ocurred. Please checkout the JSON format.[/red]')
                    return False
                
    def upload_users(self) -> bool:

        creds = b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('utf-8')
        new_users = []
        from_file = Confirm.ask('Import from JSON file?', default=False)

        if from_file:
                    
            self.file = ''
            while not os.path.exists(self.file):
                self.file = Prompt.ask('Absolute path to JSON file')
            
            try:
                ufile = open(self.file, 'rb')
            except:
                console.print(f'[red]The "{self.file}" file cannot be opened.[/red]')
                exit(-1)
            
            data = json.load(ufile)
            if 'users' in data:
                users:list[dict] = data.get('users')
                new_users = [(d['user'], d['password'], d['is_admin']) for d in users]
            else:
                console.print('[red]An error ocurred. Please checkout the JSON format.[/red]')
                return False

        else:
            more = True
            new_users:list[tuple[str,str,bool]] = []

            while more:
                user = Prompt.ask('[cyan]New username[/cyan]')
                password = Prompt.ask(f'[cyan]Password for {user}[/cyan]', password=True)
                is_admin:bool = Confirm.ask(f'[cyan]{user} is admin[/cyan]', default=True)
                new_users.append((user, password, is_admin))
                more = Confirm.ask('[cyan]Do you want to add more users?[/cyan]', default=True)
            
        if len(new_users) > 0:

            with app().test_client() as client:

                headers = { 'Authorization': f'Basic {creds}', 'Content-Type': 'application/json' }
                try:
                    res = client.post('/api/create/user', data=json.dumps({'users': new_users}), headers=headers)
                    console.print(f'[red]{res.json}[/red]' if res.json is not None else f'[green]Finished.[/green]')
                    return True
                except:
                    return False
