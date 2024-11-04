import atexit, rpi_ws281x

from rpi_ws281x import Color

class LedStrip:
	strip = None
	clear_color = None
	animation_info = None
	animation_id = 0
	animation_ctr = 0

	def progress_animation(self):
# 		print(self.animation_id)
		s = self.strip

		if self.animation_id == 0: # Static (singular color)
			self.clear(Color(255, 255, 255))
		elif self.animation_id == 1: # Rainbow
			if self.animation_ctr > 10000:
				self.animation_ctr = 0

			for i in range(s.numPixels()):
				s.setPixelColor(i, wheel((i + self.animation_ctr) & 255))
			s.show()

			self.animation_ctr += 1
			return 0.005
		elif self.animation_id == 2: # 3 bit color wipe
			if self.animation_ctr > 7:
				self.animation_ctr = 1

			self.clear(Color(255 if (self.animation_ctr & 1) > 0 else 0,
			                 255 if (self.animation_ctr & 2) > 0 else 0,
			                 255 if (self.animation_ctr & 4) > 0 else 0))

			self.animation_ctr += 1
			return 0.5
		elif self.animation_id == 3:
			pass
		elif self.animation_id == 4:
			pass
		elif self.animation_id == 5:
			pass
		return 1

	def __init__(self, str, clr_color, auto_clear=True):
		self.strip = str
		self.clear_color = clr_color
		self.strip.begin()
		if auto_clear:
			self.clear()
		atexit.unregister(self.strip._cleanup)
	def clear(self, color=None):
		for num in range(self.strip.numPixels()):
			self.strip.setPixelColor(num, color if color else self.clear_color)
		self.strip.show()
	def cleanup(self):
		self.strip._cleanup()
	def set_brightness(self, b):
		self.strip.setBrightness(b)
	def set_animation(self, id, info):
		self.animation_id = id
		self.animation_info = info
		self.animation_ctr = 0

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
