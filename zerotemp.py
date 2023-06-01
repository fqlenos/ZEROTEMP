import warnings
from sqlalchemy.exc import SAWarning
import signal
from rich.console import Console

console = Console(color_system='truecolor')

from zerotemp import __app_name__, __version__
from zerotemp.cli import app

def main():

    def __signal_handler(sig, frame): console.print('\n[yellow]Handling exit...[/yellow]'); exit(1)
    signal.signal(signal.SIGINT, __signal_handler)
    app(prog_name=__app_name__)

if __name__ == '__main__':
    warnings.simplefilter("ignore")
    #warnings.filterwarnings("ignore", category=SAWarning)
    main()