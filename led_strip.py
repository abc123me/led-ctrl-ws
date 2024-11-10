import atexit, rpi_ws281x, random

from rpi_ws281x import Color

def parseColor(str):
	ss = str.split(',')
	if len(ss) == 3:
		return Color(int(ss[0], 0), int(ss[1], 0), int(ss[2], 0))
	elif len(ss) == 4:
		return Color(int(ss[0], 0), int(ss[1], 0), int(ss[2], 0), int(ss[3], 0))
	else:
		raise ValueErrro('Invalid color format used')

class LedStrip:
	strip = None
	clear_color = None
	animation_info = None
	animation_id = 0
	animation_ctr = 0

	def random_colors_anim(self):
		pass


	temperatures = None
	def fire_anim(self):
		s = self.strip
		l = s.numPixels()
		self.animation_ctr += 1
		if self.temperatures:
			# Generate some sparks
			sparkCnt = random.randrange(3)
			for i in range(sparkCnt):
				self.temperatures[random.randrange(l)] = random.randrange(100) + 155
			# Simulate the fire
			for i in range(l):
				temp = self.temperatures[i]
				if temp > 0:
					# Simulate cooling
					temp -= 10 if temp > 100 else (5 if temp > 50 else 1)
					# Update the array
					self.temperatures[i] = temp
				# Update LED with color
				if temp > 170:
					temp = (temp - 170) * 3
					if temp > 255: temp = 255
					s[i] = Color(255, 255, temp)
				elif temp > 85:
					temp = (temp - 85) * 3
					if temp > 255: temp = 255
					s[i] = Color(255, temp, 0)
				else:
					temp = temp * 3
					if temp > 255: temp = 255
					s[i] = Color(temp, 0, 0)
			s.show()
		else:
			self.temperatures = [0] * l
			self.animation_ctr = 0
			return 0
		return 0.1

	# Color wipe animation
	def color_wipe_anim(self):
		if self.animation_ctr > 7:
			self.animation_ctr = 1
		self.clear(Color(255 if (self.animation_ctr & 1) > 0 else 0,
		                 255 if (self.animation_ctr & 2) > 0 else 0,
		                 255 if (self.animation_ctr & 4) > 0 else 0))
		self.animation_ctr += 1
		return 0.5

	# Static (single color) animation
	def static_anim(self):
		color = Color(255, 0, 0)
		if self.animation_info["color"]:
			color = parseColor(self.animation_info["color"])
		else:
			print("Warning: color not set")
		self.clear(color)
		return 1

	# Rainbow animation
	def rainbow_anim(self):
		s = self.strip()
		if self.animation_ctr > 255:
			self.animation_ctr = 0
		for i in range(s.numPixels()):
			s[i] = wheel((i + self.animation_ctr) & 255)
		s.show()
		self.animation_ctr += 1
		return 0.02

	def __init__(self, str, clr_color, auto_clear=True):
		self.progress_animation = self.static_anim
		self.strip = str
		self.clear_color = clr_color
		self.strip.begin()
		if auto_clear:
			self.clear()
		atexit.unregister(self.strip._cleanup)

	def clear(self, color=None):
		for num in range(self.strip.numPixels()):
			self.strip[num] = color if color else self.clear_color
		self.strip.show()

	def cleanup(self):
		self.strip._cleanup()

	def set_brightness(self, b):
		self.strip.setBrightness(b)

	def set_animation(self, id, info):
		self.animation_id = id
		self.animation_info = info
		self.animation_ctr = 0
		if self.animation_id == 1:   # Rainbow
			self.progress_animation = self.rainbow_anim
		elif self.animation_id == 2: # Color wipe
			self.progress_animation = self.color_wipe_anim
		elif self.animation_id == 3: # Random colors
			self.progress_animation = self.random_colors_anim
		elif self.animation_id == 4: # Fire
			self.progress_animation = self.fire_anim
		else:                        # Static (singular color)
			self.progress_animation = self.static_anim


def lookup_strip_type(strip_str):
	strip_str = str(strip_str).lower().strip()
	if strip_str == 'rgb':    return rpi_ws281x.WS2811_STRIP_RGB
	elif strip_str == 'rbg':  return rpi_ws281x.WS2811_STRIP_RBG
	elif strip_str == 'grb':  return rpi_ws281x.WS2811_STRIP_GRB
	elif strip_str == 'gbr':  return rpi_ws281x.WS2811_STRIP_GBR
	elif strip_str == 'bgr':  return rpi_ws281x.WS2811_STRIP_BGR
	elif strip_str == 'brg':  return rpi_ws281x.WS2811_STRIP_BRG
	elif strip_str == 'rgbw': return rpi_ws281x.SK6812_STRIP_RGBW
	elif strip_str == 'rbgw': return rpi_ws281x.SK6812_STRIP_RBGW
	elif strip_str == 'grbw': return rpi_ws281x.SK6812_STRIP_GRBW
	elif strip_str == 'gbrw': return rpi_ws281x.SK6812_STRIP_GBRW
	elif strip_str == 'bgrw': return rpi_ws281x.SK6812_STRIP_BGRW
	elif strip_str == 'brgw': return rpi_ws281x.SK6812_STRIP_BRGW
	return None

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)
