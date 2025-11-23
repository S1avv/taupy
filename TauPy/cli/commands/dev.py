import click
import subprocess
import os

@click.command()
def dev():
    click.echo("🚀 TauPy Dev Server started!")
    subprocess.run(["python", "main.py"])