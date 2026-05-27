import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType


class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(HTMLNode("p"), HTMLNode("p"))
        self.assertEqual(HTMLNode("b"), HTMLNode("b"))
        self.assertEqual(
            HTMLNode("b", "foo", [HTMLNode("i", "bar")], {"class": "flex"}),
            HTMLNode("b", "foo", [HTMLNode("i", "bar")], {"class": "flex"}),
        )
        self.assertNotEqual(HTMLNode("b"), HTMLNode("i"))
        self.assertNotEqual(
            HTMLNode("b", "foo", [HTMLNode("i", "bar")], {"class": "flex"}),
            HTMLNode("b", "foo", [HTMLNode("i", "bar")], {"class": "inline-flex"}),
        )

    def test_repr(self):
        self.assertEqual(str(HTMLNode()), "HTMLNode(None, None, None, None)")
        self.assertEqual(str(HTMLNode("p")), "HTMLNode(p, None, None, None)")
        self.assertEqual(
            str(HTMLNode("p", "Hello, world!")),
            "HTMLNode(p, Hello, world!, None, None)",
        )
        self.assertEqual(
            str(
                HTMLNode(
                    "p",
                    None,
                    [
                        HTMLNode(None, "foo"),
                        HTMLNode("a", "bar", None, {"href": "https://example.com"}),
                    ],
                )
            ),
            "HTMLNode(p, None, [HTMLNode(None, foo, None, None), HTMLNode(a, bar, None, {'href': 'https://example.com'})], None)",
        )

    def test_props_to_html(self):
        self.assertEqual(HTMLNode("p").props_to_html(), "")
        self.assertEqual(
            HTMLNode(
                "p",
                None,
                None,
                {
                    "href": "https://example.com",
                },
            ).props_to_html(),
            ' href="https://example.com"',
        )
        self.assertEqual(
            HTMLNode(
                "p",
                None,
                None,
                {
                    "href": "https://example.com",
                    "target": "_blank",
                },
            ).props_to_html(),
            ' href="https://example.com" target="_blank"',
        )


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Hello, world!")
        self.assertEqual(node.to_html(), "Hello, world!")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")


class TestParentNode(unittest.TestCase):
    def test_parent_repr(self):
        self.assertEqual(
            str(ParentNode("p", [LeafNode(None, "Text")], {"foo": "bar"})),
            "ParentNode(p, [LeafNode(None, Text, None)], {'foo': 'bar'})",
        )

    def test_parent_to_html_no_children(self):
        self.assertEqual(ParentNode("p", []).to_html(), "<p></p>")

    def test_parent_to_html_with_children(self):
        self.assertEqual(
            ParentNode(
                "p",
                [
                    LeafNode("b", "Bold text", {"id": "bold"}),
                    LeafNode(None, "Normal text"),
                    LeafNode("i", "italic text", {"class": "foo"}),
                    LeafNode(None, "Normal text"),
                ],
            ).to_html(),
            '<p><b id="bold">Bold text</b>Normal text<i class="foo">italic text</i>Normal text</p>',
        )

    def test_parent_to_html_with_grandchildren(self):
        self.assertEqual(
            ParentNode(
                "p",
                [
                    ParentNode(
                        "b",
                        [LeafNode("i", "Bold text", {"id": "italic"})],
                        {"id": "bold"},
                    ),
                    LeafNode(None, "Normal text"),
                    LeafNode("i", "italic text", {"class": "foo"}),
                    LeafNode(None, "Normal text"),
                ],
            ).to_html(),
            '<p><b id="bold"><i id="italic">Bold text</i></b>Normal text<i class="foo">italic text</i>Normal text</p>',
        )


class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        self.assertEqual(
            text_node_to_html_node(TextNode("Plain text", TextType.TEXT)),
            LeafNode(None, "Plain text"),
        )

    def test_bold(self):
        self.assertEqual(
            text_node_to_html_node(TextNode("This is a some bold text", TextType.BOLD)),
            LeafNode("b", "This is a some bold text"),
        )

    def test_italic(self):
        self.assertEqual(
            text_node_to_html_node(
                TextNode("This is a some italic text", TextType.ITALIC)
            ),
            LeafNode("i", "This is a some italic text"),
        )

    def test_code(self):
        self.assertEqual(
            text_node_to_html_node(TextNode("Here is some code", TextType.CODE)),
            LeafNode("code", "Here is some code"),
        )

    def test_link(self):
        self.assertEqual(
            text_node_to_html_node(
                TextNode("An example website", TextType.LINK, "https://example.com")
            ),
            LeafNode("a", "An example website", {"href": "https://example.com"}),
        )

    def test_image(self):
        self.assertEqual(
            text_node_to_html_node(
                TextNode(
                    "An image that wouldn't render",
                    TextType.IMAGE,
                    "https://example.com",
                )
            ),
            LeafNode(
                "img",
                "",
                {"alt": "An image that wouldn't render", "src": "https://example.com"},
            ),
        )


if __name__ == "__main__":
    unittest.main()
