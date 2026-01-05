#Imports
import cv2
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import os
import base64

#Set Device
if torch.cuda.is_available():
	device = torch.device("cuda:0")
else:
	device = torch.device("cpu")

print(f"Selected Device: {device}")

#Define architecture
class EMNISTModel(nn.Module):
	def __init__(self):
		super(EMNISTModel,self).__init__()

		#Layer1
		self.conv1 = nn.Conv2d(in_channels=1,out_channels=32,kernel_size=3,padding=1,bias=False)#Size does not change
		self.bn1 = nn.BatchNorm2d(num_features=32)
		self.relu1 = nn.ReLU()
		self.pool1 = nn.MaxPool2d(kernel_size=2)#Size halves into 14x14

		#Layer2
		self.conv2 = nn.Conv2d(in_channels=32,out_channels=32,kernel_size=3,padding=1,bias=False)
		self.bn2 = nn.BatchNorm2d(num_features=32)
		self.relu2 = nn.ReLU()

		#Layer3
		self.conv3 = nn.Conv2d(in_channels=32,out_channels=64,kernel_size=3,padding=1,bias=False)
		self.bn3 = nn.BatchNorm2d(num_features=64)
		self.relu3 = nn.ReLU()

		#Layer4
		self.conv4 = nn.Conv2d(in_channels=64,out_channels=64,kernel_size=3,padding=1,bias=False)
		self.bn4 = nn.BatchNorm2d(num_features=64)
		self.relu4 = nn.ReLU()

		#Layer5
		self.conv5 = nn.Conv2d(in_channels=64,out_channels=64,kernel_size=3,padding=1,bias=False)
		self.bn5 = nn.BatchNorm2d(num_features=64)
		self.relu5 = nn.ReLU()
		self.pool2 = nn.MaxPool2d(kernel_size=2)#Size halves into 7x7

		#FlattenLayer
		self.flatten = nn.Flatten()

		#Layer6
		self.fc1 = nn.Linear(in_features=64*7*7,out_features=256)
		self.relu6 = nn.ReLU()

		#Layer7
		self.fc2 = nn.Linear(in_features=256,out_features=64)
		self.relu7 = nn.ReLU()

		#DropoutLayer
		self.dropout = nn.Dropout(p=0.2)

		#Layer8
		self.fc3 = nn.Linear(in_features=64,out_features=26)

	def forward(self,x):

		#Pass through Layer1
		x = self.pool1(self.relu1(self.bn1(self.conv1(x))))

		#Pass through Layer2
		x = self.relu2(self.bn2(self.conv2(x)))

		#Pass through Layer3
		x = self.relu3(self.bn3(self.conv3(x)))

		#Pass through Layer4
		x = self.relu4(self.bn4(self.conv4(x)))

		#Pass through Layer5
		x = self.pool2(self.relu5(self.bn5(self.conv5(x))))

		#Pass through Layer5
		x = self.flatten(x)

		#Pass through Layer6
		x = self.relu6(self.fc1(x))

		#Pass through Layer7
		x = self.relu7(self.fc2(x))

		#Pass through DropoutLayer
		x = self.dropout(x)

		#Pass through Layer7
		x = self.fc3(x)

		#Return Prediction
		return x

#Load Model
model = EMNISTModel().to(device)
ScriptDir = os.path.dirname(os.path.abspath(__file__))
try:
	ModelPath = os.path.join(ScriptDir,"./EMNISTModel.pth")
	ModelPath = os.path.normpath(ModelPath)
	model.load_state_dict(torch.load(ModelPath, map_location=torch.device('cpu')))
	model.eval()
except FileNotFoundError:
	print("Model not found")

# Transform
Transform = transforms.Compose(
	[
		transforms.Grayscale(num_output_channels=1),
		transforms.ToTensor(),
  		transforms.Normalize((0.5,),(0.5,)),
	])

#Kernels
Kernel = cv2.getStructuringElement(shape=cv2.MORPH_RECT,ksize=(2,2))
NewHeight = 800

