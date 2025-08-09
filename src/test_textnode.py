import unittest

from textnode import TextNode, TextType, text_node_to_html_node

class TestTextNode(unittest.TestCase):
	def test_eq(self):
		node = TextNode("This is a text node", TextType.BOLD)
		node2 = TextNode("This is a text node", TextType.BOLD)
		self.assertEqual(node, node2)

	def testtext_node_creation(self):
		node = TextNode("Hello", TextType.TEXT)
		self.assertEqual(node.text, "Hello")
		self.assertEqual(node.text_type, TextType.TEXT)
		self.assertIsNone(node.url)

	def testtext_node_with_url(self):
		node = TextNode("Click here", TextType.LINK, "https://example.com")
		self.assertEqual(node.text, "Click here")
		self.assertEqual(node.text_type, TextType.LINK)
		self.assertEqual(node.url, "https://example.com")

	def testtext_node_inequality_text(self):
		node1 = TextNode("Hello", TextType.TEXT)
		node2 = TextNode("Hi", TextType.TEXT)
		self.assertNotEqual(node1, node2)

	def testtext_node_inequality_type(self):
		node1 = TextNode("Hello", TextType.TEXT)
		node2 = TextNode("Hello", TextType.BOLD)
		self.assertNotEqual(node1, node2)

	def testtext_node_inequality_url(self):
		node1 = TextNode("Hello", TextType.TEXT)
		node2 = TextNode("Hello", TextType.TEXT, "https://example.com")
		self.assertNotEqual(node1, node2)

	def test_repr(self):
		node = TextNode("Hello", TextType.TEXT)
		expected_repr = "TextNode(Hello, TextType.TEXT, None)"
		self.assertEqual(repr(node), expected_repr)

	def test_text(self):
		node = TextNode("This is a text node", TextType.TEXT)
		html_node = text_node_to_html_node(node)
		self.assertIsNone(html_node.tag)
		self.assertEqual(html_node.value, "This is a text node")
		self.assertIsNone(html_node.props)

	def test_bold(self):
		node = TextNode("bold", TextType.BOLD)
		html_node = text_node_to_html_node(node)
		self.assertEqual(html_node.tag, "b")
		self.assertEqual(html_node.value, "bold")

	def test_italic(self):
		node = TextNode("italics", TextType.ITALIC)
		html_node = text_node_to_html_node(node)
		self.assertEqual(html_node.tag, "i")
		self.assertEqual(html_node.value, "italics")

	def test_code(self):
		node = TextNode("print(1)", TextType.CODE)
		html_node = text_node_to_html_node(node)
		self.assertEqual(html_node.tag, "code")
		self.assertEqual(html_node.value, "print(1)")

	def test_link(self):
		node = TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev")
		html_node = text_node_to_html_node(node)
		self.assertEqual(html_node.tag, "a")
		self.assertEqual(html_node.value, "Boot.dev")
		self.assertEqual(html_node.props, {"href": "https://www.boot.dev"})

	def test_image(self):
		node = TextNode("Alt text", TextType.IMAGE, "https://example.com/img.png")
		html_node = text_node_to_html_node(node)
		self.assertEqual(html_node.tag, "img")
		self.assertEqual(html_node.value, "")
		self.assertEqual(html_node.props, {"src": "https://example.com/img.png", "alt": "Alt text"})

	def test_invalid_type_raises(self):
		class FakeType: pass
		node = TextNode("x", FakeType())
		with self.assertRaises(ValueError):
			text_node_to_html_node(node)


if __name__ == "__main__":
	unittest.main()
