import traceback
from datetime import datetime
from typing import Any

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager, CharField, ForeignKey, DateTimeField, ManyToManyField, Model, QuerySet, TextField, JSONField

from app.logger import logger


class SystemLog(Model):
	"""Global logs"""
	objects: Manager = Manager()
	time: datetime = DateTimeField(auto_now_add=True)
	text: str = TextField()

	def __str__(self) -> str:
		return f"SystemLog({self.time})"

	def to_json(self) -> dict:
		"""export data"""
		data: dict = {
			"time": self.time.strftime("%m-%d-%Y %H:%M:%S"),
			"text": self.text
		}
		return data


class WorldEnvironment(Model):
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	creator: User = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	creation_time: datetime = DateTimeField(auto_now_add=True)
	last_update: datetime = DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"World({self.name})"

	@property
	def entities(self) -> list["Entity"] | QuerySet:
		"""list entitied"""
		return Entity.objects.filter(world=self)

	@property
	def logs(self) -> list["WorldLog"]:
		"""list logs"""
		return WorldLog.objects.filter(world=self)

	def to_json(self) -> dict:
		"""export data"""
		data: dict = {
			"name": self.name,
			"entities": [entity.to_json() for entity in self.entities],
			"logs": [log.to_json() for log in self.logs]
		}
		return data

	def log(self, text: str) -> None:
		"""save text"""
		WorldLog.objects.create(world=self, text=text)

	def advance(self) -> None:
		"""move all entities by one tick"""
		try:
			for entity in self.entities:
				if entity.properties.get("alive", True):
					entity.on_tick()
		except Exception as e:
			logger.error(f"{e}, {traceback.format_exc()}")
			raise e

	def listen(self, user: User, text: str) -> None:
		"""react to user input"""
		try:
			entry: str = f"{user} says: \"{text}\""
			SystemLog.objects.create(text=entry)
			self.log(text)
			for entity in self.entities:
				entity.listen(text)
		except Exception as e:
			logger.error(f"{e}, {traceback.format_exc()}")
			raise e


class WorldLog(Model):
	"""World journal"""
	objects: Manager = Manager()
	world: WorldEnvironment = ForeignKey(WorldEnvironment, on_delete=models.CASCADE)
	time: datetime = DateTimeField(auto_now_add=True)
	text: str = TextField()

	def __str__(self) -> str:
		return f"Log({self.world.name}, {self.time})"

	def to_json(self) -> dict:
		"""export data"""
		data: dict = {
			"time": self.time.strftime("%m-%d-%Y %H:%M:%S"),
			"text": self.text
		}
		return data


class State(Model):
	"""Character status effects"""
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	logic: dict = JSONField(default=dict)

	def __str__(self) -> str:
		return f"State({self.name})"


class Task(Model):
	"""Character tasks"""
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	logic: dict = JSONField(default=dict)

	def __str__(self) -> str:
		return f"Task({self.name})"


def default_properties():
	default_data = {
		"alive": True,
		"health": 100.0,
		"stamina": 100.0
	}
	return default_data


