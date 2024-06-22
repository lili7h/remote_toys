import os
import sys
import subprocess


def dev() -> None:
    """
    Expects CWD to be parter-proker/
    :return:
    """
    os.chdir('parter_poker')
    cmd = ['flask', '--app', 'partner:devapp',  'run']
    subprocess.run(cmd)


def prod() -> None:
    os.chdir('parter_poker')
    cmd = ['waitress-serve', '--listen', '*:8080', '--call', 'partner:myapp']
    subprocess.run(cmd)


def prod_serve() -> None:
    os.chdir('parter_poker')
    waitress_cmd = ['waitress-serve', '--listen', '*:8080', '--call', 'partner:myapp']
    ngrok_cmd = ['ngrok', 'http', f'--domain={os.environ["NGROK_DOMAIN"]}', '8080']
    subprocess.Popen(waitress_cmd)
    subprocess.run(ngrok_cmd, capture_output=True)
