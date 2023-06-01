```figlet
 __________ ____   ___ _____ _____ __  __ ____  
|__  / ____|  _ \ / _ \_   _| ____|  \/  |  _ \ 
  / /|  _| | |_) | | | || | |  _| | |\/| | |_) |
 / /_| |___|  _ <| |_| || | | |___| |  | |  __/ 
/____|_____|_| \_\\___/ |_| |_____|_|  |_|_|   

```                                       
ZEROTEMP is the easy to deploy CTF handler.

# Installation

## Dependencies
Requires Python 3.10+

## Requirements
General setup is needed before running the ZEROTEMP platform.
```shell
zero@temp:~# git clone https://github.com/fqlenos/zerotemp zerotemp
zero@temp:~# cd zerotemp/
zero@temp:~# pip install -r requirements.txt
```

### Populate Database
The Database is empty. You can populate it once the Flask Web App is running.
```shell
zero@temp:~# python3 zerotemp.py run -d
zero@temp:~#
```  
In the browser, search for: http://127.0.0.1:5000/populate/

## From Source
ZEROTEMP from source deployment.
```shell
zero@temp:~# git clone https://github.com/fqlenos/zerotemp zerotemp
zero@temp:~# python3 zerotemp.py --help                                                 
                                                                                                 
 Usage: zerotemp [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ check          Check the current Docker and production configuration for CTF handler.                                │
│ clean          Clean created Docker containers/images.                                                               │
│ populate       Populate database.                                                                                    │
│ run            Run the CTF handler.                                                                                  │
│ setup          Docker and production configuration setup for CTF handler.                                            │
│ stress         Load test. [In development]                                                                           │
│ version        Version information.                                                                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
zero@temp:~# python3 zerotemp.py version
ZEROTEMP v1.0.0
zero@temp:~#
```

# Usage

## Docker
ZEROTEMP can be deployed using Docker.

> Warning! It must be launched the "setup" option before running in Docker mode.

```shell
zero@temp:~# git clone https://github.com/fqlenos/zerotemp zerotemp
zero@temp:~# python3 zerotemp.py run --help

 Usage: zerotemp run [OPTIONS]

 Run the CTF handler.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --docker                 Launch in Docker mode (default). [default: True]                                            │
│ --debug-pre  -pre        Launch in debugging mode (Development Configuration).                                       │
│ --debug-pro  -pro        Launch in debugging mode (Production Configuration).                                        │
│ --help                   Show this message and exit.                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
zero@temp:~# python3 zerotemp.py run --docker
zero@temp:~#
```

## Debugger
It can be launched in Debug Mode with:
```shell
zero@temp:~# git clone https://github.com/fqlenos/zerotemp zerotemp
zero@temp:~# python3 zerotemp.py run --help

 Usage: zerotemp run [OPTIONS]

 Run the CTF handler.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --docker                 Launch in Docker mode (default). [default: True]                                            │
│ --debug-pre  -pre        Launch in debugging mode (Development Configuration).                                       │
│ --debug-pro  -pro        Launch in debugging mode (Production Configuration).                                        │
│ --help                   Show this message and exit.                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
zero@temp:~# python3 zerotemp.py run -pre
zero@temp:~#
```