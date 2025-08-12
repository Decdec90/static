from textnode import TextNode, TextType
from pathlib import Path
from markdown_blocks import markdown_to_html_node, extract_title
import shutil

def main():
	node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
	print(node)


def empty_dir(dst: Path):
	# remove everything inside dst (but keep the folder itself)
	if not dst.exists():
		dst.mkdir(parents=True, exist_ok=True)
		return
	for child in dst.iterdir():
		if child.is_dir():
			shutil.rmtree(child)
		else:
			child.unlink()

def copy_dir(src: Path, dst: Path):
	# recursively copy src -> dst
	for item in src.iterdir():
		target = dst / item.name
		if item.is_dir():
			target.mkdir(exist_ok=True)
			copy_dir(item, target)
		else:
			shutil.copy2(item, target)
			print(f"copied: {item} -> {target}")

def copy_static_to_public(src_dir="static", dst_dir="public"):
	src = Path(src_dir)
	dst = Path(dst_dir)

	if not src.exists() or not src.is_dir():
		raise FileNotFoundError(f"source directory not found: {src}")

	dst.mkdir(parents=True, exist_ok=True)
	empty_dir(dst)
	copy_dir(src, dst)

def generate_page(from_path, template_path, dest_path):
	print(f"Generating page from {from_path} to {dest_path} using {template_path}")

	md_text = Path(from_path).read_text(encoding="utf-8")
	template = Path(template_path).read_text(encoding="utf-8")

	html_root = markdown_to_html_node(md_text)
	content_html = html_root.to_html()
	title = extract_title(md_text)

	full_html = template.replace("{{ Title }}", title).replace("{{ Content }}", content_html)

	dest = Path(dest_path)
	dest.parent.mkdir(parents=True, exist_ok=True)
	dest.write_text(full_html, encoding="utf-8")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
	"""
	Crawl dir_path_content recursively.
	For each .md file, render using template_path and write an .html file
	into dest_dir_path, preserving the relative folder structure.
	"""
	root = Path(dir_path_content)
	dest_root = Path(dest_dir_path)

	for md_file in root.rglob("*.md"):
		# Compute destination path while preserving structure
		rel = md_file.relative_to(root)               # e.g. blog/post.md
		html_rel = rel.with_suffix(".html")           # -> blog/post.html
		dest_path = dest_root / html_rel              # public/blog/post.html

		# Reuse your single-file generator (it mkdirs parents)
		generate_page(md_file, template_path, dest_path)


def main():
	#1. Delete anything in the public directory
	public_dir = Path("public")
	empty_dir(public_dir)

	#2. copy all static files from static to public
	copy_static_to_public()

	#3. Generate a page from content/index.md using template.html and write to public/index.html
	generate_pages_recursive(
		"content",
		"template.html",
		"public"
	)

if __name__ == "__main__":
	main()
