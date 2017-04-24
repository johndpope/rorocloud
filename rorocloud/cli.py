from __future__ import print_function
from builtins import input
import time
from datetime import datetime, timedelta
from tabulate import tabulate
import getpass
import click
from .client import Client, config
from .utils import datestr, truncate, setup_logger
from . import __version__

# initialized in cli
client = None

@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose logging")
def cli(verbose=False):
    """rorocloud is the command-line interface to the rorocloud service.
    """
    global client
    client = Client()
    setup_logger(verbose=verbose)

@cli.command()
def help():
    """Show this help message."""
    cli.main(args=[])


@cli.command()
def version():
    """Prints the version of rorocloud client."""
    cli.main(args=["--version"])


@cli.command()
def login():
    """Log into rorocloud service.
    """
    email = input("E-mail: ")
    pw = getpass.getpass("Password: ")
    client.login(email, pw)


@cli.command()
def whoami():
    """prints the details of current user.
    """
    user = client.whoami()
    print(user['email'])


@cli.command(context_settings={"allow_interspersed_args": False})
@click.argument("command", nargs=-1)
@click.option("--shell/--no-shell", default=False, help="execute the given command using shell")
@click.option("--foreground", default=False, is_flag=True)
def run(command, shell=None, foreground=False):
    """Runs a command in the cloud.

    Typical usage:

        rorocloud run python myscript.py
    """
    job = client.run(command, shell=shell)
    print("-- created new job", job.id)
    if foreground:
        _logs(job.id, follow=True)

@cli.command()
@click.option("-a","--all", default=False, is_flag=True)
def status(all=False):
    """Shows the status of recent jobs.
    """
    jobs = client.jobs(all=all)
    rows = []
    for job in jobs:
        start = _parse_time(job.start_time)
        end = _parse_time(job.end_time)
        total_time = (end - start)
        total_time = timedelta(total_time.days, total_time.seconds)
        rows.append([job.id, job.status, datestr(start), str(total_time), truncate(job.command, 50)])
    print(tabulate(rows, headers=['JOBID', 'STATUS', 'WHEN', 'TIME', 'CMD']))

def _parse_time(timestr):
    if not timestr:
        return datetime.utcnow()
    return datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")

@cli.command()
@click.option("-f", "--follow", default=False, is_flag=True)
@click.option("-t", "--show-timestamp", default=False, is_flag=True)
@click.argument("job_id")
def logs(job_id, follow=False, show_timestamp=False):
    """Prints the logs of a job.
    """
    _logs(job_id, follow=follow, show_timestamp=show_timestamp)

def _display_logs(logs, show_timestamp=False):
    def parse_time(timestamp):
        t = datetime.fromtimestamp(timestamp//1000)
        return t.isoformat()

    if show_timestamp:
        log_pattern = "[{timestamp}] {message}"
    else:
        log_pattern = "{message}"

    for line in logs:
        line['timestamp'] = parse_time(line['timestamp'])
        print(log_pattern.format(**line))


def _logs(job_id, follow=False, show_timestamp=False):
    """Shows the logs of job_id.
    """
    if follow:
        seen = 0
        while True:
            response = client.get_logs(job_id)
            logs = response.get('logs', [])
            _display_logs(logs[seen:], show_timestamp=show_timestamp)
            seen = len(logs)
            job = client.get_job(job_id)
            if job.status == 'command exited':
                break
            time.sleep(0.5)
    else:
        response = client.get_logs(job_id)
        if response.get('message', None):
            print(response['message'])
        else:
            _display_logs(response.get('logs'), show_timestamp=show_timestamp)

@cli.command()
@click.argument("job_id")
def stop(job_id):
    """Stops a job.
    """
    client.stop_job(job_id)


def main():
    cli()

def main_dev():
    config["ROROCLOUD_URL"] = "https://rorocloud.staging.rorodata.com/"
    cli()
