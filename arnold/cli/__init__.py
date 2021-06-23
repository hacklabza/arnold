import click


@click.group()
def cli():
    pass


@click.command()
@click.option('--host', '-p', default='0.0.0.0', help='Host IP address to run the API server from.')
@click.option('--port', '-h', default=8000, help='Port number to run the API server from.')
def run(host, port):
    click.echo(f'Running API server at {host}:{port}')


cli.add_command(run)
