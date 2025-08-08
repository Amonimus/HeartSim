from bs4 import BeautifulSoup
from django import template

register: template.Library = template.Library()


def append_recursively(soup, tag, elem):
	def append_value():
		value_cell = row.append(soup.new_tag("td", type=type(value).__name__, contenteditable=True))
		if isinstance(value, dict):
			values_table = value_cell.append(soup.new_tag("table"))
			append_recursively(soup, values_table, value)
		elif isinstance(value, list):
			values_table = value_cell.append(soup.new_tag("table"))
			append_recursively(soup, values_table, value)
		else:
			value_cell.append(str(value))

	if isinstance(elem, dict):
		for key, value in elem.items():
			row = tag.append(soup.new_tag("tr"))
			key_cell = row.append(soup.new_tag("td", contenteditable=True))
			key_cell.append(key)
			append_value()
	elif isinstance(elem, list):
		for value in elem:
			row = tag.append(soup.new_tag("tr"))
			append_value()


@register.filter()
def logic_form(logic: dict):
	soup = BeautifulSoup("", features='html.parser')
	table = soup.append(soup.new_tag("table", type=type(logic).__name__))
	append_recursively(soup, table, logic)
	button = soup.append(soup.new_tag("button", onclick="SaveJson(this)"))
	button.append("Save")
	return soup.prettify()
