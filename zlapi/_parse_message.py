def Parse(text, styles=None, parse_mode=None):
	styles = styles or []
	if parse_mode == "Markdown":
		new_text, parse_list = parse_markdown(text)
	else:
		new_text, parse_list = markdown_message(text)
	
	return new_text, parse_list


def parse_markdown(text):
	"""Parses Markdown text and returns a list of Markdown elements.

	Args:
		text (str): The Markdown text to parse.

	Returns:
		list: A list of dictionaries, each representing a Markdown element.
		Each dictionary has the following keys:
			- 'start': The starting index of the element in the text.
			- 'end': The ending index of the element in the text.
			- 'length': The length of the element in the text.
			- 'text': The text content of the element.
			- 'char_len': The length of the Markdown character used for the element.
			- 'type': The type of Markdown element (e.g., 'bold', 'italic').
	"""

	markdown_elements = []
	markdown = {
		"**": "bold",
		"__": "underline",
		"_": "italic",
		"~~": "strike"
	}

	temp_text = text
	while any(temp_text.count(char) >= 2 for char in markdown.keys()):
		
		markup_start_positions = {
			char: temp_text.find(char)
			for char in markdown.keys()
		}

		
		sorted_markup_start_positions = dict(sorted(markup_start_positions.items(), key=lambda item: item[1]))
		
		for char, start in sorted_markup_start_positions.items():
			if start < 0:
				continue

			end = temp_text.rfind(char, start + len(char))
			
			if temp_text[start + len(char):end].count(char) >= 2:
				end = temp_text.find(char, start + len(char))

			if end < 0:
				continue
			
			element = {
				"start": start,
				"end": end,
				"length": end - start - len(char) + 1,
				"text": temp_text[start + len(char):end],
				"char_len": len(char),
				"type": markdown[char]
			}
			markdown_elements.append(element)
			
			temp_text = temp_text[:start] + temp_text[start + len(char):end] + temp_text[end + len(char):]
			break
	
	markdown_elements = sorted(markdown_elements, key=lambda x: x['start'])
	
	for element in markdown_elements:
		text = text[:element["start"]] + text[element["start"] + element["char_len"]:element["end"]] + text[element["end"] + element["char_len"]:]
		element["start"] -= 1
		element["end"] += 2
	
	return text, markdown_elements


def markdown_message(text):
	except_list = []
	markdown_list = []
	markdown_chars = {
		"<b>": "bold",
		"<i>": "italic",
		"<u>": "underline",
		"<s>": "strike",
	}
	for char, name in markdown_chars.items():
		start = 0
		while True:
			start = text.find(char, start)
			if start == -1:
				break
			
			end = text.find("</" + char[1:], start)
			if end == -1:
				break
			
			length = len(text[start + len(char):end])
			text = text.replace(char, "", 1)
			text = text.replace("</"+char[1:], "", 1)
			
			for charex in markdown_chars:
				if charex in text[start:end]:
					startex = text[start:end].find(charex)
					endex = text[start:end].find("</"+charex[1:], startex)
					if endex == -1:
						endex = text[end:].find("</"+charex[1:])
						if endex == -1:
							continue
						else:
							length -= 3
					else:
						length -= 7
					
					# except_list.append({"name": charex, "start": startex, "end": endex})
			
			markdown_list.append({
				"start": start - 1,
				"end": end + len(name),
				"length": length,
				"type": name,
				# "text": markdown_text
			})
			start = 0
	return text, markdown_list


def parse_html(text):
	"""Parses Markdown text and returns a list of Markdown elements.

	Args:
		text (str): The Markdown text to parse.

	Returns:
		list: A list of dictionaries, each representing a Markdown element.
		Each dictionary has the following keys:
			- 'start': The starting index of the element in the text.
			- 'end': The ending index of the element in the text.
			- 'length': The length of the element in the text.
			- 'text': The text content of the element.
			- 'char_len': The length of the Markdown character used for the element.
			- 'type': The type of Markdown element (e.g., 'bold', 'italic').
	"""

	markdown_elements = []
	markdown = {
		"<b>": "bold",
		"<u>": "underline",
		"<i>": "italic",
		"<s>": "strike"
	}

	temp_text = text
	while any(temp_text.count(char) >= 1 and temp_text.count("</" + char[1:]) >= 1 for char in markdown.keys()):
		
		markup_start_positions = {
			char: temp_text.find(char)
			for char in markdown.keys()
		}

		
		sorted_markup_start_positions = dict(sorted(markup_start_positions.items(), key=lambda item: item[1]))
		
		for char, start in sorted_markup_start_positions.items():
			if start < 0:
				continue

			end = temp_text.rfind("</" + char[1:], start + len(char))
			
			if temp_text[start + len(char):end].count("</" + char[1:]) >= 1:
				end = temp_text.find("</" + char[1:], start + len(char))

			if end < 0:
				continue
			
			element = {
				"start": start,
				"end": end,
				"length": end - start - len(char),
				"text": temp_text[start + len(char):end],
				"char_len": len(char),
				"type": markdown[char]
			}
			markdown_elements.append(element)
			
			temp_text = temp_text[:start] + temp_text[start + len(char):end] + temp_text[end + len(char) + 1:]
			break
	
	markdown_elements = sorted(markdown_elements, key=lambda x: x['start'])
	
	for element in markdown_elements:
		text = text[:element["start"]] + text[element["start"] + element["char_len"]:element["end"]] + text[element["end"] + element["char_len"] + 1:]
		element["start"] -= 1
	
	return text, markdown_elements