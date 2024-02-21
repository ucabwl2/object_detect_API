import uvicorn
import nest_asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from PIL import Image
from io import BytesIO
from detect import run
from typing import List


from contextlib import asynccontextmanager
from fastapi import FastAPI
from models.common import DetectMultiBackend
from utils.torch_utils import select_device, smart_inference_mode
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    device = select_device(device='')
    ml_models["yolov5s"] = DetectMultiBackend(weights=ROOT / 'yolov5s.pt', device=device, dnn=False, data=ROOT / 'data/coco128.yaml', fp16=False)
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


# Assign an instance of the FastAPI class to the variable "app".
# You will interact with your api using this instance.
app = FastAPI(title='Deploying a ML Model with FastAPI',lifespan=lifespan)

# Pydantic models for the API
class AnimalDetectionInput(BaseModel):
    image_url: str
    species_type: str
    user_id: str

class AnimalDetectionOutput(BaseModel):
    cropped_image_url: Optional[str]
    is_detected_species: List[bool]
    user_id: str

# By using @app.get("/") you are allowing the GET method to work for the / endpoint.
@app.get("/")
def home():
    return "Congratulations! Your API is working as expected. Now head over to http://localhost:8080/docs."


    

# Endpoint for animal detection
@app.post("/detect_animal", response_model=AnimalDetectionOutput)
async def detect_animal(input: AnimalDetectionInput):
    try:
        input_img_path = input.image_url
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error opening image file: {e}")
    
    model = ml_models["yolov5s"]

    output_image_path, output_label_dict = run(model = model, source=input_img_path)
    result_bol = [input.species_type in values for values in output_label_dict.values()]

    # Ensure the output_image_path is a string. If it's a Path object, convert it to a string
    cropped_image_url = str(output_image_path)

    return AnimalDetectionOutput(
        cropped_image_url=cropped_image_url,
        is_detected_species=result_bol,
        user_id=input.user_id
    )




# if __name__ == "__main__":
#   # Allows the server to be run in this interactive environment
#     nest_asyncio.apply()

# #   # Host depends on the setup you selected (docker or virtual env)
# # #   host = "0.0.0.0" if os.getenv("DOCKER-SETUP") else "127.0.0.1"


# #   Spin up the server!    
#     uvicorn.run(app, host="127.0.0.1", port=8080)