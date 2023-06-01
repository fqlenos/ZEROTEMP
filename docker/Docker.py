import subprocess
from rich.console import Console
from rich.prompt import Confirm

from config import PORT

console = Console()
confirm = Confirm()

class Docker:

    def __init__(self, name:str=None) -> None:
        if name == None: console.print('[red]"Name" cannot be empty.[/red]'); exit(1)
        self.name = name

    def docker(self):
        console.print(f'[green]Building image {str(self.name).lower()}...[/green]')
        console.print('[yellow]It could take a while.[/yellow]')
        subprocess.call(f'docker build -t {str(self.name).lower()} .', shell=True)
        console.print('[green]Starting ZEROTEMP[/green]')
        subprocess.call(f'docker run -it --rm -p 5000:{PORT} --name {str(self.name).lower()} {str(self.name).lower()}', shell=True)
    
    def stop(self):
        console.print('[yellow]This could slow down the ZEROTEMP building and starting process.[/yellow]')
        yes = confirm.ask('Do you want to clear ZEROTEMP\'s cached images', default='y')
        if yes:
            console.print('[red bold]Removing ZEROTEMP\'s related images...[/red bold]')
            subprocess.call(f'docker stop {str(self.name).lower()}', shell=True, stderr=subprocess.DEVNULL)
            subprocess.call(f'docker rmi -f {str(self.name).lower()}', shell=True, stderr=subprocess.DEVNULL)
        console.print('See you later!')

    ''' log docker output if wanted '''    
    #with open('./zerotemp/docker/docker.log', 'a') as output:
        #subprocess.call(f'docker build -t {str(self.name).lower()} .', shell=True, stdout=output)
        #subprocess.call(f'docker run -it --rm --name {str(self.name).lower()} {str(self.name).lower()}', shell=True, stdout=output)