import json, os, copy

from fastapi import FastAPI, UploadFile, File
from optimizer import Optimizer
from fastapi.responses import JSONResponse, Response
import librosa

app = FastAPI()

@app.get("/")
def welcome():
    return {"message": "Welcome to the Optimizer API"}

@app.post("/sequence")
def solution(times, balls:int, loop:bool, throwType:bool):
    times = list(map(float, str(times).replace('[','').replace(']', '').replace(',', ' ').split()))

    op = Optimizer(copy.deepcopy(times), balls, loop, int(throwType))
    prob_sol = op.solve()
    sol = op.get_solution()
    print(sol)
    result = {
        'prob_sol': prob_sol,
        'times': times,
        'balls': balls,
        'loop': loop,
        'distribution_balls': sol
    }

    return JSONResponse(
        status_code=200,
        content=result,
        headers={
            'access-control-allow-origin': '*',
        }
    )

@app.post("/sound")
def solution_with_sound(balls:int, loop:bool, throwType:bool, file: UploadFile = File(...)):
    # write file to disk
    with open(file.filename, 'wb') as f:
        f.write(file.file.read())
    
    # load audio
    y, sr = librosa.load(file.filename)
    onset_frames = librosa.onset.onset_detect(y, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
    onset_times = list(librosa.frames_to_time(onset_frames))

    op = Optimizer(copy.deepcopy(onset_times), balls, loop, int(throwType))
    prob_sol = op.solve()
    sol = op.get_solution()

    result = {
        'prob_sol': prob_sol,
        'times': onset_times,
        'balls': balls,
        'loop': loop,
        'distribution_balls': sol
    }

    # delete file from disk
    os.remove(file.filename)

    return JSONResponse(
        status_code=200,
        content=result,
        headers={
            'access-control-allow-origin': '*',
        }
    )

