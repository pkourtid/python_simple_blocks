# Written by Panagiotis Kourtidis

# =============================================================================
# Import Simple Game Engine Libraries
from game_libraries import *
from game_resources import *
from game_shapes import *

from random import *

import math
import time

usleep = lambda x: time.sleep(x/1000000.0)
cotrans = lambda x,y,w: x + (w*y)

objMyGame = clsSimpleGameEngine("Simple Tiles", 300, 460, 300, 460)
objMyGame.loadResources(listResources)

# =============================================================================
# Game Variables

intGameState = 0 # Indicates what state the game is in
intBoardWidth = 10 # The horizontal number of tiles
intBoardHeight = 22 # The vertical number of tiles
intBlockDimension = 20 # How large are the block parts (20x20)
intBoardXOffset = 10;
blnShowMessage = True # Show/hide start game message
tmrPressSpace = clsSimpleTimer() # Timer for show/hide effect
intNumLines = 0 # The number of lines the player has
intGameScore = 0 # The current score for the player
arrTileStats = [] # The array that holds stats about each tile
tmrTileDrop = clsSimpleTimer() # Timer that control the fall rate
intNextTile = 1 # Holds the next tile to fall
intNextOffsetX = 220 # Where to place the next tile blocks
intNextOffsetY = 243 # Where to place the next tile blocks
intNextSize = 16 # How large should the next tile blocks be
intSelectedTile = 0 # Holds the currently falling tile
intFallingTimer = 500 # How quickly do the tiles fall
arrGameBoard = [] # Holds block information
arrBoardHeight = []
arrActiveTile = []
tmrForcedFall = clsSimpleTimer() # Timer to control how quickly we can force a fall 
intLockOffset = 100 # The offset to be used to keep track of the locked blocks
intTotalTilesPlayed = 0
intMoveUpperBound = 200

intShapeOriginX = 0
intShapeOriginY = 0

for i in range(20):
    arrTileStats.append(0)


for i in range(intBoardWidth):
	for j in range(intBoardHeight):
		arrGameBoard.append({"x":str(i),"y":str(j),"value":-1})

print("The array value = " + str(arrGameBoard[3]["value"]))

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
def drawSimpleBlocksPlayArea():
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
	global intBlockDimension
	global arrShapes
	global intNextTile

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
				objMyGame.drawImage(strTileName,(i*intBlockDimension) + intBoardXOffset, (j*intBlockDimension) + intBoardXOffset, intBlockDimension + 1, intBlockDimension + 1)

			else:
				objShape = arrShapes[intCurrentBoardLocationValue]
				objMyGame.drawImage(objShape["graphic"],(i*intBlockDimension) + intBoardXOffset, (j*intBlockDimension) + intBoardXOffset, intBlockDimension + 1, intBlockDimension + 1, 50)

	# ::::::::::::::::::::::::::::::::::::::::::::::::::::
	# The game information

	if (intNextTile > -1 and intNextTile < len(arrShapes)):
        # Empty space
		objShape = arrShapes[intNextTile]

		for i in range(len(objShape["initial_placement"])):
			objMyGame.drawImage(objShape["graphic"], (objShape["initial_placement"][i]["x"] * intNextSize) + intNextOffsetX, (objShape["initial_placement"][i]["y"] * intNextSize) + intNextOffsetY, intNextSize, intNextSize)

	objMyGame.drawImage("imgLogo", 7, 10, 206, 50);

	strNumLines = '00000' + str(intNumLines)
	strNumLines = strNumLines[-6:]

	for i in range(6):
		objMyGame.drawImage("img00" + strNumLines[i], 220+(i*10), 40, 10, 12)

	strGameScore = '00000' + str(intGameScore)
	strGameScore = strGameScore[-6:]

	for i in range(6):
		objMyGame.drawImage("img00" + strGameScore[i], 220+(i*10), 90, 10, 12)


	intTilePercent = 0
	if (intTotalTilesPlayed > 0):
		for i in range(len(arrShapes)):
			intTilePercent = 100 * (arrTileStats[i] / intTotalTilesPlayed);
			statColor = arrShapes[i]["color"];
			objMyGame.drawImage(arrShapes[i]["graphic"],223 ,(i*7) + 155, intTilePercent, 4)


	drawWord("LINES",220,25,12,12,12)
	drawWord("SCORE",220,75,12,12,12)
	drawWord("STATS",220,135,12,12,12)
	drawWord("NEXT",220,220,12,12,12)

	objMyGame.drawImage("imgDown",232,400,44,40)
	objMyGame.drawImage("imgUp",232,330,44,40)
	objMyGame.drawImage("imgLeft",212,365,40,40)
	objMyGame.drawImage("imgRight",256,365,40,40)

