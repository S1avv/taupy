import click
import subprocess
import os

@click.command()
def dev():
    subprocess.run(["python", "main.py", "--dev"])