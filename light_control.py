from lifxlan import LifxLAN
from lifxlan.light import Light as LifxLightType
from lifxlan.errors import WorkflowException
import flux_led
import colorsys
from json import load
from time import sleep
from threading import Timer

class Light:
	def __init__(self, controller):
		self.controller = controller
		self.lifx = type(controller) == LifxLightType
		self.led = type(controller) == flux_led.WifiLedBulb
		self.stored_colour = None

	def turn_on(self, duration=600):
		if self.lifx:
			try:
				self.controller.set_power(1, duration=duration)
			except WorkflowException:
				pass
		if self.led:
			self.controller.turnOn()

		if self.stored_colour is not None:
			timer = Timer(1, self.set_stored_colour)
			timer.start()

	def turn_off(self, duration=900):
		if self.lifx:
			try:
				self.controller.set_power(0, duration=duration)
			except WorkflowException:
				pass
		if self.led:
			self.controller.turnOff()

	def set_stored_colour(self):
		self.set_colour(self.stored_colour)
		self.stored_colour = None

	def is_on(self):
		if self.lifx:
			return self.controller.get_power() == 65535
		if self.led:
			return self.controller.is_on

	def set_colour(self, colour, duration=500):
		if not self.is_on() or colour != self.stored_colour:
			self.stored_colour = colour
		elif self.lifx:
			colour = lifx_convert_colour(colour)
			self.controller.set_color(colour, duration=duration)
		elif self.led:
			colour = led_convert_colour(colour)
			self.controller.setRgb(*colour)

	def get_colour(self):
		if self.lifx:
			return self.controller.get_color()
		if self.led:
			return self.controller.getRgb()

def get_palette():
	with open('config.json') as f:
		return load(f)['palette']


def get_lifx():
	lan = LifxLAN(1)
	lights = lan.get_lights()
	return lights[0]


def get_led():
	#scanner = flux_led.BulbScanner()
	#lights = scanner.scan(timeout=1)
	light = flux_led.WifiLedBulb('192.168.1.11')
	return light


main_light = Light(get_lifx())
led_light = Light(get_led())


def set(command):
	command = command.split('/')
	if command[0] == 'mode':
		mode = command[1]
		if len(command) > 2:
			state = command[2]
		else:
			state = "on"
		if mode == "off":
			main_light.turn_off()
			led_light.turn_off()
		else:
			main_light.set_colour(get_palette()[mode]['main'])
			led_light.set_colour(get_palette()[mode]['led'])

			if state == "on":
				main_light.turn_on()
				led_light.turn_on()



def lifx_convert_colour(colour):
	out = colorsys.rgb_to_hsv(colour[0], colour[1], colour[2])  # + ('2500')
	return (out[0] * 65535, out[1] * 65535, out[2] * 65535, 2500)


def led_convert_colour(colour):
	return (colour[0] * 255, colour[1] * 255, colour[2] * 255)


def get_colours():
	mc = main_light.get_colour()
	mc = colorsys.hsv_to_rgb(mc[0] / 65535, mc[1] / 65535, mc[2] / 65535)
	mc = [round(c, 2) for c in mc]

	lc = led_light.get_colour()
	lc = [round(c/255, 2) for c in lc]

	print(""""main": {},\n"led": {}""".format(mc, lc))

def test_mode(mode, state):
	led_light.turn_off()
	main_light.turn_off()
	sleep(3)
	set(mode + '/' + state)
	sleep(1)
	led_light.turn_on()
	main_light.turn_on()
	sleep(3)

if __name__ == "__main__":
	if True:
		test_mode('mode/day', 'auto')
		test_mode('mode/evening', 'auto')
		test_mode('mode/night', 'auto')
		test_mode('mode/dark', 'auto')
	if False:
		while True:
			main_light.turn_off()
			led_light.turn_off()
			sleep(2)
			main_light.turn_on()
			led_light.turn_on()
			sleep(2)
	#get_colours()