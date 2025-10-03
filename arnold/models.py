from pydantic import BaseModel


# Main models
class ModeRequest(BaseModel):
    mode: str = "manual"


# Motion models
class DrivetrainRequest(BaseModel):
    direction: str = "forward"
    duration: int = 5
    speed: float = 1.0

# Output models
class SpeakerRequest(BaseModel):
    phrase: str = "No input"
