# Written by Panagiotis Kourtidis

# =============================================================================
# Import Simple Game Engine Libraries
from game_libraries import *

# Import game resources and shapes
# You can use the shapes module to modify and/or add additonal shapes to
# the game
from game_resources import *
from game_shapes import *

# We need some standard modules for the game
from random import *
import math
import time

# Some needed functions
usleep = lambda x: time.sleep(x/1000000.0)
cotrans = lambda x,y,w: x + (w*y)

# Start the Simple Game Engine
objMyGame = clsSimpleGameEngine("Simple Tiles", 300, 460, 300, 460)

# Load the resources using the object found in game_resources.py
objMyGame.loadResources(listResources)

# =============================================================================
# Game Variables

intGameState = -1 # Indicates what state the game is in
intBoardWidth = 10 # The horizontal number of tiles
intBoardHeight = 22 # The vertical number of tiles
intBlockDimensionX = round(205/intBoardWidth,0) # How large are the block parts (20x20)
intBlockDimensionY = round(440/intBoardHeight,0) # How large are the block parts (20x20)
intBoardXOffset = len(arrShapes)
blnShowMessage = True # Show/hide start game message
intNumLines = 0 # The number of lines the player has
intGameScore = 0 # The current score for the player
arrTileStats = [] # The array that holds stats about each tile
intNextTile = 1 # Holds the next tile to fall
intNextOffsetX = 228 # Where to place the next tile blocks
intNextOffsetY = 280 # Where to place the next tile blocks
intNextSize = 10 # How large should the next tile blocks be
intSelectedTile = 0 # Holds the currently falling tile
arrGameBoard = [] # Holds block information
arrBoardHeight = []
arrActiveTile = []
intLockOffset = 100 # The offset to be used to keep track of the locked blocks
intTotalTilesPlayed = 0
intMoveUpperBound = 200
intNumberOfShapes = len(arrShapes)

intTopSpeed = 100
intBottomSpeed = 500
intFallingTimer = intBottomSpeed # How quickly do the tiles fall
intSpeedIncrease = 20 # How much should we increase the speed for each level
intLevelIncrease = 10 # Every how many lines should we move to the next level

# Create simple timers to control the game timing
# At some point the game clock will be part of the engine
tmrPressSpace = clsSimpleTimer() # Timer for show/hide effect
tmrTileDrop = clsSimpleTimer() # Timer that control the fall rate
tmrForcedFall = clsSimpleTimer() # Timer to control how quickly we can force a fall
tmrKeyDelayUP = clsSimpleTimer()
tmrKeyDelayLEFT = clsSimpleTimer()
tmrKeyDelayRIGHT = clsSimpleTimer()
tmrMenuSpeed = clsSimpleTimer()

# === Menu =========
intSelectedItem = 0

intShapeOriginX = 0
intShapeOriginY = 0

for i in range(20):
    arrTileStats.append(0)


for i in range(intBoardWidth):
	for j in range(intBoardHeight):
		arrGameBoard.append({"x":str(i),"y":str(j),"value":-1})

# ===========================================================================
# Define Game Functions

def drawWord(strWord, intStartPosX, intStartPosY, intCharSizeX, intCharSizeY, intSpacing):
	global objMyGame
	for i in range(len(strWord)):
		chrCharacter = strWord[i].upper()

		objMyGame.drawImage("chr"+chrCharacter, intStartPosX +(i*intSpacing), intStartPosY, intCharSizeX, intCharSizeY)

