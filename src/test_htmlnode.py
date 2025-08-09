import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):

	def test_props_to_html_multiple(self):
		node = HTMLNode(
			tag="a",
			value="Click here",
			props={"href": "https://www.google.com", "target": "_blank"}
		)
		expected = ' href="https://www.google.com" target="_blank"'
		self.assertEqual(node.props_to_html(), expected)

	def test_props_to_html_empty(self):
		node = HTMLNode(tag="p", value="Hello", props={})
		self.assertEqual(node.props_to_html(), "")

	def test_props_to_html_none(self):
		node = HTMLNode(tag="p", value="Hello")
		self.assertEqual(node.props_to_html(), "")

	def test_repr(self):
		node = HTMLNode(tag="p", value="Hello", props={"class": "text-bold"})
		repr_str = repr(node)
		self.assertIn("tag=p", repr_str)
		self.assertIn("value=Hello", repr_str)
		self.assertIn("{'class': 'text-bold'}", repr_str)


class TestLeafNode(unittest.TestCase):

	def test_leaf_to_html_p(self):
		node = LeafNode("p", "Hello, world!")
		self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

	def test_leaf_to_html_a_with_props(self):
		node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
		self.assertEqual(
			node.to_html(),
			'<a href="https://www.google.com">Click me!</a>'
		)

	def test_leaf_to_html_no_tag(self):
		node = LeafNode(None, "Just text")
		self.assertEqual(node.to_html(), "Just text")

	def test_leaf_no_value_raises(self):
		with self.assertRaises(ValueError):
			LeafNode("p", None)

	def test_leaf_to_html_no_value_raises(self):
		node = LeafNode("p", "test")
		node.value = None
		with self.assertRaises(ValueError):
			node.to_html()


class TestParentNode(unittest.TestCase):

	def test_parent_to_html_with_children(self):
		child_node = LeafNode("span", "child")
		parent_node = ParentNode("div", [child_node])
		self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

	def test_parent_to_html_with_grandchildren(self):
		grandchild_node = LeafNode("b", "grandchild")
		child_node = ParentNode("span", [grandchild_node])
		parent_node = ParentNode("div", [child_node])
		self.assertEqual(
			parent_node.to_html(),
			"<div><span><b>grandchild</b></span></div>"
		)

	def test_parent_with_multiple_children(self):
		child1 = LeafNode("span", "one")
		child2 = LeafNode("span", "two")
		parent_node = ParentNode("div", [child1, child2])
		self.assertEqual(
			parent_node.to_html(),
			"<div><span>one</span><span>two</span></div>"
		)

	def test_parent_with_props(self):
		child = LeafNode("span", "content")
		parent_node = ParentNode("div", [child], {"class": "container"})
		self.assertEqual(
			parent_node.to_html(),
			'<div class="container"><span>content</span></div>'
		)

	def test_parent_missing_tag_raises(self):
		child = LeafNode("span", "content")
		with self.assertRaises(ValueError):
			ParentNode(None, [child])

	def test_parent_missing_children_raises(self):
		with self.assertRaises(ValueError):
			ParentNode("div", None)

if __name__ == "__main__":
	unittest.main()

