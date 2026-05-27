import unittest

from textnode import (
    TextNode,
    TextType,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)


class TestTextNode(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(
            str(TextNode("Some code", TextType.CODE)), "TextNode(Some code, code, None)"
        )

    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_url(self):
        self.assertEqual(TextNode("This is a text node", TextType.LINK).url, None)
        self.assertEqual(
            TextNode("This is a link", TextType.LINK, "https://example.com").url,
            "https://example.com",
        )
        self.assertNotEqual(
            TextNode("Text", TextType.LINK), TextNode("Text", TextType.IMAGE)
        )


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_no_delimiters_found(self):
        self.assertEqual(
            split_nodes_delimiter(
                [TextNode("This is just some plain text", TextType.TEXT)],
                "**",
                TextType.BOLD,
            ),
            [TextNode("This is just some plain text", TextType.TEXT)],
        )

    def test_delimiters_at_the_start(self):
        self.assertEqual(
            split_nodes_delimiter(
                [
                    TextNode(
                        "**This is bold right from the start** and it has some text afterwards",
                        TextType.TEXT,
                    )
                ],
                "**",
                TextType.BOLD,
            ),
            [
                TextNode("This is bold right from the start", TextType.BOLD),
                TextNode(" and it has some text afterwards", TextType.TEXT),
            ],
        )

    def test_delimiters_at_the_end(self):
        self.assertEqual(
            split_nodes_delimiter(
                [TextNode("This gets _italic at the very end_", TextType.TEXT)],
                "_",
                TextType.ITALIC,
            ),
            [
                TextNode("This gets ", TextType.TEXT),
                TextNode("italic at the very end", TextType.ITALIC),
            ],
        )

    def test_delimiters_covering_the_whole_node(self):
        self.assertEqual(
            split_nodes_delimiter(
                [TextNode("`This is the code in it's entirety`", TextType.TEXT)],
                "`",
                TextType.CODE,
            ),
            [TextNode("This is the code in it's entirety", TextType.CODE)],
        )

    def test_delimiters_in_the_middle(self):
        self.assertEqual(
            split_nodes_delimiter(
                [TextNode("This is text with a `code block` word", TextType.TEXT)],
                "`",
                TextType.CODE,
            ),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_multiple_delimiter_nodes(self):
        self.assertEqual(
            split_nodes_delimiter(
                [
                    TextNode(
                        "This is text with a **bold** word and then **one** more",
                        TextType.TEXT,
                    )
                ],
                "**",
                TextType.BOLD,
            ),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" word and then ", TextType.TEXT),
                TextNode("one", TextType.BOLD),
                TextNode(" more", TextType.TEXT),
            ],
        )


class TestExtractMarkdownImages(unittest.TestCase):
    def test_no_images(self):
        self.assertEqual(
            extract_markdown_images("This is just some plain text"),
            [],
        )

    def test_rick_roll(self):
        self.assertEqual(
            extract_markdown_images(
                "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
            ),
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
        )


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_no_links(self):
        self.assertEqual(
            extract_markdown_links("This is just some plain text"),
            [],
        )

    def test_boot_dev_links(self):
        self.assertEqual(
            extract_markdown_links(
                "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
            ),
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
        )


class TestSplitImages(unittest.TestCase):
    def test_split_images_with_no_images(self):
        self.assertListEqual(
            split_nodes_image(
                [TextNode("This is some text without images", TextType.TEXT)]
            ),
            [TextNode("This is some text without images", TextType.TEXT)],
        )

    def test_split_images_with_an_image_at_the_start(self):
        self.assertListEqual(
            split_nodes_image(
                [
                    TextNode(
                        "![image](https://i.imgur.com/zjjcJKZ.png) this is",
                        TextType.TEXT,
                    )
                ]
            ),
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" this is", TextType.TEXT),
            ],
        )

    def test_split_images_with_two_images(self):
        self.assertListEqual(
            split_nodes_image(
                [
                    TextNode(
                        "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
                        TextType.TEXT,
                    )
                ]
            ),
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
        )

    def test_split_images_with_text_after_an_image(self):
        self.assertListEqual(
            split_nodes_image(
                [
                    TextNode(
                        "This is a text with just one ![image](https://i.imgur.com/zjjcJKZ.png) and some text after it",
                        TextType.TEXT,
                    )
                ]
            ),
            [
                TextNode("This is a text with just one ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and some text after it", TextType.TEXT),
            ],
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_link_with_no_links(self):
        self.assertListEqual(
            split_nodes_link(
                [TextNode("This is some text without links", TextType.TEXT)]
            ),
            [TextNode("This is some text without links", TextType.TEXT)],
        )

    def test_split_links_with_a_link_at_the_start(self):
        self.assertListEqual(
            split_nodes_link(
                [TextNode("[link](https://example.com) this is", TextType.TEXT)]
            ),
            [
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" this is", TextType.TEXT),
            ],
        )

    def test_split_links_with_a_link_at_the_end(self):
        self.assertListEqual(
            split_nodes_link(
                [
                    TextNode(
                        "This is text with a [link](https://example.com)", TextType.TEXT
                    )
                ]
            ),
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
        )

    def test_split_links_with_text_after_a_link(self):
        self.assertListEqual(
            split_nodes_link(
                [
                    TextNode(
                        "This is a text with a [link](https://example.com) and some text after it",
                        TextType.TEXT,
                    )
                ]
            ),
            [
                TextNode("This is a text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and some text after it", TextType.TEXT),
            ],
        )

    def test_split_nodes_link_does_not_confuse_an_image_with_a_link(self):
        self.assertListEqual(
            split_nodes_link(
                [
                    TextNode(
                        "This is a text with an ![image](https://i.imgur.com/zjjcJKZ.png), it's not a link",
                        TextType.TEXT,
                    )
                ]
            ),
            [
                TextNode(
                    "This is a text with an ![image](https://i.imgur.com/zjjcJKZ.png), it's not a link",
                    TextType.TEXT,
                ),
            ],
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(
            text_to_textnodes(
                "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
            ),
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
