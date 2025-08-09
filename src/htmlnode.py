

class HTMLNode:
	def __init__(self, tag=None, value=None, children=None, props=None):
		self.tag = tag
		self.value = value
		self.children = children
		self.props = props

	def to_html(self):
		raise NotImplementedError("Subclasses should implement this!")

	def props_to_html(self):
		if not self.props:
			return ""

		return "".join([f' {key}="{value}"' for key, value in self.props.items()])

	def __repr__(self):
		return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"


class LeafNode(HTMLNode):
	def __init__(self, tag, value, props=None):
		if value is None:
			raise ValueError("LeafNode must have a value")
		super().__init__(tag, value, None, props)

	def to_html(self):
		if self.value is None:
			raise ValueError("LeafNode must have a value")

		if self.tag is None:
			return self.value

		props_str = self.props_to_html()
		return f"<{self.tag}{props_str}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
	def __init__(self, tag, children, props=None):
		if not tag:
			raise ValueError("ParentNode must have a tag")
		if not children:
			raise ValueError("ParentNode must have children")
		super().__init__(tag, None, children, props)

	def to_html(self):
		if not self.tag:
			raise ValueError("ParentNode must have a tag")
		if not self.children:
			raise ValueError("ParentNode must have children")

		children_html = "".join([child.to_html() for child in self.children])
		props_str = self.props_to_html()
		return f"<{self.tag}{props_str}>{children_html}</{self.tag}>"
