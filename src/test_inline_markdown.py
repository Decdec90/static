import unittest
from inline_markdown import extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes
from textnode import TextNode, TextType

class TestMarkdownExtract(unittest.TestCase):

	def test_images_basic(self):
		text = "Hi ![alt1](http://a.png) and ![alt2](http://b.jpg)"
		self.assertEqual(
			extract_markdown_images(text),
			[("alt1", "http://a.png"), ("alt2", "http://b.jpg")]
		)

	def test_images_none(self):
		text = "No images here."
		self.assertEqual(extract_markdown_images(text), [])

	def test_links_basic(self):
		text = "See [Boot.dev](https://www.boot.dev) and [YouTube](https://youtube.com)"
		self.assertEqual(
			extract_markdown_links(text),
			[("Boot.dev", "https://www.boot.dev"), ("YouTube", "https://youtube.com")]
		)

	def test_links_ignore_images(self):
		text = "![img](http://x.png) and also [site](http://s.com)"
		self.assertEqual(
			extract_markdown_links(text),
			[("site", "http://s.com")]
		)

	def test_split_nodes_image_basic(self):
		nodes = [TextNode("Start ![alt](http://img.png) end", TextType.TEXT)]
		out = split_nodes_image(nodes)
		self.assertEqual(
			[(n.text, n.text_type, n.url) for n in out],
			[("Start ", TextType.TEXT, None), ("alt", TextType.IMAGE, "http://img.png"), (" end", TextType.TEXT, None)]
		)

	def test_split_nodes_image_multiple(self):
		nodes = [TextNode("x ![a](u1) y ![b](u2) z", TextType.TEXT)]
		out = split_nodes_image(nodes)
		self.assertEqual(
			[(n.text, n.text_type, n.url) for n in out],
			[("x ", TextType.TEXT, None), ("a", TextType.IMAGE, "u1"),
			 (" y ", TextType.TEXT, None), ("b", TextType.IMAGE, "u2"),
			 (" z", TextType.TEXT, None)]
		)

	def test_split_nodes_image_non_text_passthrough(self):
		link_node = TextNode("Boot.dev", TextType.LINK, "https://www.boot.dev")
		out = split_nodes_image([link_node])
		self.assertIs(out[0], link_node)

	def test_split_nodes_image_no_match(self):
		nodes = [TextNode("no images here", TextType.TEXT)]
		out = split_nodes_image(nodes)
		self.assertEqual(len(out), 1)
		self.assertEqual(out[0].text, "no images here")
		self.assertEqual(out[0].text_type, TextType.TEXT)
		self.assertIsNone(out[0].url)

	def test_split_nodes_link_basic(self):
		nodes = [TextNode("Go to [site](http://s.com) now", TextType.TEXT)]
		out = split_nodes_link(nodes)
		self.assertEqual(
			[(n.text, n.text_type, n.url) for n in out],
			[("Go to ", TextType.TEXT, None), ("site", TextType.LINK, "http://s.com"), (" now", TextType.TEXT, None)]
		)

	def test_split_nodes_link_multiple(self):
		nodes = [TextNode("[a](u1) and [b](u2)", TextType.TEXT)]
		out = split_nodes_link(nodes)
		self.assertEqual(
			[(n.text, n.text_type, n.url) for n in out],
			[("a", TextType.LINK, "u1"), (" and ", TextType.TEXT, None), ("b", TextType.LINK, "u2")]
		)

	def test_split_nodes_link_ignores_images(self):
		nodes = [TextNode("![img](http://x.png) and [site](http://s.com)", TextType.TEXT)]
		out = split_nodes_link(nodes)
		# link split should NOT consume the image; the image syntax remains in TEXT here
		self.assertEqual(
			[(n.text, n.text_type, n.url) for n in out],
			[("![img](http://x.png) and ", TextType.TEXT, None), ("site", TextType.LINK, "http://s.com")]
		)

	def test_split_nodes_link_non_text_passthrough(self):
		img_node = TextNode("alt", TextType.IMAGE, "http://x.png")
		out = split_nodes_link([img_node])
		self.assertIs(out[0], img_node)

	def test_split_nodes_link_no_match(self):
		nodes = [TextNode("no links here", TextType.TEXT)]
		out = split_nodes_link(nodes)
		self.assertEqual(len(out), 1)
		self.assertEqual(out[0].text, "no links here")
		self.assertEqual(out[0].text_type, TextType.TEXT)
		self.assertIsNone(out[0].url)

	def test_split_nodes_image_then_link_mixed(self):
		# First split images, then split links on the result list
		nodes = [TextNode("pic: ![a](u1) and link: [b](u2)", TextType.TEXT)]
		step1 = split_nodes_image(nodes)
		out = split_nodes_link(step1)
		self.assertEqual(
			[(n.text, n.text_type, n.url) for n in out],
			[("pic: ", TextType.TEXT, None),
			 ("a", TextType.IMAGE, "u1"),
			 (" and link: ", TextType.TEXT, None),
			 ("b", TextType.LINK, "u2")]
		)

	def test_text_to_textnodes_example(self):
		text = (
			"This is **text** with an _italic_ word and a `code block` "
			"and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
			"and a [link](https://boot.dev)"
		)
		out = text_to_textnodes(text)
		expected = [
			TextNode("This is ", TextType.TEXT),
			TextNode("text", TextType.BOLD),
			TextNode(" with an ", TextType.TEXT),
			TextNode("italic", TextType.ITALIC),
			TextNode(" word and a ", TextType.TEXT),
			TextNode("code block", TextType.CODE),
			TextNode(" and an ", TextType.TEXT),
			TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
			TextNode(" and a ", TextType.TEXT),
			TextNode("link", TextType.LINK, "https://boot.dev"),
		]
		self.assertEqual(out, expected)

	def test_text_to_textnodes_plain_text(self):
		text = "no markup here"
		out = text_to_textnodes(text)
		self.assertEqual(out, [TextNode("no markup here", TextType.TEXT)])

	def test_text_to_textnodes_only_link(self):
		text = "see [site](http://s.com)"
		out = text_to_textnodes(text)
		expected = [
			TextNode("see ", TextType.TEXT),
			TextNode("site", TextType.LINK, "http://s.com"),
		]
		self.assertEqual(out, expected)

	def test_text_to_textnodes_only_image(self):
		text = "pic: ![alt](http://img.png)"
		out = text_to_textnodes(text)
		expected = [
			TextNode("pic: ", TextType.TEXT),
			TextNode("alt", TextType.IMAGE, "http://img.png"),
		]
		self.assertEqual(out, expected)

	def test_text_to_textnodes_unmatched_backtick_raises(self):
		text = "bad `code"
		with self.assertRaises(ValueError):
			text_to_textnodes(text)




if __name__ == "__main__":
	unittest.main()
