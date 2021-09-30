from flask import Flask
from flask import request
import base64
import json

"""
exp ::= term  | exp + term | exp - term
term ::= factor | factor * term | factor / term
factor ::= number | ( exp )
"""

def tokenize(r_input):
	# remove whitespaces
	r_input = list(str(r_input).replace(' ', ''))
	tokens = []
	tmp = None
	for i in range(len(r_input)):
		if r_input[i] in ('+','-','*', '/', '(',')'):
			#flush temporary numbers
			if not tmp == None:
				tokens.append(tmp)
				tmp = None
			tokens.append(r_input[i])
		if r_input[i].isdigit():
			if tmp == None:
				tmp = r_input[i]
			else:
				tmp += r_input[i]
	if not tmp == None:
		#flush in case of no parentheses
		tokens.append(tmp)
	return tokens


class Parser():
	def parse(tokens):
		return Parser(tokens).add_sub()


	def __init__(self, r_input):
		if len(r_input) == 0:
			return 0
		self.token = r_input
		self.curr = r_input[0]#safe, we just tested the length

	def consume(self):
		self.token = self.token[1:]
		if len(self.token) > 0:
			self.curr = self.token[0] # safe, in if
		else:
			self.curr = None

	def add_sub(self):
		#left side
		result = self.mult_div()
		while self.curr in ('+','-'):
			if self.curr == '+':
				self.consume()
				#right side
				result += self.mult_div()
			else:
				self.consume()
				result -= self.mult_div()
		return result

	def expression(self):
		result = None
		if self.curr == '(':
			self.consume()
			result = self.add_sub()
			self.consume()
		else:
			#numeric
			result = int(self.curr)
			self.consume()
		return result

	def mult_div(self):
		# same as add_sub
		# left side
		result = self.expression()
		while self.curr in ('*','/'):
			if self.curr == '*':
				self.consume()
				#right side
				result *= self.expression()
			else:
				self.consume()
				result /= self.expression()
		return result

def handle_request(req):
	req = base64.b64decode(req)
	tokens = tokenize(req)
	return Parser.parse(tokens)

app = Flask(__name__)

@app.route("/calculus")
def index():
	req = request.args.get('query', default = 1, type = str)
	try:
		num =  handle_request(req)
		print(num)
		return json.dumps({'error':False, 'result': num})
	except:
		return json.dumps({'error':True, 'message':'Could not parse expression'})


def test_default():
	string = "MiAqICgyMy8oMyozKSktIDIzICogKDIqMyk="
	assert handle_request(string) == -132.88888888888889


def test_add_sub():
	arr = [[ b'1+3', 1+3],[b'4-2', 4-2], [b'12+4-3-1-0', 12+4-3-1-0]]
	for [string, num] in arr:
		string = base64.b64encode(string)
		assert handle_request(string) == num

def test_mul_sub():
	arr = [[ b'2*3', 2*3],[b'0*9', 0*9],[b'9/2', 9/2], [b'12/4*3*1',12/4*3*1]]
	for [string, num] in arr:
		string = base64.b64encode(string)
		assert handle_request(string) == num

def test_both():
	arr = [[ b'2*3+1', 2*3+1],[b'0*9+3/2', 0*9+3/2], [b'1+12/4*3*1-9',1+12/4*3*1-9]]
	for [string, num] in arr:
		string = base64.b64encode(string)
		assert handle_request(string) == num

def test_paren():
	arr = [[ b'2*(3+1)', 2*(3+1)],[b'0*(9+3/2)', 0*(9+3/2)], [b'(1)+(12/((4*3))*1-9)',(1)+(12/((4*3))*1-9)]]
	for [string, num] in arr:
		string = base64.b64encode(string)
		assert handle_request(string) == num