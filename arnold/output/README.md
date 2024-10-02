# Output

Arnold is equipped with a number of output devices each of which is split into it's own module and main class.

## Speaker

### Setup

This should work out of the box once the speaker is connected to the rpi.

### Config

Update in `arnold/config.py`

```python
OUTPUT = {
    'speaker': {
        'rate': 150,
        'volume': 1.0
    },
    ...
}
```

### Testing

```bash
arnold test speaker --phrase "Hello World!"
```

### Usage

```python
from arnold.output import speaker

speaker = speaker.Speaker()
speaker.say("Hello World!")
```
