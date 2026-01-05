from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
import uvicorn
import numpy as np
import cv2
import base64
import WordSearch

app = FastAPI()
	
@app.post("/solve")
async def Solve(InputFile: str = Form(...)):
	if "," in InputFile:
		_,FileContents = InputFile.split(",", 1)
	else:
		FileContents = InputFile
	FileContents = base64.b64decode(FileContents)
	FileContents = np.frombuffer(FileContents,np.uint8)
	InputImg = cv2.imdecode(FileContents,cv2.IMREAD_COLOR)
	
	try:
		OutputImage = WordSearch.Solve(InputImg)
		return {
			"Image":OutputImage,
			"Ret":True
		}
	except Exception as e:
		print(f"Error: {e}")
		return {
			"Ret":False,
			"Error":str(e)
		}

app.mount("/",StaticFiles(directory="FrontEnd",html=True),name="FrontEnd")