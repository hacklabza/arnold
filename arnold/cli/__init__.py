import json
import os

import click
import logging

from arnold import main, config, output, sensors


logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    pass


@click.group()
def calibrate():
    pass


@click.group()
def test():
    pass


# Calibration commands
@calibrate.command()
@click.option(
    '--address', '-a', default=config.SENSOR['imu']['address'], type=str,
    help='I2C address of the device.'
)
def imu(address):
    click.echo(f'Calibrating IMU at {address}')
    imu = sensors.imu.IMU(address=address)
    imu.calibrate()

    click.echo(f'Save the following values to environmental vars.')
    click.echo(f'Accelerometer Bias: {imu.sensor.abias}')
    click.echo(f'Gyroscope Bias: {imu.sensor.gbias}')
    click.echo(f'Magnetometer Bias: {imu.sensor.mbias}')

    os.environ['ARNOLD_SENSOR_IMU_BIAS'] = json.dumps({
        'accelerometer': imu.sensor.abias,
        'gyroscope': imu.sensor.gbias,
        'magnetometer': imu.sensor.mbias
    })


# Output device tests
@test.command()
@click.option(
    '--phrase', '-p', required=True, help='The phrase that should be spoken.'
)
def speaker(phrase):
    click.echo(f'Testing Speaker with "{phrase}"')
    speaker = output.speaker.Speaker()
    speaker.say(phrase)


# Sensor tests
@test.command()
@click.option(
    '--address', '-a', default=config.SENSOR['imu']['address'], type=str,
    help='I2C address of the device.'
)
@click.option('--count', '-c', default=5, help='Number of distance tests to perform.')
def imu(address, count):
    click.echo(f'Testing IMU at {address}')
    imu = sensors.imu.IMU(address=address)

    for _ in range(count):
        accelerometer_data = imu.get_accelerometer_data()
        gyroscope_data = imu.get_gyroscope_data()
        magnetometer_data = imu.get_magnetometer_data()
        temperature = imu.get_temperature()
        attitude = imu.get_attitude()

        click.echo(f'Accelerometer: {accelerometer_data}')
        click.echo(f'Gyroscope: {gyroscope_data}')
        click.echo(f'Magnetometer: {magnetometer_data}')
        click.echo(f'Temperature: {temperature}')
        click.echo(f'Attitude: {attitude}')


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
    help='Microphone device card number as per `arecord --list-devices`.'
)
@click.option(
    '--device-index', '-i', default=config.SENSOR['microphone']['device_index'],
    help='Microphone device index as per `arecord --list-devices`.'
)
def microphone(card_number, device_index):
    click.echo(f'Testing Microphone at {card_number}:{device_index}')
    microphone = sensors.microphone.Microphone(
        card_number=card_number, device_index=device_index
    )
    audio = microphone.listen()
    click.echo(microphone.recognise_command(audio))


@test.command()
@click.option(
    '--video', '-v', is_flag=True, help='Test camera in video mode.'
)
@click.option(
    '--image', '-i', is_flag=True, help='Test camera in image mode.'
)
@click.option(
    '--file-path', '-f', default=None, help='The file path to save the test image to.'
)
@click.option(
    '--width', '-w', default=None, help='The width of the image to be captured.'
)
@click.option(
    '--height', '-h', default=None, help='The height of the image to be captured.'
)
@click.option(
    '--frame-rate', '-r', default=config.SENSOR['camera']['video']['frame_rate'],
    help='The frame rate of the video to be captured.'
)
@click.option(
    '--duration', '-d', default=config.SENSOR['camera']['video']['duration'],
    help='The duration of the video to be captured.'
)
def camera(video, image, file_path, width, height, frame_rate, duration):
    capture_mode = 'image' if image else 'video'
    click.echo(f'Testing Camera in `{capture_mode}` mode.')
    camera = sensors.camera.Camera()

    if image:
        camera.capture_image(
            file_path=file_path or config.SENSOR['camera']['image']['file_path'],
            width=width or config.SENSOR['camera']['image']['width'],
            height=height or config.SENSOR['camera']['image']['height'],
        )
    elif video:
        camera.capture_video(
            file_path=file_path or config.SENSOR['camera']['video']['file_path'],
            width=width or config.SENSOR['camera']['video']['width'],
            height=height or config.SENSOR['camera']['video']['height'],
            frame_rate=frame_rate,
            duration=duration,
        )
    else:
        click.echo('No camera mode selected. Selected either video or image.')


# Main run command
@cli.command()
@click.option(
    '--autonomous', '-a', is_flag=True,
    help='Run arnold in autonomous mode.'
)
@click.option(
    '--voice-command', '-v', is_flag=True,
    help='Run arnold in voice command mode.'
)
@click.option(
    '--manual', '-m', is_flag=True, default=False,
    help='Run arnold in manual mode - controlled via the API.'
)
def run(autonomous, voice_command, manual):
    mode = 'manual'
    if autonomous:
        mode = 'autonomous'
    elif voice_command:
        mode = 'voicecommand'
    elif manual:
        mode = 'manual'

    click.echo(f'Running arnold in {mode} mode.')

    arnold = main.Arnold(mode=mode)
    arnold.run()


cli.add_command(calibrate)
cli.add_command(test)
