import os
import re
import shutil
from enum import Enum

from htmlnode import HTMLNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType, text_to_textnodes


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown: str):
    result: list[str] = []
    for part in markdown.split("\n\n"):
        block = part.strip()

        if block:
            result.append(block)

    return result


def block_to_block_type(block: str):
    if re.match(r"[#]{1,6} ", block):
        return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    if all(line.startswith(">") for line in block.splitlines()):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in block.splitlines()):
        return BlockType.UNORDERED_LIST

    is_an_ordered_list = True
    last_item_number = 0
    for line in block.splitlines():
        match = re.match(r"(\d+)\. ", line)

        if not match:
            is_an_ordered_list = False
            break

        item_number = int(match[1])
        if item_number != last_item_number + 1:
            is_an_ordered_list = False
            break

        last_item_number = item_number

    if is_an_ordered_list:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def extract_title(markdown: str):
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:]

    raise ValueError("Could not find an h1 in input markdown")


def text_to_children(text: str) -> list[HTMLNode]:
    return [text_node_to_html_node(text_node) for text_node in text_to_textnodes(text)]


def markdown_to_html_node(markdown: str):
    children: list[HTMLNode] = []
    for block in markdown_to_blocks(markdown):
        match block_to_block_type(block):
            case BlockType.HEADING:
                match = re.match(r"^([#]+) (.*)$", block)
                assert match
                level = len(match.group(1))
                text = match.group(2)
                children.append(ParentNode(f"h{level}", text_to_children(text)))
            case BlockType.CODE:
                match = re.match(r"^```\n([\s\S]*?)```$", block)
                assert match

                children.append(
                    ParentNode(
                        "pre",
                        [
                            text_node_to_html_node(
                                TextNode(match.group(1), TextType.CODE)
                            )
                        ],
                    )
                )
            case BlockType.QUOTE:
                children.append(
                    ParentNode(
                        "blockquote",
                        text_to_children(
                            " ".join(
                                line.strip() for line in re.findall(r"> (.*)", block)
                            )
                        ),
                    )
                )
            case BlockType.UNORDERED_LIST:
                children.append(
                    ParentNode(
                        "ul",
                        [
                            ParentNode("li", text_to_children(line.strip()))
                            for line in re.findall(r"- (.*)", block)
                        ],
                    )
                )
            case BlockType.ORDERED_LIST:
                children.append(
                    ParentNode(
                        "ol",
                        [
                            ParentNode("li", text_to_children(line.strip()))
                            for line in re.findall(r"\d+\. (.*)", block)
                        ],
                    )
                )
            case BlockType.PARAGRAPH:
                children.append(
                    ParentNode(
                        "p",
                        text_to_children(
                            " ".join(line.strip() for line in block.splitlines())
                        ),
                    )
                )

    return ParentNode("div", children)


def copy_static_files(src: str, dst: str):
    def copy_files_rec(src: str, dst: str):
        os.mkdir(dst)

        for filepath in os.listdir(src):
            src_path = os.path.join(src, filepath)
            dst_path = os.path.join(dst, filepath)

            if os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
            elif os.path.isdir(src_path):
                copy_files_rec(src_path, dst_path)
            else:
                raise RuntimeError(f"Unsupported file type at {src_path}")

    if os.path.exists(dst):
        shutil.rmtree(dst)

    copy_files_rec(src, dst)


def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path) as markdown_file:
        markdown = markdown_file.read()

    with open(template_path) as template_file:
        template = template_file.read()

    title = extract_title(markdown)
    content = markdown_to_html_node(markdown).to_html()

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w") as dest_file:
        dest_file.write(
            template.replace("{{ Title }}", title)
            .replace("{{ Content }}", content)
            .replace('href="/', f'href="{basepath}')
            .replace('src="/', f'src="{basepath}')
        )


def generate_pages_recursive(src: str, dst: str, basepath: str):
    if not os.path.exists(dst):
        os.mkdir(dst)

    for filepath in os.listdir(src):
        src_path = os.path.join(src, filepath)
        dst_path = os.path.join(dst, filepath).replace(".md", ".html")

        if os.path.isfile(src_path):
            generate_page(src_path, "template.html", dst_path, basepath)
        elif os.path.isdir(src_path):
            generate_pages_recursive(src_path, dst_path, basepath)
        else:
            raise RuntimeError(f"Unsupported file type at {src_path}")
