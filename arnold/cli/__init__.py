import click

from arnold import main, config, sensors


API_CONFIG = config.API
SENSOR_CONFIG = config.SENSOR_CONFIG


@click.group()
def cli():
    pass


@click.group()
def test():
    pass


@test.command()
@click.option(
    '--serial-port', '-p', default=SENSOR_CONFIG['lidar']['serial_port'],
    help='Serial port of the lidar sensor.'
)
@click.option(
    '--baudrate', '-b', default=SENSOR_CONFIG['lidar']['baudrate'],
    help='Baudrate of the serial device.'
)
@click.option('--count', '-c', default=5, help='Number of distance tests to perform.')
def lidar(serial_port, baudrate, count):
    click.echo(f'Testing Lidar at {serial_port} ({baudrate})')
    lidar = sensors.lidar.Lidar(serial_port=serial_port, baudrate=baudrate)
    for _ in range(count):
        distance = lidar.get_distance()
        click.echo(f'Distance: {distance}')


@test.command()
@click.option(
    '--card-number', '-c', default=SENSOR_CONFIG['microphone']['card_number'],
    help='Microphone device card number as per `arecord --list-devices`'
)
@click.option(
    '--device-index', '-i', default=SENSOR_CONFIG['microphone']['device_index'],
    help='Microphone device index as per `arecord --list-devices`'
)
def microphone(card_number, device_index):
    click.echo(f'Testing Microphone at {card_number}:{device_index}')
    microphone = sensors.microphone.Microphone(
        card_number=card_number, device_index=device_index
    )
    audio = microphone.listen()
    print(microphone.recognise_command(audio))


@cli.command()
@click.option(
    '--autonomous', '-a', default=False, help='Run arnold in autonomous mode.'
)
@click.option(
    '--voice-command', '-v', default=False, help='Run arnold in voice command mode.'
)
def run(autonomous, voice_command):
    mode = 'manual'
    if autonomous:
        mode = 'autonomous'
    elif voice_command:
        mode = 'voice_command'

    arnold = main.Arnold(mode=mode)
    arnold.run()

    click.echo(f'Running arnold in {mode} mode.')


cli.add_command(test)
