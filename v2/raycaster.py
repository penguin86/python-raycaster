#!/usr/bin/env python3

# RAYCASTER
# Inspired by https://www.youtube.com/watch?v=gYRrGTC7GtA
#
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
MAP_SIZE = 17
MAP_WIN_WIDTH = MAP_SIZE * MAP_SCALE
MAP_WIN_HEIGHT = MAP_SIZE * MAP_SCALE

# Textures cfg
TEXTURES = [
	"assets/texture_wall.png",
	"assets/texture_wall.png",
	"assets/texture_wall.png"
]
TEXTURE_SIZE = 64

# Raycast cfg
RAYCAST_WIN_WIDTH = 1000
RAYCAST_WIN_HEIGHT = 600
RAYCAST_RESOLUTION_SCALING = 4
RAYCAST_RENDER_WIDTH = int(RAYCAST_WIN_WIDTH / RAYCAST_RESOLUTION_SCALING)
RAYCAST_RENDER_HEIGHT = int(RAYCAST_WIN_HEIGHT / RAYCAST_RESOLUTION_SCALING)
DOF = 2*MAP_SIZE	# Depth Of Field
CEILING_COLOR = sdl2.ext.Color(0,128,255,255)
FLOOR_COLOR = sdl2.ext.Color(0,128,0,255)

# Player cfg
PLAYER_SPEED = 8
PLAYER_ROTATION_SPEED = 0.1
PLAYER_SPAWN_POSITION = {"x": int(MAP_SCALE * 2), "y": int(MAP_SCALE * 5), "r": 0}	# r is rotation in radiants

# Dungeon data
MAP = [
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1,
	2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 3, 3, 3, 3, 3, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1,
	2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
]

class Main:

	def __init__(self):
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

		self.raycastWindow = sdl2.ext.Window("3D View", size=(RAYCAST_WIN_WIDTH, RAYCAST_WIN_HEIGHT))
		self.raycastWindow.show()
		self.raycastSurface = self.raycastWindow.get_surface()
		self.raycast_u32_pixels = ctypes.cast(self.raycastSurface.pixels, ctypes.POINTER(ctypes.c_uint32))	# Raw SDL surface pixel array

		# Player
		self.player_position = PLAYER_SPAWN_POSITION

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
			player_delta_x = math.cos(self.player_position["r"]) * PLAYER_SPEED
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

			self.draw()
			if not MAP_HIDDEN:
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
		sdl2.ext.draw.fill(self.raycastSurface, CEILING_COLOR, (0, 0, RAYCAST_WIN_WIDTH, RAYCAST_WIN_HEIGHT/2)) # Clears upper raycast screen (draws ceiling)
		sdl2.ext.draw.fill(self.raycastSurface, FLOOR_COLOR, (0, RAYCAST_WIN_HEIGHT/2, RAYCAST_WIN_WIDTH, RAYCAST_WIN_HEIGHT/2)) # Clears upper raycast screen (draws floor)

		# Casts rays for raycasting
		playerAngle = self.player_position["r"]

		# Cast one ray for every window pixel, from -0,5 rads to +0,5 rads (about 60° viewing angle)
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

				# Upscaling
				lineStart = lineStart * RAYCAST_RESOLUTION_SCALING
				lineEnd = lineEnd * RAYCAST_RESOLUTION_SCALING

				# Draw segment
				for repeat in range(1, RAYCAST_RESOLUTION_SCALING + 1):
					x = i * RAYCAST_RESOLUTION_SCALING + repeat
					self.drawVline(self.raycastSurface, color, x, int(lineStart), int(lineEnd))

	def drawVline(self, surface, color, x, startY, endY):
		if x < 0 or x > RAYCAST_WIN_WIDTH or startY < 0 or endY > RAYCAST_WIN_HEIGHT or endY < startY:
			print("Trying to write outside bounds: vertical line with x {} from y {} to y {}".format(x, startY, endY))
			return

		startIdx = startY * RAYCAST_WIN_WIDTH + x
		for idx in range(startIdx, endY * RAYCAST_WIN_WIDTH + x, RAYCAST_WIN_WIDTH):
			self.raycast_u32_pixels[idx] = color

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
		if metadata['alpha']:
			raise ValueError("Textures with alpha channel are not supported")
		if w != TEXTURE_SIZE or h != TEXTURE_SIZE:
			raise ValueError("Texture {} is not {}x{}, but {}x{}".format(pngFilePath, TEXTURE_SIZE, TEXTURE_SIZE, w, h))
		# Convert to sdl2-friendly format
		converted = []
		for i in range(0, len(pixels), 3):
			# PNG is RGB, SDL surface is BGR
			converted.append(pixels[i+2] + (pixels[i+1] << 8) + (pixels[i] << 16)) # BGR
		return converted



if __name__ == '__main__':
	try:
		main = Main()
		main.run()
	except KeyboardInterrupt:
		exit(0)