class Entity(Model):
	"""Character"""
	objects: Manager = Manager()
	world: WorldEnvironment = ForeignKey(WorldEnvironment, on_delete=models.CASCADE)
	name: str = CharField(max_length=60)
	creator: User = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	properties: dict = JSONField(default=default_properties)
	states: list[State] | QuerySet = ManyToManyField(State)
	tasks: list[Task] | QuerySet = ManyToManyField(Task)

	class InvalidToken(Exception):
		pass

	class InvalidOperator(Exception):
		pass

	def __str__(self) -> str:
		return f"Entity({self.name})"

	def to_json(self) -> dict:
		"""export data"""
		data: dict = {
			"name": self.name,
			"properties": self.properties,
			"states": [state.name for state in self.states.all()],
			"tasks": [task.name for task in self.tasks.all()]
		}
		return data

	def check_state(self, state_name: str) -> tuple["State", bool]:
		"""Check if State by name is present in the Entity and return it"""
		try:
			state = State.objects.get(name=state_name)
			if state in self.states.all():
				return state, True
			else:
				return state, False
		except State.DoesNotExist:
			return None, False

	def check_task(self, task_name: str) -> tuple["Task", bool]:
		"""Check if Task by name is present in the Entity and return it"""
		try:
			task = Task.objects.get(name=task_name)
			if task in self.tasks.all():
				return task, True
			else:
				return task, False
		except Task.DoesNotExist:
			return None, False

	def add_state(self, state_name: str) -> None:
		"""Add a State to the list of states, create a new one if needed"""
		state, present = self.check_state(state_name)
		if state is None:
			state, new = State.objects.get_or_create(name=state_name)
		if not present:
			logger.debug(f"Add state: {state.name}")
			self.states.add(state)
			self.say(f"State added: {state.name}")

	def add_task(self, task_name: str) -> None:
		"""Add a Task to the list of tasks, create a new one if needed"""
		task, present = self.check_task(task_name)
		if task is None:
			task, new = Task.objects.get_or_create(name=task_name)
		if not present:
			logger.debug(f"Add task: {task.name}")
			self.tasks.add(task)
			self.say(f"Task added: {task.name}")

	def remove_state(self, state_name: str) -> None:
		"""Unlist a State if present"""
		state, present = self.check_state(state_name)
		if state is None:
			return
		if present:
			logger.debug(f"Remove state: {state.name}")
			self.states.remove(state)
			self.say(f"State remove: {state.name}")

	def remove_task(self, task_name: str) -> None:
		"""Unlist a Task if present"""
		task, present = self.check_task(task_name)
		if task is None:
			return
		if present:
			logger.debug(f"Remove task: {task.name}")
			self.tasks.remove(task)
			self.say(f"Task remove: {task.name}")

	def set_property(self, var: str, val: Any) -> None:
		"""Update property"""
		if not isinstance(val, (bool, int, float, str)):
			raise Exception("Invalid value")
		self.properties[var] = val
		self.save(update_fields=["properties"])

	def say(self, text: str) -> None:
		"""Add something to world chat"""
		entry: str = f"{self.name} says: \"{text}\""
		self.world.log(entry)

	def listen(self, text: str) -> None:
		"""Respond to user input"""
		if "sleep" in text:
			self.add_task("Sleep")

	def on_tick(self) -> None:
		"""On time step"""
		if len(self.tasks.all()) == 0:
			self.set_idle()
		else:
			self.remove_state("Idle")

		for task in self.tasks.all():
			logger.debug(f"Task Logic: {task.logic}")
			on_tick: dict = task.logic.get("on_tick")
			if on_tick is not None:
				for tick_action in on_tick:
					self.on_tick_process(tick_action)

		for state in self.states.all():
			logger.debug(f"State Logic: {state.logic}")
			on_tick: dict = state.logic.get("on_tick")
			if on_tick is not None:
				for tick_action in on_tick:
					self.on_tick_process(tick_action)

	def set_idle(self) -> None:
		"""Create Idle state logic if not created"""
		state, present = self.check_state("Idle")
		if state is None:
			raise Exception("Idle state is mandatory and should have been loaded with fixtures")
		else:
			logger.debug(f"Create Idle state: {state}")
			self.states.add(state)
		logger.debug(f"Idle state: {state}, present: {present}")

	def on_tick_process(self, tick_action: dict) -> None:
		"""handle logic json"""
		conditions: list = tick_action.get("conditions")
		logger.debug(f"Conditions: {conditions}")
		check = self.evaluate_operator("and", conditions)
		logger.debug(f"Check: {check}")
		if check:
			actions: dict = tick_action.get("actions")
			for action in actions:
				logger.debug(f"Action: {action}")
				for command, statement in action.items():
					logger.debug(f"Command {command}, {statement}")
					if command == 'set':
						var = statement.get("var")
						math = statement.get("value")
						if isinstance(math, dict) or isinstance(math, list):
							logger.debug(f"Eval, {math}")
							operator, values = self.get_code(math)
							val = self.evaluate_operator(operator, values)
						else:
							val = math
						logger.debug(f"Result: {val}")
						if var.startswith("self."):
							var = var.replace("self.", "")
						logger.debug(f"Properties: {self.properties}")
						self.set_property(var, val)
					elif command == 'addstate':
						self.add_state(statement)
					elif command == 'addtask':
						self.add_task(statement)

	def get_code(self, obj: Any) -> tuple[str, list]:
		"""Format logic object as a key-value pair, be it a one-key dict or a 2-size list"""
		logger.debug(f"Conversion of {obj}")
		if isinstance(obj, list) and len(obj) == 2:
			key: str = obj[0]
			values: list = obj[1]
		elif isinstance(obj, dict) and len(obj.keys()) == 1:
			key = list(obj.keys())[0]
			values = list(obj.values())[0]
		else:
			raise Exception("Improper action")
		logger.debug(f"Got: k = {key}, v = {values}")
		return key, values

	def evaluate_token(self, token: str) -> Any:
		"""Return object's value, which may be an immediate value or anotherobject"""
		logger.debug(f"Token: {token}")
		if isinstance(token, str):
			token = token.lower()
			if token.startswith("self."):
				var: str = token.replace("self.", "")
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
		"""Calculate value"""
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
		elif operator == ">=" or operator == "gte":
			self.validate_input_size(values, 2)
			values = self.make_numeric(values)
			result = values[0] >= values[1]
		elif operator == "<" or operator == "lt":
			self.validate_input_size(values, 2)
			values = self.make_numeric(values)
			result = values[0] < values[1]
		elif operator == "<=" or operator == "lte":
			self.validate_input_size(values, 2)
			values = self.make_numeric(values)
			result = values[0] <= values[1]
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
			raise Entity.InvalidOperator
		logger.debug(f"Math, result: {result}")
		return result

	def validate_input_size(self, data: list, size: int) -> None:
		"""Check that the value size matches condition"""
		if len(data) != size:
			raise Exception("Invalid value size")

	def make_numeric(self, data: list) -> list:
		"""If any of values in a list isn't a float, attempt to translate it"""
		if not all([isinstance(val, (int, float)) for val in data]):
			data = [self.evaluate_token(value) for value in data]
		if not all([isinstance(val, (int, float)) for val in data]):
			raise Exception("Not all values are numeric")
		return data

	def make_boolean(self, data: list) -> list:
		"""If any of values in a list isn't a boolean, attempt to translate it"""
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

	def validate_for_eq(self, data: list) -> list:
		"""If any of values in a list isn't an immedaite comparable value, attempt to translate it"""
		if not all([isinstance(val, (bool, int, float)) for val in data]):
			data = [self.evaluate_token(value) for value in data]
		if not all([isinstance(val, (bool, int, float)) for val in data]):
			raise Exception("Not all values are comparible")
		return data
