from enum import Enum
import re
from textnode import text_node_to_html_node, TextNode, TextType
from htmlnode import ParentNode
from inline_markdown import text_to_textnodes

def markdown_to_blocks(markdown):
	# Split on double newlines to separate blocks
	blocks = markdown.split("\n\n")

	# Strip leading/trailing whitespace from each block and remove empty ones
	blocks = [block.strip() for block in blocks if block.strip() != ""]

	return blocks

class BlockType(Enum):
	PARAGRAPH = "paragraph"
	HEADING = "heading"
	CODE = "code"
	QUOTE = "quote"
	UNORDERED_LIST = "unordered_list"
	ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
	# Heading: 1–6 # followed by space
	if re.match(r"^#{1,6} ", block):
		return BlockType.HEADING

	# Code block: triple backticks at start and end
	if block.startswith("```") and block.endswith("```"):
		return BlockType.CODE

	# Quote: every line starts with >
	if all(line.startswith(">") for line in block.split("\n")):
		return BlockType.QUOTE

	# Unordered list: every line starts with "- "
	if all(line.startswith("- ") for line in block.split("\n")):
		return BlockType.UNORDERED_LIST

	# Ordered list: numbered 1., 2., 3., ...
	lines = block.split("\n")
	if all(re.match(r"^\d+\. ", line) for line in lines):
		return BlockType.ORDERED_LIST

	# Default: paragraph
	return BlockType.PARAGRAPH


def text_to_children(text):
	# parse inline markdown to TextNodes, then convert each to HTMLNode
	children = []
	for tn in text_to_textnodes(text):
		children.append(text_node_to_html_node(tn))
	return children

def _heading_level(block):
	# count leading #'s before the required space
	i = 0
	while i < len(block) and block[i] == '#':
		i += 1
	return max(1, min(6, i))

def _strip_quote_markers(block):
	lines = []
	for line in block.split("\n"):
		if line.startswith(">"):
			line = line[1:]
			if line.startswith(" "):
				line = line[1:]
		lines.append(line)
	return "\n".join(lines)

def _strip_ul_markers(block):
	return "\n".join([line[2:] if line.startswith("- ") else line for line in block.split("\n")])

def _strip_ol_markers(block):
	stripped = []
	for line in block.split("\n"):
		j = 0
		while j < len(line) and line[j].isdigit():
			j += 1
		if j < len(line) - 1 and line[j:j+2] == ". ":
			stripped.append(line[j+2:])
		else:
			stripped.append(line)
	return "\n".join(stripped)

def markdown_to_html_node(markdown):
	blocks = markdown_to_blocks(markdown)
	root = ParentNode("div", [])

	for block in blocks:
		btype = block_to_block_type(block)

		if btype == BlockType.HEADING:
			level = _heading_level(block)
			text = block[level+1:]
			node = ParentNode(f"h{level}", text_to_children(text))

		elif btype == BlockType.CODE:
			inner = block[3:-3] if block.startswith("```") and block.endswith("```") else block
			code_leaf = text_node_to_html_node(TextNode(inner, TextType.CODE))
			node = ParentNode("pre", [code_leaf])

		elif btype == BlockType.QUOTE:
			text = _strip_quote_markers(block)
			node = ParentNode("blockquote", text_to_children(text))

		elif btype == BlockType.UNORDERED_LIST:
			items = []
			for raw in _strip_ul_markers(block).split("\n"):
				items.append(ParentNode("li", text_to_children(raw)))
			node = ParentNode("ul", items)

		elif btype == BlockType.ORDERED_LIST:
			items = []
			for raw in _strip_ol_markers(block).split("\n"):
				items.append(ParentNode("li", text_to_children(raw)))
			node = ParentNode("ol", items)

		else:  # PARAGRAPH
			node = ParentNode("p", text_to_children(block))

		root.children.append(node)

	return root
