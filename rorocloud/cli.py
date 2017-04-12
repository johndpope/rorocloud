from __future__ import print_function
import click
from .client import Client

client = Client()

@click.group()
def cli():
    """rorocloud is the command-line interface to the rorocloud service.
    """
    pass


@cli.command()
def login():
    """Log into rorocloud service.
    """
    pass


@cli.command(context_settings={"allow_interspersed_args": False})
@click.argument("command", nargs=-1)
@click.option("--shell/--no-shell", default=False, help="execute the given command using shell")
def run(command, shell=None):
    """Runs a command in the cloud.

    Typical usage:

        rorocloud run python myscript.py
    """
    job = client.run(command, shell=shell)
    print("Created new job", job.id)


@cli.command()
def status():
    """Shows the status of recent jobs.
    """
    print("{:10s} {:20s}".format("JOB ID", "CMD"))
    for job in client.jobs():
        line = "{id:10s} {command:20s}".format(id=job.id, command=job.command)
        print(line)

@cli.command()
@click.argument("job_id")
def stop(job_id):
    """Stops a job.
    """
    client.stop_job(job_id)
