import unittest
from splitnodes import split_nodes_delimiter
from textnode import TextNode, TextType

class TestSplitNodesDelimiter(unittest.TestCase):

	def test_split_with_code(self):
		node = TextNode("This is `code` here", TextType.TEXT)
		new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
		self.assertEqual(len(new_nodes), 3)
		self.assertEqual(new_nodes[0].text, "This is ")
		self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
		self.assertEqual(new_nodes[1].text, "code")
		self.assertEqual(new_nodes[1].text_type, TextType.CODE)
		self.assertEqual(new_nodes[2].text, " here")
		self.assertEqual(new_nodes[2].text_type, TextType.TEXT)

	def test_split_with_no_delimiter(self):
		node = TextNode("No delimiters here", TextType.TEXT)
		new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
		self.assertEqual(len(new_nodes), 1)
		self.assertEqual(new_nodes[0].text, "No delimiters here")
		self.assertEqual(new_nodes[0].text_type, TextType.TEXT)

	def test_split_ignores_non_text_nodes(self):
		node = TextNode("Already code", TextType.CODE)
		new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
		self.assertEqual(len(new_nodes), 1)
		self.assertEqual(new_nodes[0], node)

	def test_unmatched_delimiter_raises(self):
		node = TextNode("This is `broken code", TextType.TEXT)
		with self.assertRaises(ValueError):
			split_nodes_delimiter([node], "`", TextType.CODE)


if __name__ == "__main__":
	unittest.main()

