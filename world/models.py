import traceback
from datetime import datetime
from typing import Any, Optional

from django.contrib.auth.models import User
from django.db import models

from django.db.models import Model, Manager, CharField, JSONField, ForeignKey, QuerySet, ManyToManyField, DateTimeField, TextField, BooleanField

from app.logger import logger

class LogicManager:
	def __init__(self, entity: 'Entity'):
		self.entity = entity

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
			raise Exception(f"Improper action {obj}")
		logger.debug(f"Got: k = {key}, v = {values}")
		return key, values

	def evaluate_token(self, token: str) -> Any:
		"""Return object's value, which may be an immediate value or anotherobject"""
		logger.debug(f"Token: {token}")
		if isinstance(token, str):
			token = token.lower()
			if token.startswith("self."):
				var: str = token.replace("self.", "")
				if var in self.entity.properties:
					val = self.entity.properties.get(var)
				else:
					logger.error(f"{var} is not in {self.entity.properties}")
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

	def make_numeric(self, data: list) -> list:
		"""If any of values in a list isn't a float, attempt to translate it"""
		if not all([isinstance(val, (int, float)) for val in data]):
			data = [self.evaluate_token(value) for value in data]
		if not all([isinstance(val, (int, float)) for val in data]):
			raise Exception("Not all values are numeric")
		return data

	def validate_for_eq(self, data: list) -> list:
		"""If any of values in a list isn't an immedaite comparable value, attempt to translate it"""
		if not all([isinstance(val, (bool, int, float)) for val in data]):
			data = [self.evaluate_token(value) for value in data]
		if not all([isinstance(val, (bool, int, float)) for val in data]):
			raise Exception("Not all values are comparible")
		return data

	@staticmethod
	def validate_input_size(data: list, size: int) -> None:
		"""Check that the value size matches condition"""
		if len(data) != size:
			raise Exception("Invalid value size")


class LogicObject(Model):
	objects: Manager = Manager()
	name: str = CharField(max_length=60)
	logic: dict = JSONField(default=dict)

	class Meta:
		abstract = True


class State(LogicObject):
	"""Character status effects"""

	def __str__(self) -> str:
		return f"State({self.name})"


class Task(LogicObject):
	"""Character tasks"""

	#
	# class States(models.TextChoices):
	# 	scheduled = 'scheduled'
	# 	working = 'working'
	# 	complete = 'complete'
	#
	# state: str = CharField(max_length=10, choices=States.choices)

	def __str__(self) -> str:
		return f"Task({self.name})"


