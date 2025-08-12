# markdown_blocks.py
# End-to-end Markdown (block-level) parser -> HTML node tree

import re
from enum import Enum

from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import ParentNode
from inline_markdown import text_to_textnodes


class BlockType(Enum):
	PARAGRAPH = "paragraph"
	HEADING = "heading"
	CODE = "code"
	QUOTE = "quote"
	UNORDERED_LIST = "unordered_list"
	ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown: str):
	"""
	Split a full markdown document into logical blocks.

	- Normalizes CRLF to LF
	- Splits on one or more blank lines
	- Trims each block and drops empties
	"""
	text = markdown.replace("\r\n", "\n")
	blocks = re.split(r"\n\s*\n", text)
	return [b.strip() for b in blocks if b.strip()]


def extract_title(markdown: str) -> str:
	"""
	Return the first H1 ('# <title>') text; raise if none exists.
	"""
	for line in markdown.splitlines():
		line = line.strip()
		if line.startswith("# "):
			return line[2:].strip()
	raise ValueError("No H1 header found in markdown")


def block_to_block_type(block: str) -> BlockType:
	"""
	Classify a trimmed block into a BlockType.
	"""
	# fenced code
	if block.startswith("```") and block.endswith("```"):
		return BlockType.CODE

	# heading (1–6 #'s + space)
	if re.match(r"^#{1,6} ", block):
		return BlockType.HEADING

	lines = block.split("\n")

	# quote: every line starts with '>' optionally followed by space
	if all(re.match(r"^>\s?.*$", ln) for ln in lines):
		return BlockType.QUOTE

	# unordered list: every line starts with '-' or '*' + space
	if all(re.match(r"^(\*|-)\s+.+$", ln) for ln in lines):
		return BlockType.UNORDERED_LIST

	# ordered list: lines '1. x', '2. y' ... and numbers are 1..n
	matches = [re.match(r"^(\d+)\.\s+.+$", ln) for ln in lines]
	if all(m is not None for m in matches):
		nums = [int(m.group(1)) for m in matches]
		if nums == list(range(1, len(nums) + 1)):
			return BlockType.ORDERED_LIST

	return BlockType.PARAGRAPH


def _heading_level(block: str) -> int:
	"""
	Count leading '#' to determine heading level (assumes valid heading block).
	"""
	count = 0
	for ch in block:
		if ch == "#":
			count += 1
		else:
			break
	return count


def _strip_quote_markers(block: str) -> str:
	"""
	Remove leading '>' or '> ' from each line in a quote block.
	"""
	lines = block.split("\n")
	cleaned = []
	for ln in lines:
		if ln.startswith("> "):
			cleaned.append(ln[2:])
		elif ln.startswith(">"):
			cleaned.append(ln[1:])
		else:
			cleaned.append(ln)
	return "\n".join(cleaned)


def _strip_ul_markers(block: str) -> str:
	"""
	Remove leading '- ' or '* ' from each line in an unordered list block.
	"""
	lines = block.split("\n")
	cleaned = [
		ln[2:] if (ln.startswith("- ") or ln.startswith("* ")) else ln
	for ln in lines]
	return "\n".join(cleaned)


def _strip_ol_markers(block: str) -> str:
	"""
	Remove leading '<number>. ' from each line in an ordered list block.
	"""
	lines = block.split("\n")
	cleaned = [re.sub(r"^\d+\.\s+", "", ln) for ln in lines]
	return "\n".join(cleaned)


def text_to_children(text: str):
	"""
	Run inline markdown on a text block and convert resulting TextNodes into HTML nodes.
	"""
	children = []
	for tn in text_to_textnodes(text):
		children.append(text_node_to_html_node(tn))
	return children


def markdown_to_html_node(markdown: str) -> ParentNode:
	"""
	Main converter: Markdown (string) -> root HTML ParentNode ('div').

	- Detects block type
	- For code/quote/list/paragraph, builds appropriate HTML structure
	- For inline text (most blocks), uses inline_markdown -> TextNodes -> HTML
	- ALWAYS constructs the root with a non-empty children list (prevents errors)
	"""
	blocks = markdown_to_blocks(markdown)

	children = []
	for block in blocks:
		btype = block_to_block_type(block)

		if btype == BlockType.HEADING:
			level = _heading_level(block)
			# skip the '<level> #' and following single space
			text = block[level + 1:]
			children.append(ParentNode(f"h{level}", text_to_children(text)))

		elif btype == BlockType.CODE:
			# retain inner text; no inline parsing inside <pre>
			inner = block[3:-3] if block.startswith("```") and block.endswith("```") else block
			code_leaf = text_node_to_html_node(TextNode(inner, TextType.CODE))
			children.append(ParentNode("pre", [code_leaf]))

		elif btype == BlockType.QUOTE:
			text = _strip_quote_markers(block)
			children.append(ParentNode("blockquote", text_to_children(text)))

		elif btype == BlockType.UNORDERED_LIST:
			items = []
			for raw in _strip_ul_markers(block).split("\n"):
				items.append(ParentNode("li", text_to_children(raw)))
			children.append(ParentNode("ul", items))

		elif btype == BlockType.ORDERED_LIST:
			items = []
			for raw in _strip_ol_markers(block).split("\n"):
				items.append(ParentNode("li", text_to_children(raw)))
			children.append(ParentNode("ol", items))

		else:  # paragraph
			children.append(ParentNode("p", text_to_children(block)))

	if not children:
		raise ValueError("No content blocks found in markdown")

	return ParentNode("div", children)