#Load WordList
Words = set()
try:
	WordListPath = os.path.join(ScriptDir,"./EnglishWords.txt")
	WordListPath = os.path.normpath(WordListPath)
	with open(WordListPath,'r',encoding='UTF-8') as file:
		while line := file.readline():
			Words.add(line.strip())
except FileNotFoundError:
	print("WordList not found")

#Rays
Rays = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(-1,-1),(1,-1)]
#Function

def Process(InputImg):
	Height,Width = InputImg.shape[:2]
	if Height > NewHeight:
		Ratio = NewHeight/float(Height)
		NewWidth = int(Ratio*Width)
		InputImg = cv2.resize(InputImg , (NewWidth,NewHeight) , interpolation=cv2.INTER_AREA)
	_,InputImgEncode = cv2.imencode('.png',InputImg)
	InputImgEncode = base64.b64encode(InputImgEncode).decode('utf-8')
	InputImgEncode = "data:image/png;base64,"+InputImgEncode
	return InputImgEncode

def Solve(InputImg):
	InputImgProcessed = cv2.cvtColor(InputImg , cv2.COLOR_BGR2GRAY)
	InputImgProcessed = cv2.GaussianBlur(src=InputImgProcessed,ksize=(3,3),sigmaX=0,sigmaY=0)
	_,InputImgProcessed = cv2.threshold(src=InputImgProcessed,thresh=0,maxval=255,type=cv2.THRESH_OTSU+cv2.THRESH_BINARY_INV)
	InputImgProcessed = cv2.morphologyEx(src=InputImgProcessed,op=cv2.MORPH_CLOSE,kernel=Kernel)
	OutputOverlayImg = InputImg.copy()

	#Detect Contours of each letter and place them in rows

	contours,_ = cv2.findContours(InputImgProcessed,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	ImgHist = np.zeros(InputImg.shape[0],np.int32)
	Boxes = []

	#Contours exist
	if len(contours) > 0:
		AvgArea = sum(cv2.contourArea(contour) for contour in contours)/len(contours)
	else:
		AvgArea = 0

	for cnt in contours:
		if cv2.contourArea(cnt) < 0.1*AvgArea:
			continue
		x,y,w,h = cv2.boundingRect(cnt)
		Boxes.append((x,y,w,h))

	for box in Boxes:
		for i in range(box[1],box[1]+box[3]):
			ImgHist[i] += 1

	HistThresh = max(ImgHist)*0.5 #50%
	RowRanges = []
	InRow = False
	StartY = 0

	for y in range(len(ImgHist)):
		#Enter Row
		if ImgHist[y] > HistThresh and InRow == False:
			StartY = y
			InRow = True
		#Exit Row
		elif ImgHist[y] <= HistThresh and InRow == True:
			RowRanges.append((StartY,y))
			InRow = False

	PuzzleCoords = [[] for _ in range(len(RowRanges))]

	for box in Boxes:
		YCenter = box[1]+box[3]/2
		for rowind in range(len(RowRanges)):
			if RowRanges[rowind][0]<=YCenter<=RowRanges[rowind][1]:
				PuzzleCoords[rowind].append(box)

	for row in PuzzleCoords:
		row.sort(key=lambda x: x[0])

	#Pass through model
		
	Puzzle = []
	LetterWidth = None

	for RowCoords in PuzzleCoords:
		Row = []
		for box in RowCoords:
			x,y,w,h = box
			if not LetterWidth:
				LetterWidth = w
			
			CellImage = InputImgProcessed[y:y+h , x:x+w]
			CellImage = Image.fromarray(CellImage)
			CellImage.thumbnail((24,24), Image.Resampling.LANCZOS)

			PillowFrame = Image.new("L", (28, 28), 0)
			PillowFrame.paste(CellImage, ((28 - CellImage.size[0]) // 2, (28 - CellImage.size[1]) // 2))

			CellImage = Transform(PillowFrame)
			CellImage = CellImage.unsqueeze(0)
			CellImage = CellImage.to(device)
			with torch.no_grad():
				output = model(CellImage)
				_,prediction = torch.max(output,dim=1)
				Num = prediction.item()
				Row.append(chr(ord('A')+Num))
				
		Puzzle.append(Row)

	#Find Words

	WordsFound = {}

	for row in range(len(Puzzle)):
		for col in range(len(Puzzle[row])):
			for RayRow,RayCol in Rays:
				CurrentWord = ""
				CurrentRow,CurrentCol = row,col
				while (True):
					if ((0<=CurrentRow<len(Puzzle))and(0<=CurrentCol<len(Puzzle[row]))):
						CurrentWord += Puzzle[CurrentRow][CurrentCol]
						if (CurrentWord in Words):
							StartCoords = (row,col)
							CurrentCoords = (CurrentRow,CurrentCol)
							if StartCoords > CurrentCoords:
								StartCoords,CurrentCoords = CurrentCoords,StartCoords
							if CurrentWord not in WordsFound:
								WordsFound[CurrentWord] = [(StartCoords,CurrentCoords)]
							elif ((StartCoords,CurrentCoords) not in WordsFound[CurrentWord]):
								WordsFound[CurrentWord].append((StartCoords,CurrentCoords))

						CurrentRow += RayRow
						CurrentCol += RayCol
					else:
						break

	#Clean substrings

	OccupancyMatrix = np.zeros((len(Puzzle),len(Puzzle[0])),np.int8)
	WordsFound = sorted(WordsFound.items(),key=lambda word:len(word[0]),reverse=True)
	FilteredWords = {}

	for word,coords in WordsFound:
		for instance in coords:
			StartCoords,EndCoords = instance
			StartRow,StartCol = StartCoords
			EndRow,EndCol = EndCoords
			Occupied = True
			while ((StartRow,StartCol)!=(EndRow,EndCol)):
				if (OccupancyMatrix[StartRow][StartCol] == 0):
					Occupied = False

				if (StartRow<EndRow):
					StartRow += 1
				elif (StartRow>EndRow):
					StartRow -= 1

				if (StartCol<EndCol):
					StartCol += 1
				elif (StartCol>EndCol):
					StartCol -= 1
			if (OccupancyMatrix[StartRow][StartCol] == 0):
					Occupied = False
					
			if (not Occupied):
				StartRow,StartCol = StartCoords
				if (word not in FilteredWords):
					FilteredWords[word] = []
				FilteredWords[word].append(instance)
				while ((StartRow,StartCol)!=(EndRow,EndCol)):
					OccupancyMatrix[StartRow][StartCol] = 1
					if (StartRow<EndRow):
						StartRow += 1
					elif (StartRow>EndRow):
						StartRow -= 1

					if (StartCol<EndCol):
						StartCol += 1
					elif (StartCol>EndCol):
						StartCol -= 1
				OccupancyMatrix[StartRow][StartCol] = 1

	#Highlight words

	for word,coords in FilteredWords.items():
		for instance in coords:
			StartInd,EndInd = instance
			StartCoords,EndCoords = PuzzleCoords[StartInd[0]][StartInd[1]],PuzzleCoords[EndInd[0]][EndInd[1]]
			StartCenter = ((StartCoords[0]+StartCoords[2]//2),(StartCoords[1]+StartCoords[3]//2))
			EndCenter = ((EndCoords[0]+EndCoords[2]//2),(EndCoords[1]+EndCoords[3]//2))
			color = tuple(np.random.random(size=3)*256)
			width = (StartCoords[2]+EndCoords[2])//2
			cv2.line(img=OutputOverlayImg,pt1=StartCenter,pt2=EndCenter,color=color,thickness=width,lineType=cv2.LINE_AA)

	InputImg = cv2.addWeighted(src1=InputImg,alpha=0.7,src2=OutputOverlayImg,beta=0.3,gamma=0)
	
	_,InputImgEncode = cv2.imencode('.png',InputImg)
	InputImgEncode = base64.b64encode(InputImgEncode).decode('utf-8')
	InputImgEncode = "data:image/png;base64,"+InputImgEncode
	return InputImgEncode