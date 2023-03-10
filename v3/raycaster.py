#!/usr/bin/env python3

# PYTHON RAYCASTER
# Inspired by https://www.youtube.com/watch?v=gYRrGTC7GtA
# Copyright (C) 2023 Daniele Verducci

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# REQUIREMENTS:
# pip install pysdl2 pysdl2-dll pypng

import sys
import sdl2.ext
import math
import time
import ctypes
import png

# Map cfg
MAP_HIDDEN = True
MAP_SCALE = 24
MAP_SIZE = 32
MAP_WIN_WIDTH = MAP_SIZE * MAP_SCALE
MAP_WIN_HEIGHT = MAP_SIZE * MAP_SCALE
MAP_DOOR_CELL_TYPE = 3

# Textures cfg
# Index is shifted by 1 relative to map, because 0 is no wall
TEXTURES = [
	"assets/texture_wall_brick.png",	# = map index 1
	"assets/texture_wall_brick_door_left.png",	# = map index 2
	"assets/texture_wall_brick_door_center.png",	# = map index 3
	"assets/texture_wall_brick_door_right.png",	# = map index 4
	"assets/texture_wall_brick_flag.png",	# = map index 5
	"assets/texture_temple.png",	# = map index 6
]
TEXTURE_SIZE = 64

# Raycast cfg
RAYCAST_WIN_WIDTH = 1000
RAYCAST_WIN_HEIGHT = 1000
RAYCAST_RENDER_MULTIPLIER = 4
RAYCAST_RENDER_WIDTH = int(RAYCAST_WIN_WIDTH / RAYCAST_RENDER_MULTIPLIER)
RAYCAST_RENDER_HEIGHT = int(RAYCAST_WIN_HEIGHT / RAYCAST_RENDER_MULTIPLIER)
DOF = 2*MAP_SIZE	# Depth Of Field
CEILING_COLOR = [0,128,255]
FLOOR_COLOR = [64,64,64]

# Player cfg
PLAYER_SPEED = 8
PLAYER_ROTATION_SPEED = 0.1
PLAYER_SPAWN_POSITION = {"x": 1.5, "y": 1.5, "r": 1.7}	# r is rotation in radiants

# Dungeon data
MAP = [
	1, 1, 1, 1, 1, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 6, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 5, 0, 0, 0, 0, 0, 0, 0, 5, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 2, 1, 1, 5, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 4, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 4, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 4, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
]

