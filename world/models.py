import traceback
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager, CharField, ForeignKey, DateTimeField, ManyToManyField, Model, QuerySet, TextField, JSONField

from app.logger import logger


class SystemLog(Model):
	objects: Manager = Manager()
	time: datetime = DateTimeField(auto_now_add=True)
	text: str = TextField()

	def to_json(self) -> dict:
		data: dict = {
			"time": self.time.strftime("%m-%d-%Y %H:%M:%S"),
			"text": self.text
		}
		return data


class WorldEnviroment(Model):
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	creator: User = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	creation_time: datetime = DateTimeField(auto_now_add=True)
	last_update: datetime = DateTimeField(auto_now_add=True)
	entities: list["Entity"] | QuerySet = ManyToManyField("Entity")

	def to_json(self):
		data: dict = {
			"name": self.name,
			"entities": [entity.to_json() for entity in self.entities.all()],
			"logs": [log.to_json() for log in self.logs]
		}
		return data

	def log(self, text: str) -> None:
		WorldLog.objects.create(world=self, text=text)

	@property
	def logs(self) -> list["WorldLog"]:
		return WorldLog.objects.filter(world=self)

	def advance(self):
		try:
			for entity in self.entities.all():
				entity.on_tick()
		except Exception as e:
			logger.error(f"{e}, {traceback.format_exc()}")
			raise e


class WorldLog(Model):
	objects: Manager = Manager()
	world: WorldEnviroment = ForeignKey(WorldEnviroment, on_delete=models.CASCADE)
	time: datetime = DateTimeField(auto_now_add=True)
	text: str = TextField()

	def to_json(self) -> dict:
		data: dict = {
			"time": self.time.strftime("%m-%d-%Y %H:%M:%S"),
			"text": self.text
		}
		return data


class State(Model):
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	logic: dict = JSONField(default=dict)


class Task(Model):
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	logic: dict = JSONField(default=dict)


def default_properties():
	default_data = {
		"alive": True,
		"health": 100.0,
		"stamina": 100.0
	}
	return default_data


