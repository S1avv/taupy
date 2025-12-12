import click

from taupy.cli.commands.new import new
from taupy.cli.commands.dev import dev
from taupy.cli.commands.build import build

from taupy.cli.version import check_for_updates


@click.group()
def cli():
    pass


cli.add_command(new)
cli.add_command(dev)
cli.add_command(build)


def main():
    check_for_updates()
    cli()