class Main:

	def __init__(self):
		# Print instructions
		print('RAYCASTER by penguin86\n\nMovement: up, down, left, right\nOpen door: space\n\nFPS:')

		# Check valid map
		if len(MAP) != MAP_SIZE * MAP_SIZE:
			raise ValueError("Map size is {}, but should be a power of {}".format(len(MAP), MAP_SIZE))

		# Load textures
		self.textures = []
		for texFile in TEXTURES:
			self.textures.append(self.loadTexture(texFile))

		# Graphics
		sdl2.ext.init()
		if not MAP_HIDDEN:
			self.mapWindow = sdl2.ext.Window("2D Map", size=(MAP_WIN_WIDTH, MAP_WIN_HEIGHT))
			self.mapWindow.show()
			self.mapSurface = self.mapWindow.get_surface()

		self.raycastWindow = sdl2.SDL_CreateWindow(b"3D View", 100, 100, RAYCAST_WIN_WIDTH, RAYCAST_WIN_HEIGHT,sdl2.SDL_WINDOW_SHOWN)
		self.raycastRenderer = sdl2.SDL_CreateRenderer(self.raycastWindow, -1,sdl2.SDL_RENDERER_ACCELERATED |sdl2.SDL_RENDERER_PRESENTVSYNC)
		self.raycastSurface = sdl2.SDL_CreateRGBSurface(0,RAYCAST_WIN_WIDTH,RAYCAST_WIN_HEIGHT,32,0,0,0,0)

		# Player
		self.player_position = {"x": int(MAP_SCALE * PLAYER_SPAWN_POSITION["x"]), "y": int(MAP_SCALE * PLAYER_SPAWN_POSITION["y"]), "r": PLAYER_SPAWN_POSITION["r"]}	# r is rotation in radiants

		return

	def run(self):
		lastFpsCalcTime = 0
		frames = 0

		running = True
		while running:
			events = sdl2.ext.get_events()
			for event in events:
				if event.type == sdl2.SDL_QUIT or (event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_ESCAPE):
					running = False
					break

			keystate = sdl2.SDL_GetKeyboardState(None)
			# Rotate player
			if keystate[sdl2.SDL_SCANCODE_LEFT]:
				self.player_position["r"] = self.player_position["r"] - PLAYER_ROTATION_SPEED
			elif keystate[sdl2.SDL_SCANCODE_RIGHT]:
				self.player_position["r"] = self.player_position["r"] + PLAYER_ROTATION_SPEED

			# Compute deltax and deltay based on player direction
			player_delta_x = (math.cos(self.player_position["r"]) * PLAYER_SPEED) + 1 # "+ 1": Adjust for rounding errors
			player_delta_y = math.sin(self.player_position["r"]) * PLAYER_SPEED

			# Move player based on its direction
			if keystate[sdl2.SDL_SCANCODE_UP]:
				self.movePlayerRelative(player_delta_x, player_delta_y)
			elif keystate[sdl2.SDL_SCANCODE_DOWN]:
				self.movePlayerRelative(-player_delta_x, -player_delta_y)

			# Limit position into dungeon bounds
			if self.player_position["x"] < 0:
				self.player_position["x"] = 0
			if self.player_position["x"] > MAP_WIN_WIDTH:
				self.player_position["x"] = MAP_WIN_WIDTH
			if self.player_position["y"] < 0:
				self.player_position["y"] = 0
			if self.player_position["y"] > MAP_WIN_HEIGHT:
				self.player_position["y"] = MAP_WIN_HEIGHT
			if self.player_position["r"] > 2*math.pi:
				self.player_position["r"] = 0
			if self.player_position["r"] < 0:
				self.player_position["r"] = 2*math.pi

			# Open doors
			if keystate[sdl2.SDL_SCANCODE_SPACE]:
				self.openDoor()

			self.draw()
			if not MAP_HIDDEN:
				self.mapWindow.refresh()
			#self.raycastWindow.refresh()

			# Calculate FPS
			frames = frames + 1
			if time.time() - lastFpsCalcTime > 1:
				fps = frames/(time.time() - lastFpsCalcTime)
				print(int(fps))
				frames = 0
				lastFpsCalcTime = time.time()

		return 0

	def movePlayerRelative(self, player_delta_x, player_delta_y):
		# Prevent player from going into walls (X axis)
		newPlayerX = int(self.player_position["x"] + player_delta_x)
		mapX = int(newPlayerX / MAP_SCALE)
		mapY = int(self.player_position["y"] / MAP_SCALE)
		mapArrayPosition = mapY * MAP_SIZE + mapX
		if mapArrayPosition >= 0 and mapArrayPosition < MAP_SIZE*MAP_SIZE-1 and MAP[mapArrayPosition] == 0:
			# Move player (X)
			self.player_position["x"] = newPlayerX

		# Prevent player from going into walls (Y axis)
		newPlayerY = int(self.player_position["y"] + player_delta_y)
		mapX = int(self.player_position["x"] / MAP_SCALE)
		mapY = int(newPlayerY / MAP_SCALE)
		mapArrayPosition = mapY * MAP_SIZE + mapX
		if mapArrayPosition >= 0 and mapArrayPosition < MAP_SIZE*MAP_SIZE-1 and MAP[mapArrayPosition] == 0:
			# Move player (Y)
			self.player_position["y"] = newPlayerY

	def draw(self):
		if not MAP_HIDDEN:
			self.draw2Dmap()
			self.drawPlayer()

		self.drawRays()
		sdl2.SDL_RenderPresent(self.raycastRenderer)

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
		sdl2.ext.draw.fill(self.mapSurface, sdl2.ext.Color(0,0,0,255)) # Clears map screen
		for i in range(len(MAP)):
			posX = i % MAP_SIZE * MAP_SCALE
			posY = math.floor(i / MAP_SIZE) * MAP_SCALE
			color = 0
			if MAP[i] > 0:
				color = 255
			sdl2.ext.draw.fill(self.mapSurface, sdl2.ext.Color(color,color,color,255), (posX, posY, MAP_SCALE - 1, MAP_SCALE - 1))

	def drawRays(self):
		# Ceiling
		sdl2.SDL_SetRenderDrawColor(self.raycastRenderer, CEILING_COLOR[0], CEILING_COLOR[1], CEILING_COLOR[2], sdl2.SDL_ALPHA_OPAQUE)
		sdl2.SDL_RenderClear(self.raycastRenderer)
		# Floor
		sdl2.SDL_SetRenderDrawColor(self.raycastRenderer, FLOOR_COLOR[0], FLOOR_COLOR[1], FLOOR_COLOR[2], sdl2.SDL_ALPHA_OPAQUE)
		sdl2.SDL_RenderFillRect(self.raycastRenderer, sdl2.SDL_Rect(0, int(RAYCAST_WIN_HEIGHT/2), RAYCAST_WIN_WIDTH, int(RAYCAST_WIN_HEIGHT)))

		# Casts rays for raycasting
		playerAngle = self.player_position["r"]

		# Cast one ray for every window pixel, from -0,5 rads to +0,5 rads (about 60?? viewing angle)
		for i in range(RAYCAST_RENDER_WIDTH):
			rayAngle = playerAngle + (i/RAYCAST_RENDER_WIDTH) - 0.5
			if rayAngle < 0:
				rayAngle = math.pi * 2 + rayAngle
			if rayAngle > math.pi * 2:
				rayAngle = rayAngle - math.pi * 2

			# Which map wall tiles have been hit by rayX and rayY
			mapBlockHitX = 0
			mapBlockHitY = 0

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
					mapBlockHitY = MAP[mapArrayPosition]	# Save which map wall tile we reached
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
					mapBlockHitX = MAP[mapArrayPosition]	# Save which map wall tile we reached
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

			if not MAP_HIDDEN:
				# Draw rays in 2D view
				sdl2.ext.draw.line(self.mapSurface, sdl2.ext.Color(0,0,255,255), (self.player_position["x"], self.player_position["y"], rayX, rayY))


			# ------ Draw 3D view ------

			# Calculate line height based on distance
			lineHeight = MAP_SCALE * RAYCAST_RENDER_HEIGHT / shortestDist
			# Center line vertically in window
			lineOffset = RAYCAST_RENDER_HEIGHT / 2 - lineHeight / 2

			# Draw pixels vertically from top to bottom to obtain a line
			textureSegmentEnd = 0
			for textureColumnPixel in range(0, TEXTURE_SIZE):
				# Calc texture segment length on screen
				textureSegmentLength = lineHeight / TEXTURE_SIZE
				if textureSegmentEnd == 0:
					# First iteration: calculate segment start
					textureSegmentStart = lineOffset + textureColumnPixel * textureSegmentLength
				else:
					# Next iterations: use the previous segment end (avoids rounding errors)
					textureSegmentStart = textureSegmentEnd
				textureSegmentEnd = textureSegmentStart + textureSegmentLength
				# Obtain texture value in the pixel representing the current segment and calculate shading
				if vertDist > horizDist:
					texIndex = mapBlockHitY - 1	# The texture covering the selected map tile (0 is no texture, 1 is texture at self.textures[0] etc)
					texColumn = int(rayX / (MAP_SCALE / TEXTURE_SIZE) % TEXTURE_SIZE)
					shading = True
				else:
					texIndex = mapBlockHitX - 1	# The texture covering the selected map tile
					texColumn = int(rayY / (MAP_SCALE / TEXTURE_SIZE) % TEXTURE_SIZE)
					shading = False

				# Obtain texture pixel color
				color = self.textures[texIndex][texColumn + textureColumnPixel * TEXTURE_SIZE]
				# Calculate color resulting from texture pixel value + shading
				if shading:
					color = self.shade(color)

				# Clipping
				lineEnd = textureSegmentEnd
				if lineEnd > RAYCAST_RENDER_HEIGHT:
					lineEnd = RAYCAST_RENDER_HEIGHT
				lineStart = textureSegmentStart
				if lineStart < 0:
					lineStart = 0
				if lineEnd < lineStart:
					continue

				# Draw segment (all is scaled x4)

				b = color & 0b000000000000000011111111
				g = color >> 8 & 0b000000000000000011111111
				r = color >> 16 & 0b000000000000000011111111
				sdl2.SDL_SetRenderDrawColor(self.raycastRenderer, r, g, b, sdl2.SDL_ALPHA_OPAQUE) # Non fare in tutti i cicli

				x = i * RAYCAST_RENDER_MULTIPLIER
				#sdl2.SDL_RenderFillRect(self.raycastRenderer, sdl2.SDL_Rect(x, int(lineStart * RAYCAST_RENDER_MULTIPLIER), RAYCAST_RENDER_MULTIPLIER, int((lineEnd - lineStart) * RAYCAST_RENDER_MULTIPLIER) + 1))
				sdl2.SDL_RenderFillRectF(self.raycastRenderer, sdl2.SDL_FRect(x, lineStart * RAYCAST_RENDER_MULTIPLIER, RAYCAST_RENDER_MULTIPLIER, (lineEnd - lineStart) * RAYCAST_RENDER_MULTIPLIER))

	def shade(self, color):
		# Obtain channels
		b = color & 0b000000000000000011111111
		g = color >> 8 & 0b000000000000000011111111
		r = color >> 16 & 0b000000000000000011111111
		# Dim channels (and limit to 255, because python doesn't have a fixed byte length)
		b = (b >> 1)
		g = (g >> 1)
		r = (r >> 1)
		# Compose color
		return b + (g << 8) + (r << 16)

	def dist(self, ax, ay, bx, by):
		return math.sqrt((bx-ax)*(bx-ax) + (by-ay)*(by-ay))

	def loadTexture(self, pngFilePath):
		# Loads a texture from png file and converts to sdl2-friendly format
		reader = png.Reader(filename=pngFilePath)
		w, h, pixels, metadata = reader.read_flat()
		if w != TEXTURE_SIZE or h != TEXTURE_SIZE:
			raise ValueError("Texture {} is not {}x{}, but {}x{}".format(pngFilePath, TEXTURE_SIZE, TEXTURE_SIZE, w, h))
		color_length = 3 # RGB
		if metadata['alpha']:
			color_length = 4 # RGBA (but alpha is ignored)
		# Convert to sdl2-friendly format
		converted = []
		for i in range(0, len(pixels), color_length):
			# PNG is RGB, SDL surface is BGR
			converted.append(pixels[i+2] + (pixels[i+1] << 8) + (pixels[i] << 16)) # BGR
		return converted

	def openDoor(self):
		# Opens a door near the user
		# Works by modifying the map (removing the door)

		# Find where is the user
		mapX = int(self.player_position["x"] / MAP_SCALE)
		mapY = int(self.player_position["y"] / MAP_SCALE)
		mapArrayPosition = mapY * MAP_SIZE + mapX

		# Find in which direction the user is looking
		playerAngle = self.player_position["r"]
		lookingAtMapArrayPosition = 0
		if playerAngle > math.pi / 4 and playerAngle <= 3 * math.pi / 4:
			# Looking up
			lookingAtMapArrayPosition = mapArrayPosition - MAP_SIZE
		elif playerAngle > 3 * math.pi / 4 and playerAngle <= 5 * math.pi / 4:
			# Looking left
			lookingAtMapArrayPosition = mapArrayPosition - 1
		elif playerAngle > 5 * math.pi / 4 and playerAngle <= 7 * math.pi / 4:
			# Looking down
			lookingAtMapArrayPosition = mapArrayPosition + MAP_SIZE
		else:
			# Looking right
			lookingAtMapArrayPosition = mapArrayPosition + 1

		if MAP[lookingAtMapArrayPosition] == MAP_DOOR_CELL_TYPE:
			# Player looking at a door: open it ("remove" it, leaving an empty space)
			MAP[lookingAtMapArrayPosition] = 0
		else:
			print("Player looking at cell #{} of type {}: nothing to do".format(lookingAtMapArrayPosition, MAP[lookingAtMapArrayPosition]))



if __name__ == '__main__':
	try:
		main = Main()
		main.run()
	except KeyboardInterrupt:
		exit(0)
