import click
import subprocess

@click.command()
def run():
    subprocess.run(["python", "main.py"])