# =============================================================================
# REVIEWED : Yes
#
def resetGame():

	global arrShapes
	global intLevel
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
	intNextTile = randint(0, len(arrShapes)-1)
	print(intNextTile)

	# RESET THE LEVEL
	intLevel = 0;

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
	intFallingTimer = 500

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
			if (arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] < 10):
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

	# Check if any active tile cannot move down
	blnTileStopped = False;

	for i in range(intBoardWidth):
		for j in range(intBoardHeight):
			if (arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] < 10):
				if (j > intBoardHeight - 2):
					blnTileStopped = True;
				elif (arrGameBoard[cotrans(i,j+1,intBoardWidth)]["value"] > 9):
					blnTileStopped = True

	# No blocking so moving all active tiles down
	if (blnTileStopped == False):
		for i in range(intBoardWidth):
			for j in reversed(range(intBoardHeight)):
				if (arrGameBoard[cotrans(i,j-1,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j-1,intBoardWidth)]["value"] < 10):
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
				if (arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] > -1 and arrGameBoard[cotrans(i,j,intBoardWidth)]["value"] < 10):
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

				# Add a multiplier for the score calculation
				intLinesInRow = intLinesInRow + 1

				# Move all tiles from our current position down
				for k in reversed(range(1,j+1)):
					print(str(k),end="")
					for l in range(intBoardWidth):
						arrGameBoard[cotrans(l,k,intBoardWidth)]["value"] = arrGameBoard[cotrans(l,k-1,intBoardWidth)]["value"]
						arrGameBoard[cotrans(l,k-1,intBoardWidth)]["value"] = -1

		intGameScore = intGameScore + (4 * intLinesInRow)
		selectTile()

	setActiveTilePositions()

# =============================================================================
# REVIEWED : Yes
#
def processRight():

	global intBoardWidth
	global intBoardHeight
	global arrGameBoard
	global intShapeOriginX
	global arrActiveTile

	# Check all active tiles and see if anything in blocking them
	blnLegalMove = True

	for i in arrActiveTile:
		intPosX = i["x"]
		intPosY = i["y"]
		intPosMoveToX = intPosX + 1
		if (intPosMoveToX < intBoardWidth):
			intTileAtDestination = arrGameBoard[cotrans(intPosMoveToX,intPosY,intBoardWidth)]["value"]
			if (intTileAtDestination > 10):
				blnLegalMove = False
				break
		else:
			blnLegalMove = False
			break

	if (blnLegalMove == True):
		for i in reversed(arrActiveTile):
			intGamePos = cotrans(i["x"],i["y"],intBoardWidth)
			intGamePosTo = cotrans(i["x"]+1,i["y"],intBoardWidth)
			arrGameBoard[intGamePosTo]["value"] = arrGameBoard[intGamePos]["value"]
			arrGameBoard[intGamePos]["value"] = -1
		intShapeOriginX = intShapeOriginX + 1

	setActiveTilePositions()

# =============================================================================
# REVIEWED : Yes
#
def processLeft():

	global intBoardWidth
	global intBoardHeight
	global arrGameBoard
	global intShapeOriginX
	global arrActiveTile

	# Check all active tiles and see if anything in blocking them
	blnLegalMove = True

	for i in arrActiveTile:
		intPosX = i["x"]
		intPosY = i["y"]
		intPosMoveToX = intPosX - 1
		if (intPosMoveToX > -1):
			intTileAtDestination = arrGameBoard[cotrans(intPosMoveToX,intPosY,intBoardWidth)]["value"]
			if (intTileAtDestination > 10):
				blnLegalMove = False
				break
		else:
			blnLegalMove = False
			break

	if (blnLegalMove == True):
		for i in arrActiveTile:
			intGamePos = cotrans(i["x"],i["y"],intBoardWidth)
			intGamePosTo = cotrans(i["x"]-1,i["y"],intBoardWidth)
			arrGameBoard[intGamePosTo]["value"] = arrGameBoard[intGamePos]["value"]
			arrGameBoard[intGamePos]["value"] = -1
		intShapeOriginX = intShapeOriginX - 1

	setActiveTilePositions()

