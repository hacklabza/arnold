from pydantic import BaseModel

# API Models
class DrivetrainRequest(BaseModel):
    direction: str = "forward"
    duration: int = 5
    speed: float = 1.0


class SpeakerRequest(BaseModel):
    phrase: str = "No input"
