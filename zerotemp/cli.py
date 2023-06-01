import typer
from typing import Optional

app = typer.Typer(add_completion=False, no_args_is_help=True)

@app.command(help='Docker and production configuration setup for CTF handler.')
def setup() -> None:

    from config import Configuration
    from rich.console import Console

    console = Console(color_system='truecolor')

    configuration = Configuration()
    done = configuration.setup()
    if not done: console.print('[yellow]Exiting...[/yellow]')

@app.command(help='Check the current Docker and production configuration for CTF handler.')
def check() -> None:
    
    from config import Configuration

    Configuration.show_config()

@app.command(help='Clean created Docker containers/images.')
def clean() -> None:

    from . import __app_name__
    from docker import Docker

    docker = Docker(name=__app_name__)
    docker.stop()

@app.command(help='Run the CTF handler.')
def run(
    run_docker:Optional[bool] = typer.Option(True, "--docker", help='Launch in Docker mode (default).'),
    run_debug_pre:Optional[bool] = typer.Option(False, "-pre", "--debug-pre", help='Launch in debugging mode (Development Configuration).'),
    run_debug_pro:Optional[bool] = typer.Option(False, "-pro", "--debug-pro", help='Launch in debugging mode (Production Configuration).'),
) -> None:

    if run_debug_pro and run_docker:

        from serve import Serve
        from config import Production

        Serve.standalone(profile=Production)

    elif run_debug_pre and run_docker:

        from serve import Serve
        from config import Development

        Serve.standalone(profile=Development)

    else:
        from docker import Docker
        from . import __app_name__

        serve = Docker(name=__app_name__)
        serve.docker()

@app.command(help='Version information.')
def version() -> None:

    from . import __app_name__, __version__
    from rich.console import Console
    console = Console(color_system='truecolor')

    console.print(f'{str(__app_name__).upper()} {__version__}', style='grey58', highlight=False)
    raise typer.Exit()

@app.command(help='Populate database.', no_args_is_help=True)
def populate(
    challenges:Optional[bool] = typer.Option(None, "-c", "--challenges", help='Upload challenges.'),
    users:Optional[bool] = typer.Option(None, "-u", "--users", help='Upload users.'),
) -> None:
    
    from feeder import Feeder

    feeder = Feeder()
    if challenges:
        feeder.upload_challenges()
    elif users:
        feeder.upload_users()


@app.command(help='Load test. [In development]')
def stress() -> None:

    print('[?] In development... Ready on Version v1.0.1.')
    exit()
    """ 
    from stress import Stress
    stress = Stress()
    stress.create_users() 
    """