def processLateral(intMoveType):

	global intBoardWidth
	global intBoardHeight
	global arrGameBoard
	global intShapeOriginX
	global arrActiveTile

	intCheckBoundsLower = -1
	intCheckBoundsUpper = intBoardWidth

	intOffsetUpdate = 0

	if (intMoveType == 1):
		intOffsetUpdate = -1
	elif (intMoveType == 2):
		intOffsetUpdate = 1

	# Check all active tiles and see if anything in blocking them
	blnLegalMove = True

	for i in arrActiveTile:
		intPosX = i["x"]
		intPosY = i["y"]
		intPosMoveToX = intPosX + intOffsetUpdate
		if (intPosMoveToX > intCheckBoundsLower and intPosMoveToX < intCheckBoundsLower):
			intTileAtDestination = arrGameBoard[cotrans(intPosMoveToX,intPosY,intBoardWidth)]["value"]
			if (intTileAtDestination > 10):
				blnLegalMove = False
				break
		else:
			blnLegalMove = False
			break

	if (blnLegalMove == True):
		for i in arrActiveTile:
			intGamePos = cotrans(i["x"],i["y"],intBoardWidth)
			intGamePosTo = cotrans(i["x"]-1,i["y"],intBoardWidth)
			arrGameBoard[intGamePosTo]["value"] = arrGameBoard[intGamePos]["value"]
			arrGameBoard[intGamePos]["value"] = -1
		intShapeOriginX = intShapeOriginX + intOffsetUpdate

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

	print("About to rotate")

	blnCanRotate = True
	objShape = arrShapes[intSelectedTile]
	angle = (math.pi * 90) / 180
	arrNewPositions = []

	if (objShape["rotates"] == True):
		print("This tile can rotate")
		for k in range(len(arrActiveTile)):
			print("Rotating tile at x: " + str(arrActiveTile[k]["x"]) + " y: " + str(arrActiveTile[k]["y"]))
			center_x = intShapeOriginX + objShape["center_x"]
			center_y = intShapeOriginY + objShape["center_y"]

			print("Rotating around center x: " +  str(center_x) + " y: " + str(center_y))
			rotated_pos_x = int(round((math.cos(angle) * (arrActiveTile[k]["x"] - center_x)) - (math.sin(angle) * (arrActiveTile[k]["y"] - center_y)) + center_x))
			rotated_pos_y = int(round((math.sin(angle) * (arrActiveTile[k]["x"] - center_x)) + (math.cos(angle) * (arrActiveTile[k]["y"] - center_y)) + center_y))

			print("Should be placed at x: " +  str(rotated_pos_x) + " y: " + str(rotated_pos_y))
			if (rotated_pos_x < 0 or rotated_pos_x > (intBoardWidth - 1)):
				print("this point out of bounds")
				blnCanRotate = False
				break

			if (arrGameBoard[cotrans(rotated_pos_x,rotated_pos_y,intBoardWidth)]["value"] == -1 or arrGameBoard[cotrans(rotated_pos_x,rotated_pos_y,intBoardWidth)]["value"] == intSelectedTile):
				arrNewPositions.append({"x":rotated_pos_x,"y":rotated_pos_y});
			else:
				print("this point collides")
				blnCanRotate = False
				break

		if (blnCanRotate == True):
			print("We should be able to rotate all points")
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
	
	objMyGame.drawRect(0, 0, 300, 460, (50,50,50))
	match intGameState:
		case 0: # READY TO PLAY - PRESS KEY OR TOUCH /////////////////////////

			# Draw the main SimpleBlocks play area
			drawSimpleBlocksPlayArea();

			# Logic to show/hide the start game message
			if ((blnShowMessage and tmrPressSpace.checkTimePassed(800)) or (not blnShowMessage and tmrPressSpace.checkTimePassed(300))):
				blnShowMessage = not blnShowMessage
				tmrPressSpace.resetTimer()

			if (blnShowMessage == True):
				objMyGame.drawImage("imgStartGameLogo", 10, 170, 200, 40)

			if (objMyGame.checkKeyStatus('SPACE')):
				resetGame()
				selectTile()
				intGameState = 1



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
				if (tmrPressSpace.checkTimePassed(100)):
					tmrPressSpace.resetTimer()
					processLeft()

			if (objMyGame.checkKeyStatus("RIGHT")):
				if (tmrPressSpace.checkTimePassed(100)):
					tmrPressSpace.resetTimer()
					processRight();

			if (objMyGame.checkKeyStatus("UP")):
				if (tmrPressSpace.checkTimePassed(100)):
					tmrPressSpace.resetTimer()
					rotateTile()

			'''
			#if (objMyGameEngine.checkKeyStatus("KeyE") && objMyGameEngine.checkKeyStateChanged("KeyE"))
			#rotateShape();
			'''

			# Draw the playing area
			drawSimpleBlocksPlayArea()

	blnRunning = objMyGame.processEvents()
	
	objMyGame.displayUpdate()
	
#for lstElement in arrGameBoard:
#	print(lstElement["x"] + ", " + lstElement["y"])