# =============================================================================
# REVIEWED : Yes
#
def drawPlayArea():
	# ==============================================================
	# Projected tile logic
	# Project each active tile down to project their locked state
	# This information will be used on the next step to draw a
	# shadow for the projected tile

	global objMyGame
	global intGameState
	global intBoardHeight
	global arrGameBoard
	global intLockOffset
	global intBoardWidth
	global intBlockDimensionX
	global intBlockDimensionY
	global arrShapes
	global intNextTile

	global intTopSpeed
	global intBottomSpeed
	global intFallingTimer

	# Calculate game speed
	intSpeed = int((100 * (intBottomSpeed - intFallingTimer)) / (intBottomSpeed - intTopSpeed))

	intProjectedOffset = 1;

	if (intGameState == 1):
		for m in range(intBoardHeight):
			blnFailedProjection = True

			for k in range(len(arrActiveTile)):
				if (arrActiveTile[k]["y"] + intProjectedOffset > (intBoardHeight - 1) or arrGameBoard[cotrans(arrActiveTile[k]["x"],arrActiveTile[k]["y"] + intProjectedOffset,intBoardWidth)]["value"] > (intLockOffset - 1)):
					blnFailedProjection = False

			if (blnFailedProjection == True):
				intProjectedOffset = intProjectedOffset + 1
			else:
				intProjectedOffset =  intProjectedOffset - 1
				break

	objMyGame.drawRect(6, 6, 203, 443, (0,0,0))

	# ==============================================================
	# Scan the playing area and draw the appropriate
	# graphic based on the block definition

	for i in range(intBoardWidth):
		for j in range(intBoardHeight):
			intCurrentBoardLocationValue = arrGameBoard[cotrans(i,j,intBoardWidth)]["value"]

			if (intCurrentBoardLocationValue > intLockOffset - 1):
			    intCurrentBoardLocationValue = intCurrentBoardLocationValue - intLockOffset

			if (intCurrentBoardLocationValue == -1):
				# Empty space

				strTileName = "imgBlockEmpty"

				# If it is a projected tile position then draw the projected block
				for k in range(len(arrActiveTile)):
					if (i == arrActiveTile[k]["x"] and j == (arrActiveTile[k]["y"] + intProjectedOffset)):
						strTileName = "imgBlockEmptyProjection"
				objMyGame.drawImage(strTileName,(i*intBlockDimensionX) + intBoardXOffset, (j*intBlockDimensionY) + intBoardXOffset, intBlockDimensionX, intBlockDimensionY)

			else:
				objShape = arrShapes[intCurrentBoardLocationValue]
				objMyGame.drawImage(objShape["graphic"],(i*intBlockDimensionX) + intBoardXOffset, (j*intBlockDimensionY) + intBoardXOffset, intBlockDimensionX, intBlockDimensionY)

	# ::::::::::::::::::::::::::::::::::::::::::::::::::::
	# The game information



	# *******************************************
	# Next shape display

	drawWord("NEXT",220,260,12,12,12)
	
	objMyGame.drawImage("imgDesign",218,273,66,56,30)

	if (intNextTile > -1 and intNextTile < len(arrShapes)):
        # Empty space
		objShape = arrShapes[intNextTile]

		intMinNextY = 10
		intMinNextX = 10

		for i in range(len(objShape["initial_placement"])):
			if (objShape["initial_placement"][i]["y"] < intMinNextY):
				intMinNextY = objShape["initial_placement"][i]["y"]
			if (objShape["initial_placement"][i]["x"] < intMinNextX):
				intMinNextX = objShape["initial_placement"][i]["x"]

		for i in range(len(objShape["initial_placement"])):
			objMyGame.drawImage(objShape["graphic"], ((objShape["initial_placement"][i]["x"] - intMinNextX) * intNextSize) + intNextOffsetX, ((objShape["initial_placement"][i]["y"] - intMinNextY) * intNextSize) + intNextOffsetY, intNextSize, intNextSize)

	# *******************************************
	# Lines display

	drawWord("LINES",220,25,12,12,12)
	objMyGame.drawImage("imgDesign",218,38,66,18,30)

	strNumLines = '00000' + str(intNumLines)
	strNumLines = strNumLines[-6:]

	for i in range(6):
		objMyGame.drawImage("img00" + strNumLines[i], 220+(i*10), 40, 10, 12)

	# *******************************************
	# Score display
	
	drawWord("SCORE",220,75,12,12,12)
	objMyGame.drawImage("imgDesign",218,88,66,18,30)

	strGameScore = '00000' + str(intGameScore)
	strGameScore = strGameScore[-6:]

	for i in range(6):
		objMyGame.drawImage("img00" + strGameScore[i], 220+(i*10), 90, 10, 12)

	# *******************************************
	# Level display

	drawWord("LEVEL",220,125,12,12,12)
	objMyGame.drawImage("imgDesign",218,138,66,18,30)

	# Draw the game level
	strGameLevel = '00000' + str(intGameLevel)
	strGameLevel = strGameLevel[-6:]

	for i in range(6):
		objMyGame.drawImage("img00" + strGameLevel[i], 220+(i*10), 140, 10, 12)

	# *******************************************
	# Stats display
	
	drawWord("STATS",220,175,12,12,12)
	
	objMyGame.drawImage("imgDesign",218,188,66,len(arrShapes) * 8,30)

	intTilePercent = 0
	
	if (intTotalTilesPlayed > 0):
		for i in range(len(arrShapes)):
			intTilePercent = 100 * (arrTileStats[i] / intTotalTilesPlayed);
			statColor = arrShapes[i]["color"];
			objMyGame.drawImage(arrShapes[i]["graphic"],223 ,(i*7) + 193, intTilePercent, 4)


	# Draw the PansaCreations and Game title Logo
	objMyGame.drawImage("imgLogoPansa",208,340,20,100)
	objMyGame.drawImage("imgLogo", 9, 10, 202, 50);

