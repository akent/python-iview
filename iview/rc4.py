#!/usr/bin/env python
__license__ = 'LGPL'

# Portions of this library is Copyright (C) by the user 'Siph0n', which I found at:
#   <http://www.macshadows.com/forums/index.php?showtopic=5766> (retrieved 18 November 2009)
# Licenced under the GNU LGPL. (No version specified.)

class RC4:
	def __init__(self, key = ""):
		if key:
			self._rc4_init(key)
		   
	def _rc4_init(self, key):
		(self.x,self.y) = (0,0)
		self.state_array = [i for i in xrange(0,256)]
		for i in xrange(0,256):
			self.x = ((ord(key[i%len(key)]) & 0xff) + self.state_array[i] + self.x) & 0xff
			self.state_array[i], self.state_array[self.x] = self.state_array[self.x], self.state_array[i]
		self.x = 0

	def engine_crypt(self, input):
		self.out = []
		for i in xrange(0,len(input)):
			self.x = (self.x + 1) & 0xff
			self.y = (self.state_array[self.x] + self.y) & 0xff
			self.state_array[self.x], self.state_array[self.y] = self.state_array[self.y], self.state_array[self.x]
			self.out.append(chr((ord(input[i]) ^ self.state_array[(self.state_array[self.x] + self.state_array[self.y]) & 0xff])))
		return "".join(self.out)

	def hex_to_str(self, input):
		codes = ''

		i = 0
		if input[0] == '0' and input[1] == 'x': # starts with '0x'
			i = 2

		while i < len(input):
			codes = ''.join((codes, chr(int(input[i] + input[i+1], 16)))) # 16 = base 16, i.e. hex
			i += 2

		return codes
