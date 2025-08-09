import re
from textnode import TextNode, TextType
from splitnodes import split_nodes_delimiter

def extract_markdown_images(text):
	# ![alt](url)
	pattern = r'!\[(.*?)\]\((.*?)\)'
	return re.findall(pattern, text)

def extract_markdown_links(text):
	# [text](url) but NOT images (exclude leading '!')
	pattern = r'(?<!!)\[(.*?)\]\((.*?)\)'
	return re.findall(pattern, text)


def split_nodes_image(old_nodes):
	new_nodes = []
	for node in old_nodes:
		if node.text_type != TextType.TEXT:
			new_nodes.append(node)
			continue

		pos = 0
		for alt_text, url in extract_markdown_images(node.text):
			match_str = f"![{alt_text}]({url})"
			start = node.text.find(match_str, pos)
			if start > pos:
				new_nodes.append(TextNode(node.text[pos:start], TextType.TEXT))
			new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
			pos = start + len(match_str)

		if pos < len(node.text):
			new_nodes.append(TextNode(node.text[pos:], TextType.TEXT))
	return new_nodes

def split_nodes_link(old_nodes):
	new_nodes = []
	for node in old_nodes:
		if node.text_type != TextType.TEXT:
			new_nodes.append(node)
			continue

		pos = 0
		for link_text, url in extract_markdown_links(node.text):
			match_str = f"[{link_text}]({url})"
			start = node.text.find(match_str, pos)
			if start > pos:
				new_nodes.append(TextNode(node.text[pos:start], TextType.TEXT))
			new_nodes.append(TextNode(link_text, TextType.LINK, url))
			pos = start + len(match_str)

		if pos < len(node.text):
			new_nodes.append(TextNode(node.text[pos:], TextType.TEXT))
	return new_nodes

def text_to_textnodes(text):
	nodes = [TextNode(text, TextType.TEXT)]
	nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
	nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
	nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
	nodes = split_nodes_image(nodes)
	nodes = split_nodes_link(nodes)
	return nodes