# =============================================================================
# REVIEWED : Yes
#
def resetGame():

	global arrShapes
	global intGameLevel
	global intBoardWidth
	global intBoardHeight
	global arrGameBoard
	global intTotalTilesPlayed
	global arrTileStats
	global tmrPressSpace
	global tmrTileDrop
	global intGameScore
	global intNumLines
	global intFallingTimer
	global intNextTile

	# SETUP THE NEXT TILE
	intNextTile = randint(0, intNumberOfShapes-1)

	# RESET THE LEVEL
	intGameLevel = 0

	# RESET DATA ON GAME BOARD
	for i in range(intBoardWidth):
		for j in range(intBoardHeight):
			arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] = -1

	# RESET THE STATS ARRAY
	intTotalTilesPlayed = len(arrTileStats)
	for i in range(len(arrTileStats)):
		arrTileStats[i] = 1

	# RESET GAME TIMERS
	tmrPressSpace.resetTimer()
	tmrTileDrop.resetTimer()

	intGameScore = 0
	intNumLines = 0
	intFallingTimer = intBottomSpeed

# =============================================================================
# REVIEWED : Yes
#
def setActiveTilePositions():

	global arrActiveTile
	global intBoardWidth
	global intBoardHeight
	global arrGameBoard

	# Empty the array keeping track of the positions occupied by the active tile
	arrActiveTile.clear()

	for i in range(intBoardWidth):
		for j in range(intBoardHeight):
			if (arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] < intNumberOfShapes):
				arrActiveTile.append({"x":i,"y":j})

