import click

from taupy.cli.commands.new import new
from taupy.cli.commands.dev import dev
from taupy.cli.commands.run import run
from taupy.cli.commands.build import build
from taupy.cli.commands.config import config
from taupy.cli.commands.doctor import doctor
from taupy.cli.commands.info import info

from taupy.cli.version import check_for_updates


@click.group()
def cli():
    pass


cli.add_command(new)
cli.add_command(dev)
cli.add_command(run)
cli.add_command(build)
cli.add_command(config)
cli.add_command(doctor)
cli.add_command(info)


def main():
    check_for_updates()
    cli()