class Entity(Model):
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	creator: User = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	properties: dict = JSONField(default=default_properties)
	states: list[State] | QuerySet = ManyToManyField(State)
	tasks: list[Task] | QuerySet = ManyToManyField(Task)

	class InvalidToken(Exception):
		pass

	def to_json(self):
		data: dict = {
			"name": self.name,
			"properties": self.properties
		}
		return data

	def check_state(self, state_name: str) -> tuple["State", bool]:
		try:
			state = State.objects.get(name=state_name)
			if state in self.states.all():
				return state, True
			else:
				return state, False
		except State.DoesNotExist:
			return None, False

	def check_task(self, task_name: str) -> tuple["Task", bool]:
		try:
			task = Task.objects.get(name=task_name)
			if task in self.tasks.all():
				return task, True
			else:
				return task, False
		except State.DoesNotExist:
			return None, False

	def on_tick(self):
		if len(self.tasks.all()) == 0:
			self.set_idle()

		for state in self.states.all():
			logger.debug(f"Logic: {state.logic}")
			on_tick: dict = state.logic.get("on_tick")
			if on_tick is not None:
				self.on_tick_process(on_tick)

	def set_idle(self):
		state, present = self.check_state("Idle")
		if state is None:
			idle_logic = {
				"on_tick": {
					"conditions": [
						{
							"and": [
								["==", ["self.alive", True]],
								[">", ["self.stamina", 0]]
							]
						}
					],
					"actions": [
						{
							"set": {
								"var": "self.stamina",
								"value": ["sum", ["self.stamina", -1]]
							}
						}
					]
				}
			}
			state, new = State.objects.get_or_create(
				name="Idle",
				logic=idle_logic
			)
		if not present:
			self.states.add(state)

	def on_tick_process(self, on_tick):
		main_operator = "and"
		conditions: list = on_tick.get("conditions")
		logger.debug(f"Conditions: {conditions}")
		check = self.evaluate_operator(main_operator, conditions)
		logger.debug(f"Check: {check}")
		if check:
			actions: dict = on_tick.get("actions")
			for action in actions:
				for command, statement in action.items():
					if command == 'set':
						logger.debug(f"Command {command}, {statement}")
						var = statement.get("var")
						math = statement.get("value")
						logger.debug(f"Eval, {math}")
						operator, values = self.get_code(math)
						val = self.evaluate_operator(operator, values)
						logger.debug(f"Result: {val}")
						if var.startswith("self."):
							var = var.replace("self.", "")
						logger.debug(f"Properties: {self.properties}")
						self.set_property(val, var)

	def set_property(self, val, var):
		self.properties[var] = val
		self.save(update_fields=["properties"])

	def get_code(self, obj) -> tuple[str, list]:
		logger.debug(f"Conversion of {obj}")
		if isinstance(obj, list) and len(obj) == 2:
			key = obj[0]
			values = obj[1]
		elif isinstance(obj, dict) and len(obj.keys()) == 1:
			key = list(obj.keys())[0]
			values = list(obj.values())[0]
		else:
			raise Exception("Improper action")
		logger.debug(f"Got: k = {key}, v = {values}")
		return key, values

	def check_all_conditions(self, checks):
		check_results = []
		for check in checks:
			logger.debug(f"Check: {check}")
			try:
				conj_met = self.evaluate_condition(check)
			except Entity.InvalidToken:
				conj_met = True
			check_results.append(conj_met)
		return check_results

	def evaluate_condition(self, check):
		logger.debug(f"Eval: {check}")
		operator, values = self.get_code(check)
		real_values = []
		for value in values:
			real_values.append(self.evaluate_token(value))
		conj_met = self.evaluate_operator(operator, real_values)
		logger.debug(f"Eval result: {conj_met}")
		return conj_met

	def evaluate_token(self, token: str):
		logger.debug(f"Token: {token}")
		if isinstance(token, str):
			token = token.lower()
			if token.startswith("self."):
				var = token.replace("self.", "")
				if var in self.properties:
					val = self.properties.get(var)
				else:
					raise Entity.InvalidToken
			else:
				if token in ["true"]:
					val = True
				elif token in ["false"]:
					val = False
				elif token.isnumeric():
					val = float(token)
				else:
					raise Entity.InvalidToken
		else:
			val = token
		logger.debug(f"Value: {val}")
		return val

	def evaluate_operator(self, operator: str, values: list):
		logger.debug(f"Math, oper: {operator}, values: {values}")

		if operator == "==" or operator == "eq":
			self.validate_input_size(values, 2)
			values = self.validate_for_eq(values)
			val1 = values[0]
			val2 = values[1]
			result = val1 == val2
		elif operator == ">" or operator == "gt":
			self.validate_input_size(values, 2)
			values = self.make_numeric(values)
			result = values[0] > values[1]
		elif operator == "<" or operator == "lq":
			self.validate_input_size(values, 2)
			values = self.make_numeric(values)
			result = values[0] < values[1]
		elif operator == "and":
			values = self.make_boolean(values)
			result = all(values)
		elif operator == "or":
			values = self.make_boolean(values)
			result = any(values)
		elif operator == "sum":
			values = self.make_numeric(values)
			result = sum(values)
		else:
			raise Exception("Invalid operator")
		logger.debug(f"Math, result: {result}")
		return result

	def validate_input_size(self, data, size):
		if len(data) != size:
			raise Exception("Invalid value size")

	def make_numeric(self, data):
		if not all([isinstance(val, (int, float)) for val in data]):
			data = [self.evaluate_token(value) for value in data]
		if not all([isinstance(val, (int, float)) for val in data]):
			raise Exception("Not all values are numeric")
		return data

	def make_boolean(self, data):
		if not all([isinstance(val, bool) for val in data]):
			real_values = []
			for value in data:
				logger.debug(f"Value: {value}")
				o, v = self.get_code(value)
				real_values.append(self.evaluate_operator(o, v))
			logger.debug(f"Real values: {real_values}")
			data = real_values
		if not all([isinstance(val, bool) for val in data]):
			raise Exception("Not all values are boolean")
		return data

	def validate_for_eq(self, data):
		if not all([isinstance(val, (bool, int, float)) for val in data]):
			data = [self.evaluate_token(value) for value in data]
		if not all([isinstance(val, (bool, int, float)) for val in data]):
			raise Exception("Not all values are comparible")
		return data