# =============================================================================
# REVIEWED : Yes
#
def selectTile():
	# Initialize the origin of the new block
	# This can depend on the game area width

	global intShapeOriginX
	global intShapeOriginY
	global intSelectedTile
	global intNextTile
	global arrTileStats
	global intTotalTilesPlayed
	global arrShapes
	global arrGameBoard
	global intGameState

	intShapeOriginX = 2
	intShapeOriginY = 0

	# Set the current block and select the next
	intSelectedTile = intNextTile;
	intNextTile = randint(0, len(arrShapes) - 1)

	# Keep some stats about the tiles
	arrTileStats[intSelectedTile] = arrTileStats[intSelectedTile] + 1
	intTotalTilesPlayed = intTotalTilesPlayed + 1

	# Initialize the block on the playing area
	# console.log(intSelectedTile);
	objShape = arrShapes[intSelectedTile]

	for i in range(len(arrShapes[intSelectedTile]["initial_placement"])):
		intPlayAreaPosX = arrShapes[intSelectedTile]["initial_placement"][i]["x"] + intShapeOriginX
		intPlayAreaPosY = arrShapes[intSelectedTile]["initial_placement"][i]["y"]

		if (arrGameBoard[cotrans(intPlayAreaPosX,intPlayAreaPosY,intBoardWidth)]["value"] != -1):
			intGameState = 0
			break
		else:
			arrGameBoard[cotrans(intPlayAreaPosX,intPlayAreaPosY,intBoardWidth)]["value"] = intSelectedTile

	# Record the active positions
	setActiveTilePositions()


# =============================================================================
# REVIEWED : Yes
#
def processFall():

	global intBoardWidth
	global intBoardHeight
	global arrGameBoard
	global intShapeOriginY
	global intGameScore
	global intLockOffset
	global intNumLines
	global intFallingTimer

	global intLevelIncrease
	global intSpeedIncrease
	global intGameLevel

	# Check if any active tile cannot move down
	blnTileStopped = False;

	for i in range(intBoardWidth):
		for j in range(intBoardHeight):
			if (arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] < intNumberOfShapes):
				if (j > intBoardHeight - 2):
					blnTileStopped = True;
				elif (arrGameBoard[cotrans(i,j+1,intBoardWidth)]["value"] > 9):
					blnTileStopped = True

	# No blocking so moving all active tiles down
	if (blnTileStopped == False):
		for i in range(intBoardWidth):
			for j in reversed(range(intBoardHeight)):
				if (arrGameBoard[cotrans(i,j-1,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j-1,intBoardWidth)]["value"] < intNumberOfShapes):
					arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] = arrGameBoard[cotrans(i,j-1,intBoardWidth)]["value"] + intMoveUpperBound
					arrGameBoard[cotrans(i,j-1,intBoardWidth)]["value"] = -1
		intShapeOriginY = intShapeOriginY + 1

		# Finalize the moves
		for i in arrGameBoard:
			if (i["value"] >= intMoveUpperBound):
				i["value"] = i["value"] - intMoveUpperBound

	# We need to lock the tiles since we are blocked
	else:
		# Lock the tiles by adding an offset value
		for i in range(intBoardWidth):
			for j in range(intBoardHeight):
				if (arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] < intNumberOfShapes):
					# alert("FREEZING")
					arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] = arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] + intLockOffset


		# Add a single point to our score
		intGameScore = intGameScore + 1

		# Check for lines made and remove them
		intLinesInRow = 0
		for j in range(intBoardHeight):
			blnFoundLine = True;
			for i in range(intBoardWidth):
				if (arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] == -1):
					blnFoundLine = False
					break

			# We found a line so we need to remove it
			if (blnFoundLine == True):

				# Keep track of the number of lines
				intNumLines = intNumLines + 1

				# Check for level and speed increase thresholds
				if (intNumLines % intLevelIncrease == 0):
					intFallingTimer = intFallingTimer - intSpeedIncrease
					intGameLevel = intGameLevel + 1

				# Add a multiplier for the score calculation
				intLinesInRow = intLinesInRow + 1

				# Move all tiles from our current position down
				for k in reversed(range(1,j+1)):
					for l in range(intBoardWidth):
						arrGameBoard[cotrans(l,k,intBoardWidth)]["value"] = arrGameBoard[cotrans(l,k-1,intBoardWidth)]["value"]
						arrGameBoard[cotrans(l,k-1,intBoardWidth)]["value"] = -1

		intGameScore = intGameScore + (4 * intLinesInRow)
		selectTile()

	setActiveTilePositions()

