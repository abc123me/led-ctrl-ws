#!/usr/bin/env /home/leds/led-ctrl-ws/leds-venv/bin/python3

import atexit, time, rpi_ws281x
from led_strip import LedStrip, lookup_strip_type
from mysql import connector as mysql
from rpi_ws281x import PixelStrip, Color
from threading import Thread, Lock

leds_db = None
leds_cursor = None
leds_db_lock = Lock()
led_strips = {}
anim_threads = {}
shutdown = False
tableChecksum = None

def anim_strip(led_id, anim_id):
	global shutdown, tableChecksum, leds_db_lock
	print("LED Strip %d animation thread - staring animation %d" % (led_id, anim_id))
	strip = led_strips[led_id]
	num = 0
	blink = False
	cksum = -69420
	while not shutdown:
		if tableChecksum != cksum:
			cksum = tableChecksum
			leds_db_lock.acquire()
			leds_cursor.execute("SELECT Brightness, AnimationID FROM LedStrips WHERE ID = %d" % (led_id))
			res = leds_cursor.fetchone()
			strip.set_brightness(res[0])
			strip.set_animation(res[1], None)
			leds_db_lock.release()
			print("Animation table updated!")
		time.sleep(strip.progress_animation())
	print("Animation thread stopped!")

def main():
	print("Hello world, connecting to MySQL server now!")
	global leds_db, leds_cursor
	leds_db = mysql.connect(host="localhost", user="leds", password="password", database="LED_DB")
	leds_cursor = leds_db.cursor()
	print("MySQL Connected: " + str(leds_db))
	global tableChecksum
	leds_cursor.execute("CHECKSUM TABLE LedStrips")
	tableChecksum = str(leds_cursor.fetchone()[1])
	#                           0   1      2    3       4    5       6        7
	leds_cursor.execute("SELECT ID, Count, Pin, FreqHz, DMA, Invert, Channel, Ordering, "
	#        8           9            10           11           12
		"Brightness, ClearColorR, ClearColorG, ClearColorB, AnimationID FROM LedStrips")
	global led_strips, anim_threads
	for x in leds_cursor:
		print("Initializing LED Strip: " + str(x))
		stype = rpi_ws281x.WS2811_STRIP_RGB
		led_strips[x[0]] = LedStrip(PixelStrip(num=x[1], pin=x[2], freq_hz=x[3], dma=x[4], invert=x[5], channel=x[6], strip_type=lookup_strip_type(x[7]), brightness=x[8]), Color(x[9], x[10], x[11]))
		anim_threads[x[0]] = Thread(target=anim_strip, args=(x[0], x[12]))
		print("Initialized!")
	# Start animation threads
	global shutdown
	for id in range(len(led_strips)):
		anim_threads[id].start()
	print("Animation thread(s) started!")
	global leds_db_lock
	try:
		while True:
			leds_db_lock.acquire()
			leds_cursor.execute("CHECKSUM TABLE LedStrips")
			tableChecksum = str(leds_cursor.fetchone()[1])
			leds_db.commit()
			leds_db_lock.release()
			time.sleep(1)
	except KeyboardInterrupt:
		print("Program interrupted, shutting down gracefully!")
	# Handle exit
	shutdown = True

def on_exit():
	print("Shutting down!")
	# Stop animation thread, clear LED strips
	global shutdown, anim_threads, led_strips
	shutdown = True
	for id in range(len(led_strips)):
		anim_threads[id].join()
		led_strips[id].clear()
		led_strips[id].cleanup()
	print("LED strips cleared!")
	# Close MySQL cursor
	global leds_cursor
	if leds_cursor:
		leds_cursor.close()
		leds_cursor = None
		print("MySQL cursor closed!")
	# Close MySQL connection
	global leds_db
	if leds_db:
		leds_db.close()
		leds_db = None
		print("MySQL connection closed!")
	print("Goodbye world!")

if __name__ == "__main__":
	atexit.register(on_exit)
	main()


