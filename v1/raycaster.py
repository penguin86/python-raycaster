#!/usr/bin/env python3

# RAYCASTER
# Inspired by https://www.youtube.com/watch?v=gYRrGTC7GtA
#
# pip install pysdl2 pysdl2-dll

import sys
import sdl2.ext
import math
import time

MAP_WIN_WIDTH = 640
MAP_WIN_HEIGHT = 640
RAYCAST_WIN_WIDTH = 800
RAYCAST_WIN_HEIGHT = 480
DUNGEON_WIDTH = MAP_WIN_WIDTH
DUNGEON_HEIGHT = MAP_WIN_HEIGHT
PLAYER_SPEED = 10
PLAYER_ROTATION_SPEED = 0.17
RAY_LENGTH = 100
MAP_SCALE = 40

MAP = [
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
]
MAP_SIZE = 16
DOF = 2*MAP_SIZE	# Depth Of Field

class Main:

	def __init__(self):
		# Check valid map
		if len(MAP) != MAP_SIZE * MAP_SIZE:
			raise ValueError("Map size is {}, but should be a power of {}".format(len(MAP), MAP_SIZE))

		# Graphics
		sdl2.ext.init()
		self.mapWindow = sdl2.ext.Window("2D Map", size=(MAP_WIN_WIDTH, MAP_WIN_HEIGHT))
		self.mapWindow.show()
		self.mapSurface = self.mapWindow.get_surface()

		self.raycastWindow = sdl2.ext.Window("3D View", size=(RAYCAST_WIN_WIDTH, RAYCAST_WIN_HEIGHT))
		self.raycastWindow.show()
		self.raycastSurface = self.raycastWindow.get_surface()

		# Player
		self.player_position = {"x": int(DUNGEON_WIDTH/2), "y": int(DUNGEON_HEIGHT/2), "r": 0}	# r is rotation in radiants

		return

	def run(self):
		lastFpsCalcTime = 0
		frames = 0

		running = True
		while running:
			events = sdl2.ext.get_events()
			for event in events:
				if event.type == sdl2.SDL_QUIT:
					running = False
					break
				if event.type == sdl2.SDL_KEYDOWN:
					# Rotate player
					if event.key.keysym.sym == sdl2.SDLK_LEFT:
						self.player_position["r"] = self.player_position["r"] - PLAYER_ROTATION_SPEED
					elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
						self.player_position["r"] = self.player_position["r"] + PLAYER_ROTATION_SPEED

					# Compute deltax and deltay based on player direction
					player_delta_x = math.cos(self.player_position["r"]) * PLAYER_SPEED
					player_delta_y = math.sin(self.player_position["r"]) * PLAYER_SPEED

					# Move player based on its direction
					if event.key.keysym.sym == sdl2.SDLK_UP:
						self.player_position["y"] = int(self.player_position["y"] + player_delta_y)
						self.player_position["x"] = int(self.player_position["x"] + player_delta_x)
					elif event.key.keysym.sym == sdl2.SDLK_DOWN:
						self.player_position["y"] = int(self.player_position["y"] - player_delta_y)
						self.player_position["x"] = int(self.player_position["x"] - player_delta_x)

					# Limit position into dungeon bounds
					if self.player_position["x"] < 0:
						self.player_position["x"] = 0
					if self.player_position["x"] > DUNGEON_WIDTH:
						self.player_position["x"] = DUNGEON_WIDTH
					if self.player_position["y"] < 0:
						self.player_position["y"] = 0
					if self.player_position["y"] > DUNGEON_HEIGHT:
						self.player_position["y"] = DUNGEON_HEIGHT
					if self.player_position["r"] > 2*math.pi:
						self.player_position["r"] = 0
					if self.player_position["r"] < 0:
						self.player_position["r"] = 2*math.pi

			self.draw()
			self.mapWindow.refresh()
			self.raycastWindow.refresh()

			# Calculate FPS
			frames = frames + 1
			if time.time() - lastFpsCalcTime > 1:
				fps = frames/(time.time() - lastFpsCalcTime)
				print(int(fps))
				frames = 0
				lastFpsCalcTime = time.time()

		return 0

	def draw(self):
		sdl2.ext.draw.fill(self.mapSurface, sdl2.ext.Color(0,0,0,255)) # Clears map screen
		sdl2.ext.draw.fill(self.raycastSurface, sdl2.ext.Color(0,0,128,255), (0, 0, RAYCAST_WIN_WIDTH, RAYCAST_WIN_HEIGHT/2)) # Clears upper raycast screen (draws ceiling)
		sdl2.ext.draw.fill(self.raycastSurface, sdl2.ext.Color(0,128,0,255), (0, RAYCAST_WIN_HEIGHT/2, RAYCAST_WIN_WIDTH, RAYCAST_WIN_HEIGHT/2)) # Clears upper raycast screen (draws floor)

		self.draw2Dmap()
		self.drawPlayer()
		self.drawRays()

	def drawPlayer(self):
		# Player in 2D map
		sdl2.ext.draw.fill(self.mapSurface, sdl2.ext.Color(0,255,0,255), (self.player_position["x"] - 2, self.player_position["y"] - 2, 4, 4))
		# Player line of sight in 2D map
		ray = {
			"x": int(self.player_position["x"] + math.cos(self.player_position["r"]) * 50), # deltaX + playerX
			"y": int(self.player_position["y"] + math.sin(self.player_position["r"]) * 50)  # deltaY + playerY
		}
		sdl2.ext.draw.line(self.mapSurface, sdl2.ext.Color(255,0,0,255), (self.player_position["x"], self.player_position["y"], ray["x"], ray["y"]))


	def draw2Dmap(self):
		# 2D map
		for i in range(len(MAP)):
			posX = i % MAP_SIZE * MAP_SCALE
			posY = math.floor(i / MAP_SIZE) * MAP_SCALE
			color = 0
			if MAP[i] == 1:
				color = 255
			sdl2.ext.draw.fill(self.mapSurface, sdl2.ext.Color(color,color,color,255), (posX, posY, MAP_SCALE - 1, MAP_SCALE - 1))

	def drawRays(self):
		# Casts rays for raycasting
		playerAngle = self.player_position["r"]

		# Cast one ray for every window pixel, from -0,5 rads to +0,5 rads (about 60° viewing angle)
		for i in range(RAYCAST_WIN_WIDTH):
			rayAngle = playerAngle + (i/RAYCAST_WIN_WIDTH) - 0.5
			if rayAngle < 0:
				rayAngle = math.pi * 2 + rayAngle
			if rayAngle > math.pi * 2:
				rayAngle = rayAngle - math.pi * 2

			# Check horizontal lines
			dof = 0 # Depth of field
			if rayAngle == 0 or rayAngle == math.pi:
				# Looking left or right (ray will never intersect parallel lines)
				rayY = self.player_position["y"]
				rayX = self.player_position["x"] + DOF * MAP_SCALE
				dof = DOF	# Set depth of field to maximum to avoid unneeded checks
			elif rayAngle > math.pi:
				# Looking up
				aTan = -1/math.tan(rayAngle)
				rayY = (int(self.player_position["y"] / MAP_SCALE) * MAP_SCALE) - 0.00001
				rayX = (self.player_position["y"] - rayY) * aTan + self.player_position["x"]
				yOffset = -MAP_SCALE
				xOffset = -yOffset * aTan
			else:
				# Looking down
				aTan = -1/math.tan(rayAngle)
				rayY = (int(self.player_position["y"] / MAP_SCALE) * MAP_SCALE) + MAP_SCALE
				rayX = (self.player_position["y"] - rayY) * aTan + self.player_position["x"]
				yOffset = MAP_SCALE
				xOffset = -yOffset * aTan

			# Check if we reached a wall
			while dof < DOF:
				mapX = int(rayX / MAP_SCALE)
				mapY = int(rayY / MAP_SCALE)
				mapArrayPosition = mapY * MAP_SIZE + mapX
				if mapArrayPosition >= 0 and mapArrayPosition < MAP_SIZE*MAP_SIZE and MAP[mapArrayPosition] != 0:
					dof = DOF	# Hit the wall: we are done, no need to do other checks
				else:
					# Didn't hit the wall: check successive horizontal line
					rayX = rayX + xOffset
					rayY = rayY + yOffset
					dof = dof + 1

			# Save horyzontal probe rays for later comparison with vertical
			horizRayX = rayX
			horizRayY = rayY

			# Check vertical lines
			dof = 0 # Depth of field
			nTan = -math.tan(rayAngle)
			xOffset = 0
			yOffset = 0
			if rayAngle == math.pi * 0.5 or rayAngle == math.pi * 1.5:
			#if rayAngle == 0 or rayAngle == math.pi:
				# Looking up or down (ray will never intersect vertical lines)
				rayX = self.player_position["x"]
				rayY = self.player_position["y"] + DOF * MAP_SCALE
				dof = DOF	# Set depth of field to maximum to avoid unneeded checks
			elif rayAngle > math.pi * 0.5 and rayAngle < math.pi * 1.5:
				# Looking left
				rayX = (int(self.player_position["x"] / MAP_SCALE) * MAP_SCALE) - 0.00001
				rayY = (self.player_position["x"] - rayX) * nTan + self.player_position["y"]
				xOffset = -MAP_SCALE
				yOffset = -xOffset * nTan
			else:
				# Looking right
				rayX = (int(self.player_position["x"] / MAP_SCALE) * MAP_SCALE) + MAP_SCALE
				rayY = (self.player_position["x"] - rayX) * nTan + self.player_position["y"]
				xOffset = MAP_SCALE
				yOffset = -xOffset * nTan

			# Check if we reached a wall
			while dof < DOF:
				mapX = int(rayX / MAP_SCALE)
				mapY = int(rayY / MAP_SCALE)
				mapArrayPosition = mapY * MAP_SIZE + mapX
				if mapArrayPosition >= 0 and mapArrayPosition < MAP_SIZE*MAP_SIZE-1 and MAP[mapArrayPosition] != 0:
					dof = DOF	# Hit the wall: we are done, no need to do other checks
				else:
					# Didn't hit the wall: check successive horizontal line
					rayX = rayX + xOffset
					rayY = rayY + yOffset
					dof = dof + 1

			horizDist = self.dist(self.player_position["x"], self.player_position["y"], horizRayX, horizRayY)
			vertDist = self.dist(self.player_position["x"], self.player_position["y"], rayX, rayY)
			shortestDist = vertDist
			if vertDist > horizDist:
				rayX = horizRayX
				rayY = horizRayY
				shortestDist = horizDist

			# Draw rays in 2D view
			sdl2.ext.draw.line(self.mapSurface, sdl2.ext.Color(0,0,255,255), (self.player_position["x"], self.player_position["y"], rayX, rayY))


			# ------ Draw 3D view ------

			# Calculate line height based on distance
			lineHeight = MAP_SCALE * RAYCAST_WIN_HEIGHT / shortestDist
			if lineHeight > RAYCAST_WIN_HEIGHT:
				lineHeight = RAYCAST_WIN_HEIGHT
			# Center line vertically in window
			lineOffset = RAYCAST_WIN_HEIGHT / 2 - lineHeight / 2

			# Simulate lighting based on wall incidence
			color = sdl2.ext.Color(255,255,255,255)
			if vertDist > horizDist:
				color = sdl2.ext.Color(200,200,200,255)

			# Draw line
			sdl2.ext.draw.line(self.raycastSurface, color, (i, int(lineOffset), i, int(lineOffset + lineHeight)))

	def dist(self, ax, ay, bx, by):
		return math.sqrt((bx-ax)*(bx-ax) + (by-ay)*(by-ay))



if __name__ == '__main__':
	try:
		main = Main()
		main.run()
	except KeyboardInterrupt:
		exit(0)