def processLateral(intMoveType):

	global intBoardWidth
	global intBoardHeight
	global arrGameBoard
	global intShapeOriginX
	global arrActiveTile

	intPosXMove = 0
	iterRange = iter(arrActiveTile)

	if (intMoveType == 1): # LEFT
		intPosXMove = -1
	elif (intMoveType == 2): # RIGHT
		intPosXMove = 1
		iterRange = iter(reversed(arrActiveTile))

	# Check all active tiles and see if anything in blocking them
	blnLegalMove = True

	for i in arrActiveTile:
		intPosX = i["x"]
		intPosY = i["y"]
		intPosMoveToX = intPosX + intPosXMove
		if (intPosMoveToX > -1 and intPosMoveToX < intBoardWidth):
			intTileAtDestination = arrGameBoard[cotrans(intPosMoveToX,intPosY,intBoardWidth)]["value"]
			if (intTileAtDestination > intNumberOfShapes):
				blnLegalMove = False
				break
		else:
			blnLegalMove = False
			break

	if (blnLegalMove == True):
		for i in iterRange:
			intGamePos = cotrans(i["x"],i["y"],intBoardWidth)
			intGamePosTo = cotrans(i["x"] + intPosXMove,i["y"],intBoardWidth)
			arrGameBoard[intGamePosTo]["value"] = arrGameBoard[intGamePos]["value"]
			arrGameBoard[intGamePos]["value"] = -1
		intShapeOriginX = intShapeOriginX + intPosXMove

	setActiveTilePositions()

def rotateTile():
	rotateShape()
	setActiveTilePositions()


def rotateShape():

	global intSelectedTile
	global arrShapes
	global arrActiveTile
	global arrGameBoard
	global intShapeOriginX
	global intShapeOriginY

	blnCanRotate = True
	objShape = arrShapes[intSelectedTile]
	angle = (math.pi * 90) / 180
	arrNewPositions = []

	if (objShape["rotates"] == True):

		for k in range(len(arrActiveTile)):
			center_x = intShapeOriginX + objShape["center_x"]
			center_y = intShapeOriginY + objShape["center_y"]

			rotated_pos_x = int(round((math.cos(angle) * (arrActiveTile[k]["x"] - center_x)) - (math.sin(angle) * (arrActiveTile[k]["y"] - center_y)) + center_x))
			rotated_pos_y = int(round((math.sin(angle) * (arrActiveTile[k]["x"] - center_x)) + (math.cos(angle) * (arrActiveTile[k]["y"] - center_y)) + center_y))

			if (rotated_pos_x < 0 or rotated_pos_x > (intBoardWidth - 1)):
				blnCanRotate = False
				break

			if (arrGameBoard[cotrans(rotated_pos_x,rotated_pos_y,intBoardWidth)]["value"] == -1 or arrGameBoard[cotrans(rotated_pos_x,rotated_pos_y,intBoardWidth)]["value"] == intSelectedTile):
				arrNewPositions.append({"x":rotated_pos_x,"y":rotated_pos_y});
			else:
				blnCanRotate = False
				break

		if (blnCanRotate == True):
			for k in range(len(arrActiveTile)):
				arrGameBoard[cotrans(arrActiveTile[k]["x"],arrActiveTile[k]["y"],intBoardWidth)]["value"] = -1
			for k in range(len(arrNewPositions)):
				arrGameBoard[cotrans(arrNewPositions[k]["x"],arrNewPositions[k]["y"],intBoardWidth)]["value"] = intSelectedTile


resetGame()

# ===========================================================================
# Start the Game Loop

objMyGame.resizeDisplay()

blnRunning = True
		
