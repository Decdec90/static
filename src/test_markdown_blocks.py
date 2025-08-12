import unittest
from markdown_blocks import markdown_to_blocks, BlockType, block_to_block_type, extract_title

class TestMarkdownToBlocks(unittest.TestCase):
	def test_basic_blocks(self):
		markdown = "# Heading\n\nThis is a paragraph.\n\n- Item 1\n- Item 2"
		expected = [
			"# Heading",
			"This is a paragraph.",
			"- Item 1\n- Item 2"
		]
		self.assertEqual(markdown_to_blocks(markdown), expected)

	def test_extra_whitespace(self):
		markdown = "   # Heading   \n\n   Paragraph text   \n\n\n\n- List item"
		expected = [
			"# Heading",
			"Paragraph text",
			"- List item"
		]
		self.assertEqual(markdown_to_blocks(markdown), expected)

	def test_only_empty_lines(self):
		markdown = "\n\n\n\n"
		self.assertEqual(markdown_to_blocks(markdown), [])

	def test_block_type_heading_levels(self):
		self.assertEqual(block_to_block_type("# H1"), BlockType.HEADING)
		self.assertEqual(block_to_block_type("###### H6"), BlockType.HEADING)

	def test_block_type_code_fence(self):
		block = "```\nprint('hi')\n```"
		self.assertEqual(block_to_block_type(block), BlockType.CODE)

	def test_block_type_quote_multiline(self):
		block = "> line one\n> line two\n> line three"
		self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

	def test_block_type_unordered_list(self):
		block = "- one\n- two\n- three"
		self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

	def test_block_type_ordered_list(self):
		block = "1. first\n2. second\n3. third"
		self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

	def test_block_type_paragraph_fallback(self):
		block = "Just a normal paragraph with *markdown* **inside**."
		self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

	def test_extract_title_basic(self):
		md = "# Hello"
		self.assertEqual(extract_title(md), "Hello")

	def test_extract_title_trims_spaces(self):
		md = "   #   My Title   \n\nSome content"
		self.assertEqual(extract_title(md), "My Title")

	def test_extract_title_ignores_other_headers(self):
		md = "## Not it\n### Also not it\n# Real One\nParagraph"
		self.assertEqual(extract_title(md), "Real One")

	def test_extract_title_uses_first_h1(self):
		md = "# First Title\n\n# Second Title"
		self.assertEqual(extract_title(md), "First Title")

	def test_extract_title_ignores_no_space_after_hash(self):
		md = "#Hello (no space)\n\n# Proper Title"
		self.assertEqual(extract_title(md), "Proper Title")

	def test_extract_title_raises_when_missing(self):
		md = "No h1 here\n## Subheading only\nParagraph text"
		with self.assertRaises(ValueError):
			extract_title(md)


if __name__ == "__main__":
	unittest.main()
