import re
from enum import Enum


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str | None = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other: object, /) -> bool:
        return (
            isinstance(other, TextNode)
            and self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def split_nodes_delimiter(
    old_nodes: list[TextNode],
    delimiter: str,
    text_type: TextType,
):
    result: list[TextNode] = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue

        start = old_node.text.find(delimiter)
        if start < 0:
            result.append(old_node)
            continue

        end = 0
        while start >= 0:
            if start > end:
                result.append(TextNode(old_node.text[end:start], TextType.TEXT))

            start += len(delimiter)
            end = old_node.text.find(delimiter, start)
            if end < 0:
                raise ValueError(
                    f"Invalid syntax: expected a closing {delimiter} in in {old_node.text}"
                )

            result.append(TextNode(old_node.text[start:end], text_type))
            end += len(delimiter)
            start = old_node.text.find(delimiter, end)

        if end < len(old_node.text) - 1:
            result.append(TextNode(old_node.text[end:], TextType.TEXT))

    return result


def extract_markdown_images(text: str):
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text: str):
    return re.findall(r"\[(.*?)\]\((.*?)\)", text)


def split_nodes_image(old_nodes: list[TextNode]):
    result: list[TextNode] = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue

        matched_anything = False
        last_match_end = 0
        for match in re.finditer(r"!\[(.*?)\]\((.*?)\)", old_node.text):
            matched_anything = True
            start = match.start(0)
            end = match.end(0)

            if start > last_match_end:
                result.append(
                    TextNode(old_node.text[last_match_end:start], TextType.TEXT)
                )

            last_match_end = end

            alt = old_node.text[match.start(1) : match.end(1)]
            src = old_node.text[match.start(2) : match.end(2)]
            result.append(TextNode(alt, TextType.IMAGE, src))

        if matched_anything:
            if last_match_end < len(old_node.text) - 1:
                result.append(TextNode(old_node.text[last_match_end:], TextType.TEXT))
        else:
            result.append(old_node)

    return result


def split_nodes_link(old_nodes: list[TextNode]):
    result: list[TextNode] = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue

        matched_anything = False
        last_match_end = 0
        for match in re.finditer(r"(?<!\!)\[(.*?)\]\((.*?)\)", old_node.text):
            matched_anything = True
            start = match.start(0)
            end = match.end(0)

            if start > last_match_end:
                result.append(
                    TextNode(old_node.text[last_match_end:start], TextType.TEXT)
                )

            last_match_end = end

            text = old_node.text[match.start(1) : match.end(1)]
            href = old_node.text[match.start(2) : match.end(2)]
            result.append(TextNode(text, TextType.LINK, href))

        if matched_anything:
            if last_match_end < len(old_node.text) - 1:
                result.append(TextNode(old_node.text[last_match_end:], TextType.TEXT))
        else:
            result.append(old_node)

    return result


def text_to_textnodes(text: str):
    result = [TextNode(text, TextType.TEXT)]
    result = split_nodes_delimiter(result, "**", TextType.BOLD)
    result = split_nodes_delimiter(result, "_", TextType.ITALIC)
    result = split_nodes_delimiter(result, "`", TextType.CODE)
    result = split_nodes_image(result)
    result = split_nodes_link(result)
    return result
