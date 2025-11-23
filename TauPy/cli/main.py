import click

from TauPy.cli.commands.new import new
from TauPy.cli.commands.dev import dev
from TauPy.cli.commands.run import run
from TauPy.cli.commands.build import build

from TauPy.cli.version import check_for_updates


@click.group()
def cli():
    pass


cli.add_command(new)
cli.add_command(dev)
cli.add_command(run)
cli.add_command(build)


def main():
    check_for_updates()
    cli()
