# 
FROM python:3.9
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
# 
# RUN mkdir/detec_API
WORKDIR /detect_API/app

# 
COPY ./requirements.txt /detect_API/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /detect_API/requirements.txt

# 
COPY ./app /detect_API/app
#COPY /Users/wlin109/Desktop/API_IPS /API_IPS

ENV PORT 8000
EXPOSE 8000
# 
WORKDIR /detect_API/app/
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# uvicorn app.main:app --host 0.0.0.0 --port 8080