while blnRunning:

	# Clear the Screen
	objMyGame.displayClear()
	
	# Draw the background
	objMyGame.drawRect(0, 0, 300, 460, (50,50,50))

	# Check what game state we are in and run the corresponding code

	match intGameState:

		# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
		# Game main menu logic
		# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		case -1:

			# Draw the game title
			objMyGame.drawImage("imgLogo", 9, 10, 278, 60)

			# Draw a couple of backgrounds
			objMyGame.drawRect(12, 90, 270, 360, (20,20,20))
			objMyGame.drawRect(30, 108, 236, 320, (0,0,0))

			# Draw the menu options
			drawWord("NEW GAME",70,130,18,18,18)
			drawWord("LEADERS",70,180,18,18,18)
			drawWord("QUIT",70,380,18,18,18)

			# Check the user input and take action
			if (objMyGame.checkKeyStatus("DOWN") and tmrMenuSpeed.checkTimePassed(100)):
				intSelectedItem = (intSelectedItem + 1)
				if (intSelectedItem > 2):
					intSelectedItem = 0
				tmrMenuSpeed.resetTimer()

			elif (objMyGame.checkKeyStatus("UP") and tmrMenuSpeed.checkTimePassed(100)):
				intSelectedItem = (intSelectedItem - 1)
				if (intSelectedItem < 0):
					intSelectedItem = 2
				tmrMenuSpeed.resetTimer()

			if (objMyGame.checkKeyStatus("RETURN") and tmrMenuSpeed.checkTimePassed(100)):
				if (intSelectedItem == 0):
					intGameState = 0
				elif (intSelectedItem == 1):
					break
				elif (intSelectedItem == 2):
					break

			# Draw a select box based on the selected menu item
			if (intSelectedItem == 0):
				objMyGame.drawImage("imgDesign",44,120,210,40,30)
			elif (intSelectedItem == 1):
				objMyGame.drawImage("imgDesign",44,170,210,40,30)
			elif (intSelectedItem == 2):
				objMyGame.drawImage("imgDesign",44,370,210,40,30)

			
			# Draw the PansaCreations logo
			objMyGame.drawImage("imgLogoPansa",270,300,20,100)

		# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
		# Ready to play - wait for player to start the game by pressing space
		# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		case 0: # READY TO PLAY - PRESS KEY OR TOUCH /////////////////////////

			# Draw the main SimpleBlocks play area
			drawPlayArea();

			# Logic to show/hide the start game message
			if ((blnShowMessage and tmrPressSpace.checkTimePassed(800)) or (not blnShowMessage and tmrPressSpace.checkTimePassed(300))):
				blnShowMessage = not blnShowMessage
				tmrPressSpace.resetTimer()

			if (blnShowMessage == True):
				objMyGame.drawImage("imgStartGameLogo", 10, 170, 192, 40)

			if (objMyGame.checkKeyStatus('SPACE')):
				resetGame()
				selectTile()
				intGameState = 1

		# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
		# The main game loop - the player pays the game
		# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

		case 1: # PLAYING THE GAME ///////////////////////////////////////////

			setActiveTilePositions()

			# Check the timer that control the fall speed
			# if the timer expired then move the dropping tile down
			if (tmrTileDrop.checkTimePassed(intFallingTimer)):
				tmrTileDrop.resetTimer()
				processFall()

			# Check the user input and take action
			if (objMyGame.checkKeyStatus("DOWN") and tmrForcedFall.checkTimePassed(30)):
				processFall()
				tmrForcedFall.resetTimer()

			if (objMyGame.checkKeyStatus("LEFT")):
				if (tmrKeyDelayLEFT.checkTimePassed(100)):
					tmrKeyDelayLEFT.resetTimer()
					processLateral(1)


			if (objMyGame.checkKeyStatus("RIGHT")):
				if (tmrKeyDelayRIGHT.checkTimePassed(100)):
					tmrKeyDelayRIGHT.resetTimer()
					processLateral(2)

			if (objMyGame.checkKeyStatus("UP")):
				if (tmrKeyDelayUP.checkTimePassed(100)):
					tmrKeyDelayUP.resetTimer()
					rotateTile()

			# Draw the playing area
			drawPlayArea()

	blnRunning = objMyGame.processEvents()
	
	objMyGame.displayUpdate()
	pygame.time.wait(10)