class Entity(Model):
	"""Character"""
	objects: Manager = Manager()
	world: 'WorldEnvironment' = ForeignKey('WorldEnvironment', on_delete=models.CASCADE)
	name: str = CharField(max_length=60)
	creator: User = ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
	properties: dict = JSONField(default=dict)
	states: list[State] | QuerySet = ManyToManyField(State)
	tasks: list[Task] | QuerySet = ManyToManyField(Task)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.logic_manager = LogicManager(self)
		self.command_response: dict = {}
		if 'can_hear' in self.properties:
			self.command_response["sleep"] = lambda: self.add_task("Sleep")
			self.command_response["hello"] = lambda: self.say("Hello!")

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
		if 'can_hear' in self.properties:
			for command, response in self.command_response.items():
				if command in text:
					response()

	def check_state(self, state_name: str) -> tuple[Optional["State"], bool]:
		"""Check if State by name is present in the Entity and return it"""
		try:
			state: State = State.objects.get(name=state_name)
			if state in self.states.all():
				return state, True
			else:
				return state, False
		except State.DoesNotExist:
			return None, False

	def check_task(self, task_name: str) -> tuple[Optional["Task"], bool]:
		"""Check if Task by name is present in the Entity and return it"""
		try:
			task: Task = Task.objects.get(name=task_name)
			if task in self.tasks.all():
				return task, True
			else:
				return task, False
		except Task.DoesNotExist:
			return None, False

	def add_state(self, state_name: str) -> None:
		"""Add a State to the list of states, create a new one if needed"""
		logger.debug(f"Add state: {state_name}")
		state, present = self.check_state(state_name)
		if state is None:
			state, new = State.objects.get_or_create(name=state_name)
		if not present:
			self.states.add(state)
			self.say(f"State added: {state.name}")
			self.on_start(state)

	def add_task(self, task_name: str) -> None:
		"""Add a Task to the list of tasks, create a new one if needed"""
		logger.debug(f"Add task: {task_name}")
		task, present = self.check_task(task_name)
		if task is None:
			task, new = Task.objects.get_or_create(name=task_name)
		if not present:
			self.tasks.add(task)
			self.say(f"Task added: {task.name}")
			self.on_start(task)

	def remove_state(self, state_name: str) -> None:
		"""Unlist a State if present"""
		logger.debug(f"Remove state: {state_name}")
		if state_name == "Any":
			raise Exception(f"State {state_name} cannot be removed")
		else:
			state, present = self.check_state(state_name)
		if state is None:
			logger.warning(f"State {state_name} not found")
			return
		if present:
			self.states.remove(state)
			self.say(f"State remove: {state.name}")

	def remove_task(self, task_name: str) -> None:
		"""Unlist a Task if present"""
		logger.debug(f"Remove task: {task_name}")
		if task_name == "this":
			task, present = self.check_task(self.name)
		else:
			task, present = self.check_task(task_name)
		if task is None:
			logger.warning(f"Task {task_name} not found")
			return
		if present:
			self.tasks.remove(task)
			self.say(f"Task remove: {task.name}")

	def on_start(self, logic_object: LogicObject):
		on_start: dict = logic_object.logic.get("on_start")
		if on_start is not None:
			for start_action in on_start:
				self.execute(start_action)
		else:
			logger.warning("No on_start logic found")

	def complete_task(self, task_name: str) -> None:
		logger.debug(f"Complete task: {task_name}")
		task, present = self.check_task(task_name)
		if task is None:
			logger.warning(f"Task {task_name} not found")
			return
		if present:
			self.on_complete(task)
			self.remove_task(task_name)

	def on_complete(self, logic_object: LogicObject):
		on_complete: dict = logic_object.logic.get("on_complete")
		if on_complete is not None:
			for complete_action in on_complete:
				self.execute(complete_action)
		else:
			logger.warning("No on_complete logic found")
		self.say(f"Task complete: {logic_object.name}")

	def set_default_state(self) -> None:
		state, present = self.check_state("Any")
		if state is None:
			raise Exception("Any state is mandatory and should have been loaded with fixtures")
		else:
			logger.debug(f"Create Any state: {state}")
			self.states.add(state)
		logger.debug(f"Any state: {state}, present: {present}")

	def set_idle(self) -> None:
		"""Create Idle state logic if not created"""
		state, present = self.check_state("Idle")
		if state is None:
			raise Exception("Idle state is mandatory and should have been loaded with fixtures")
		else:
			logger.debug(f"Create Idle state: {state}")
			self.states.add(state)
		logger.debug(f"Idle state: {state}, present: {present}")

	def check_idle(self):
		if len(self.tasks.all()) == 0:
			self.set_idle()
		else:
			self.remove_state("Idle")

	def get_tick_process(self, logic_object: LogicObject):
		logger.debug(f"{logic_object} Logic: {logic_object.logic}")
		on_tick: dict = logic_object.logic.get("on_tick")
		if on_tick is not None:
			for tick_action in on_tick:
				self.check_conditions_and_execute(tick_action)
		else:
			logger.warning("No on_tick logic found")

	def on_tick(self) -> None:
		"""On time step"""
		self.check_idle()

		for task in self.tasks.all():
			logger.debug(task)
			self.get_tick_process(task)

		for state in self.states.all():
			logger.debug(state)
			self.get_tick_process(state)

	def check_conditions_and_execute(self, tick_action: dict) -> None:
		"""handle logic json"""
		conditions: list = tick_action.get("conditions")
		logger.debug(f"Conditions: {conditions}")
		if conditions:
			check: bool = self.evaluate_operator("and", conditions)
		else:
			check = True
		logger.debug(f"Check: {check}")
		if check:
			self.execute(tick_action)

	def set_from_math(self, statement: dict):
		var = statement.get("var")
		math = statement.get("value")
		if isinstance(math, dict) or isinstance(math, list):
			logger.debug(f"Eval, {math}")
			operator, values = self.logic_manager.get_code(math)
			val = self.evaluate_operator(operator, values)
		else:
			val = math
		logger.debug(f"Result: {val}")
		if var.startswith("self."):
			var = var.replace("self.", "")
		logger.debug(f"Properties: {self.properties}")
		self.set_property(var, val)

	def run_command(self, command: str, statement: dict | str):
		logger.debug(f"Command {command}, {statement}")
		if command == 'set':
			self.set_from_math(statement)
		elif command == 'state_add':
			self.add_state(statement)
		elif command == 'state_remove':
			self.remove_state(statement)
		elif command == 'task_add':
			self.add_task(statement)
		elif command == 'task_remove':
			self.remove_task(statement)
		elif command == 'task_complete':
			self.complete_task(statement)

	def execute(self, state_action: dict):
		actions: dict = state_action.get("actions")
		for action in actions:
			logger.debug(f"Action: {action}")
			for command, statement in action.items():
				self.run_command(command, statement)

	def evaluate_operator(self, operator: str, values: list):
		"""Calculate value"""
		logger.debug(f"Math, oper: {operator}, values: {values}")

		if operator == "==" or operator == "eq":
			self.logic_manager.validate_input_size(values, 2)
			values = self.logic_manager.validate_for_eq(values)
			val1 = values[0]
			val2 = values[1]
			result = val1 == val2
		elif operator == ">" or operator == "gt":
			self.logic_manager.validate_input_size(values, 2)
			values = self.logic_manager.make_numeric(values)
			result = values[0] > values[1]
		elif operator == ">=" or operator == "gte":
			self.logic_manager.validate_input_size(values, 2)
			values = self.logic_manager.make_numeric(values)
			result = values[0] >= values[1]
		elif operator == "<" or operator == "lt":
			self.logic_manager.validate_input_size(values, 2)
			values = self.logic_manager.make_numeric(values)
			result = values[0] < values[1]
		elif operator == "<=" or operator == "lte":
			self.logic_manager.validate_input_size(values, 2)
			values = self.logic_manager.make_numeric(values)
			result = values[0] <= values[1]
		elif operator == "and":
			values = self.make_boolean(values)
			result = all(values)
		elif operator == "not":
			values = self.make_boolean(values)
			result = not any(values)
		elif operator == "or":
			values = self.make_boolean(values)
			result = any(values)
		elif operator == "sum":
			values = self.logic_manager.make_numeric(values)
			result = sum(values)
		elif operator == "state_has":
			result = self.has_states(values)
		else:
			raise Entity.InvalidOperator
		logger.debug(f"Math, result: {result}")
		return result

	def has_states(self, values: list | str) -> bool:
		if isinstance(values, str):
			state_name = values
			state, present = self.check_state(state_name)
			result = present
		else:
			result = True
			for state_name in values:
				state, present = self.check_state(state_name)
				if not present:
					result = False
					break
		return result

	def make_boolean(self, data: list) -> list:
		"""If any of values in a list isn't a boolean, attempt to translate it"""
		if not all([isinstance(val, bool) for val in data]):
			real_values = []
			if isinstance(data, list):
				for value in data:
					logger.debug(f"Value: {value}")
					o, v = self.logic_manager.get_code(value)
					real_values.append(self.evaluate_operator(o, v))
			elif isinstance(data, dict):
				for o, v in data.items():
					real_values.append(self.evaluate_operator(o, v))
			logger.debug(f"Real values: {real_values}")
			data = real_values
		if not all([isinstance(val, bool) for val in data]):
			raise Exception("Not all values are boolean")
		return data


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
	disabled: bool = BooleanField(default=False)
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
	def logs(self) -> list['WorldLog']:
		"""list logs"""
		return WorldLog.objects.filter(world=self)

	def to_json(self) -> dict:
		"""export data"""
		data: dict = {
			"name": self.name,
			"created": self.creation_time,
			"disabled": self.disabled,
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
			if not self.disabled:
				for entity in self.entities:
					if entity.properties.get("alive", False):
						entity.on_tick()
		except Exception as e:
			logger.error(f"{e}, {traceback.format_exc()}")
			raise e

	def listen(self, user: User, text: str) -> None:
		"""react to user input"""
		try:
			entry: str = f"{user} says: \"{text}\""
			SystemLog.objects.create(text=entry)
			self.log(entry)
			if text.lower().startswith("/help"):
				self.log("/help -- this text\n/disable -- Pause\n/enable -- Unpause\n /say % -- command")
			elif text.lower().startswith("/disable"):
				self.disabled = True
				self.save(update_fields=['disabled'])
				self.log("The world is frozen")
			elif text.lower().startswith("/enable"):
				self.disabled = False
				self.save(update_fields=['disabled'])
			elif text.lower().startswith("/say "):
				for entity in self.entities:
					entity.listen(text)
			elif text.lower().startswith("/rename "):
				parameters = text.split(' ')
				if len(parameters) != 3:
					self.log("Invalid command")
				else:
					for entity in self.entities:
						if entity.name == parameters[1]:
							entity.say(f"Changing to a new name: {parameters[2]}")
							entity.name = parameters[2]
							entity.save(update_fields=['name'])
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
