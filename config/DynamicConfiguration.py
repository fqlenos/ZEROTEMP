import re
import os
import json
import secrets
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.table import Table
import config

console = Console()
basedir = os.path.abspath(os.path.dirname(__file__))

DEFAULT_CONFIG:dict = {
        'SECRET_KEY': secrets.token_hex(32 // 2),
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + os.path.join(basedir, 'zerotemp.db'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': True,
        'DEBUG': False,
        'TESTING': False,
        'TEMPLATES_AUTO_RELOAD': False,
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'PERMANENT_SESSION_LIFETIME': 2592000,
        'PORT': 5000,
        'CTF_NAME': 'ZEROTEMP',
        'ZEROTEMP_CONFIG': 'Yes'
    }

class Configuration:

    def __init__(self) -> None:
        self.questions:list[dict] = self.get_questions()
        self.previous = -1
        self.aux_current = 0
        self.current = 0
        self.config = {}

    def get_questions(self) -> None:
        questions = [
            {
                'question': 'Do you want to setup with recommended Flask configuration?',
                'valid_answers': ['Yes', 'No'],
                'default': 'Yes',
                'next_question_1': 'CTF Challenge name',
                'next_question_2': 'SECRET_KEY',
                'zconfig': 'ZEROTEMP_CONFIG'
            },
            {
                'question': 'CTF Challenge name',
                'valid_answers': [],
                'default': 'ZEROTEMP',
                'next_question': 'Select host\'s port to publish',
                'zconfig': 'CTF_NAME'
            },
            {
                'question': 'Select host\'s port to publish',
                'valid_answers': [],
                'default': '5000',
                'next_question': '',
                'zconfig': 'PORT'
            },
            {
                'question': 'SECRET_KEY',
                'valid_answers': [],
                'default': str(secrets.token_hex(32 // 2)),
                'next_question': 'SQLALCHEMY_DATABASE_URI',
                'zconfig': 'SECRET_KEY'
            },
            {
                'question': 'SQLALCHEMY_DATABASE_URI',
                'valid_answers': [],
                'default': 'sqlite:///' + os.path.join(basedir, 'zerotemp.db'),
                'next_question': 'SQLALCHEMY_TRACK_MODIFICATIONS',
                'zconfig': 'SQLALCHEMY_DATABASE_URI'
            },
            {
                'question': 'SQLALCHEMY_TRACK_MODIFICATIONS',
                'valid_answers': ['True', 'False'],
                'default': 'True',
                'next_question': 'DEBUG',
                'zconfig': 'SQLALCHEMY_TRACK_MODIFICATIONS'
            },
            {
                'question': 'DEBUG',
                'valid_answers': ['True', 'False'],
                'default': 'False',
                'next_question': 'TESTING',
                'zconfig': 'DEBUG'
            },
            {
                'question': 'TESTING',
                'valid_answers': ['True', 'False'],
                'default': 'False',
                'next_question': 'TEMPLATES_AUTO_RELOAD',
                'zconfig': 'TESTING'
            },            
            {
                'question': 'TEMPLATES_AUTO_RELOAD',
                'valid_answers': ['True', 'False'],
                'default': 'False',
                'next_question': 'SESSION_COOKIE_SECURE',
                'zconfig': 'TEMPLATES_AUTO_RELOAD'
            },
            {
                'question': 'SESSION_COOKIE_SECURE',
                'valid_answers': ['True', 'False'],
                'default': 'True',
                'next_question': 'SESSION_COOKIE_HTTPONLY',
                'zconfig': 'SESSION_COOKIE_SECURE'
            },
            {
                'question': 'SESSION_COOKIE_HTTPONLY',
                'valid_answers': ['True', 'False'],
                'default': 'True',
                'next_question': 'PERMANENT_SESSION_LIFETIME',
                'zconfig': 'SESSION_COOKIE_HTTPONLY'
            },
            {
                'question': 'PERMANENT_SESSION_LIFETIME (in seconds)',
                'valid_answers': [],
                'default': '2592000',
                'next_question': 'CTF Challenge name',
                'zconfig': 'PERMANENT_SESSION_LIFETIME'
            }
        ]
        return questions

    def setup(self) -> bool:

        console.print('[blue]General configuration for Flask App and Docker[/blue]')

        while self.current < len(self.questions):
            question = self.questions[self.current]['question']
            self.valid_answers:list[str] = self.questions[self.current]['valid_answers']
            if all([len(self.valid_answers) > 0, 'back' not in self.valid_answers, self.current > 0]): self.valid_answers.append('back')
            elif all([len(self.valid_answers) > 0, 'back' not in self.valid_answers]): self.valid_answers
            else: self.valid_answers = None
            if 'default' in self.questions[self.current]: self.default_answer = self.questions[self.current]['default']
            else: self.default_answer = None
            answer = Prompt.ask(f'[cyan]{str(question).strip()}[/cyan]', choices=self.valid_answers, default=self.default_answer)
            if answer == 'exit': return False 
            if answer == 'back':
                if self.previous > -1:
                    self.current = self.previous
                    self.aux_current = 0
                    self.choices = self.valid_answers
                    self.default = self.default_answer
                elif self.current > 0: 
                    self.current -= 1
                    self.aux_current = 0
            else:
                if 'SECRET_KEY' in question:
                    if len(str(answer)) > 32: console.print('[yellow]Performance may be affected with a "SECRET_KEY" greater than 32 bytes.[/yellow]')
                if 'SQLALCHEMY_DATABASE_URI' in question:
                    valid = self.re_validator(engine=str(answer))
                    if valid: self.valid_answers = None
                    else:
                        msg = '\n'.join([
                            '[red]SQLALCHEMY_DATABASE_URI must follow official standards for sqlite/mysql+pymsql:[/red]',
                            '\t[red]SQLite:\tsqlite:///path/to/database.db[/red]',
                            '\t[red]MySQL:\tmysql+pymysql://username:password@host:port/database_name?charset=utf8mb4[/red]'
                        ])
                        console.print(msg)
                        continue
                if 'Select host\'s port to publish' in question:
                    valid = self.int_validator(port=str(answer))
                    if valid: self.valid_answers = None
                    else:
                        console.print('[red]The port must be an integer.[/red]')
                        continue
                if 'CTF Challenge name' in question:
                    valid = True if str(answer) != '' or str(answer) is not None else False 
                    if valid: self.valid_answers = None
                    else:
                        console.print('[red]You cannot add an empty CTF name.[/red]')
                        continue
                if self.valid_answers is None:
                    self.config[self.questions[self.current]['zconfig']] = answer
                    next_question = self.questions[self.current]['next_question']
                    for pack_num, pack in enumerate(self.questions):
                        if next_question in pack['question'] and next_question != '': 
                            self.aux_current = pack_num
                    if self.current != self.aux_current: 
                        self.previous = self.current
                        self.current = self.aux_current
                    else: break
                elif answer in self.valid_answers:
                    self.config[self.questions[self.current]['zconfig']] = answer
                    pos = self.valid_answers.index(answer) + 1
                    if f'next_question_{pos}' in self.questions[self.current]: next_question = self.questions[self.current][f'next_question_{pos}']
                    else: next_question = self.questions[self.current][f'next_question']
                    for pack_num, pack in enumerate(self.questions):
                        if next_question in pack['question'] and next_question != '': 
                            self.aux_current = pack_num
                    if self.current != self.aux_current: 
                        self.previous = self.current
                        self.current = self.aux_current
                    else: break
                else: console.print('[red]Not valid answer.[/red]')

        saved = self.present()
        if saved: return True
        return False

    def present(self) -> bool:

        if self.config['ZEROTEMP_CONFIG'] == 'Yes': 
            if int(self.config['PORT']) != 5000: DEFAULT_CONFIG.update({ 'PORT': self.config['PORT'] })
            if str(self.config['CTF_NAME']).lower() != 'zerotemp': DEFAULT_CONFIG.update({ 'CTF_NAME': self.config['CTF_NAME'] })
            self.config:dict = DEFAULT_CONFIG
        self.show_config(dictconfig=self.config)
        
        save = Confirm.ask('[cyan]Do you want to continue with the selected configuration?[/cyan]', default=True)
        if save: return self.save()
        else:
            repeat = Confirm.ask('[cyan]Do you want to start again with the configuration?[/cyan]', default=True)
            if repeat:
                self.questions:list[dict] = self.get_questions()
                self.previous = -1
                self.aux_current = 0
                self.current = 0
                self.config = {}
                self.setup()
            else: console.print('[yellow]Exiting the configuration process...[/yellow]')
        return False

    def save(self) -> bool:
        
        basedir = os.path.abspath(os.path.dirname(__file__))
        try:
            with open(f'{os.path.join(basedir, "config.json")}', 'w+') as config_file:
                json.dump(self.config, config_file, default=str, indent=4)
            console.print('[green]Successfully saved the configuration.[/green]')
            return True
        except Exception as e:
            console.print('[red]An error ocurred while saving...[/red]')
        return False
    
    @classmethod
    def show_config(cls, dictconfig:dict={}):
        
        if not dictconfig:
            basedir = os.path.abspath(os.path.dirname(__file__))
            try:
                with open(f'{os.path.join(basedir, "config.json")}', 'r') as config_file:
                    dictconfig = json.load(config_file)
            except Exception as e:
                dictconfig = DEFAULT_CONFIG

            if not dictconfig: dictconfig = DEFAULT_CONFIG
        
        table = Table(title='[blue]Current configuration[/blue]', caption='[red]"SECRET_KEY" will be autogenerated if empty.[/red]')
        table.add_column('Configuration')
        table.add_column('Selected')
        for key, value in dictconfig.items():
            if str(key).startswith('_'): continue
            if key not in DEFAULT_CONFIG: continue
            if str(value) == str(DEFAULT_CONFIG[key]) or (key == 'SECRET_KEY' and (len(str(value)) >= 15 and len(str(value)) <= 32)): value = f'[green]{str(value)}[/green]'
            else: value = f'[yellow]{str(value)}[/yellow] -> [cyan]Recommended: {DEFAULT_CONFIG[key]}[/cyan]'
            table.add_row(key, value)
        console.print(table)

    @classmethod
    def re_validator(cls, engine:str):
        #sqlite_pattern = re.compile(r'^sqlite:///[\w/.]+\.db$')
        sqlite_pattern = re.compile(r'^sqlite:///[\w\s\\/:.-]+\.db$')
        mysql_pattern = re.compile(r'^mysql\+pymysql://[^\s:]+:[^\s@]+@[\w.-]+:\d+/\w+\??[\w=&]*$')
        #postgresql_pattern = re.compile(r'^postgresql://\w+:\w+@\w+:\d+/\w+\??\w+=\w+')
        if any([bool(sqlite_pattern.match(str(engine).strip())), bool(mysql_pattern.match(str(engine).strip()))]):
            return True
        return False
    
    @classmethod
    def int_validator(cls, port:str):
        try:
            return int(port)
        except ValueError:
            return False