import click
import logging

from arnold import main, config, sensors


logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    pass


@click.group()
def test():
    pass


@test.command()
@click.option(
    '--address', '-a', default=config.SENSOR['accelerometer']['address'], type=str,
    help='I2C address of the device.'
)
@click.option('--count', '-c', default=5, help='Number of distance tests to perform.')
def accelerometer(address, count):
    click.echo(f'Testing Accelerometer at {address}')
    accelerometer = sensors.accelerometer.Accelerometer(address=address)
    for _ in range(count):
        axes = accelerometer.get_axes()
        click.echo(f'Axes: {axes}')


@test.command()
@click.option(
    '--serial-port', '-p', default=config.SENSOR['lidar']['serial_port'],
    help='Serial port of the lidar sensor.'
)
@click.option(
    '--baudrate', '-b', default=config.SENSOR['lidar']['baudrate'],
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
    '--card-number', '-c', default=config.SENSOR['microphone']['card_number'],
    help='Microphone device card number as per `arecord --list-devices`'
)
@click.option(
    '--device-index', '-i', default=config.SENSOR['microphone']['device_index'],
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
    '--autonomous', is_flag=True,
    help='Run arnold in autonomous mode.'
)
@click.option(
    '--voice-command', is_flag=True,
    help='Run arnold in voice command mode.'
)
@click.option(
    '--manual', '-m', is_flag=True, default=False,
    help='Run arnold in manual mode - controlled via the API.'
)
def run(autonomous, voice_command, manual):
    if autonomous:
        mode = 'autonomous'
    elif voice_command:
        mode = 'voicecommand'
    elif manual:
        mode = 'manual'

    click.echo(f'Running arnold in {mode} mode.')

    arnold = main.Arnold(mode=mode)
    arnold.run()


cli.add_command(test)
