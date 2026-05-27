import unittest

from utils import (
    BlockType,
    block_to_block_type,
    extract_title,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_basic(self):
        self.assertListEqual(
            markdown_to_blocks(
                """
# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item
"""
            ),
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                """- This is the first list item in a list block
- This is a list item
- This is another list item""",
            ],
        )

    def test_markdown_to_blocks(self):
        self.assertEqual(
            markdown_to_blocks("""
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""),
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_headings(self):
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("#### Heading 4"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("##### Heading 5"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)

        self.assertNotEqual(
            block_to_block_type("####### Not a heading"), BlockType.HEADING
        )

        self.assertNotEqual(block_to_block_type("#No space"), BlockType.HEADING)
        self.assertNotEqual(block_to_block_type("Paragraph"), BlockType.HEADING)

    def test_code(self):
        self.assertEqual(block_to_block_type("```\nsome code here```"), BlockType.CODE)

        self.assertNotEqual(
            block_to_block_type("```\nendless not code"), BlockType.CODE
        )

        self.assertNotEqual(
            block_to_block_type("```no newline at the start```"), BlockType.CODE
        )

    def test_quote(self):
        self.assertEqual(block_to_block_type("> something smart"), BlockType.QUOTE)

        self.assertEqual(
            block_to_block_type("> and\n> even\n> smarter"), BlockType.QUOTE
        )

        self.assertNotEqual(block_to_block_type(">not\nso\n>smart"), BlockType.QUOTE)

    def test_unordered_list(self):
        self.assertEqual(block_to_block_type("- item"), BlockType.UNORDERED_LIST)

        self.assertEqual(
            block_to_block_type("- two\n- items"), BlockType.UNORDERED_LIST
        )

        self.assertEqual(
            block_to_block_type("- even\n- three\n- items"), BlockType.UNORDERED_LIST
        )

        self.assertNotEqual(
            block_to_block_type("-not\n-really\n-a\n-list"), BlockType.UNORDERED_LIST
        )

    def test_ordered_list(self):
        self.assertEqual(
            block_to_block_type("1. an\n2. ordered\n3. list"), BlockType.ORDERED_LIST
        )

        self.assertNotEqual(
            block_to_block_type("1. not\n3. that\n5. ordered"), BlockType.ORDERED_LIST
        )

    def test_paragraph(self):
        self.assertEqual(
            block_to_block_type("This is just a paragraph"), BlockType.PARAGRAPH
        )

        self.assertEqual(block_to_block_type("Another paragraph"), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_headings(self):
        md = """
# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3</h3><h4>Heading 4</h4><h5>Heading 5</h5><h6>Heading 6</h6></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_quotes(self):
        md = """
> Someone **has**
> said _something_ smart
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>Someone <b>has</b> said <i>something</i> smart</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- **First** item
- second _item_
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li><b>First</b> item</li><li>second <i>item</i></li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. **First** item
2. second _item_
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li><b>First</b> item</li><li>second <i>item</i></li></ol></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )


class TestExtractTitle(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(extract_title("# This is a heading"), "This is a heading")

        self.assertEqual(
            extract_title("some paragraph first\nand then\n\n# A heading"), "A heading"
        )

    def test_no_h1(self):
        self.assertRaises(ValueError, lambda: extract_title("This is a heading"))


if __name__ == "__main__":
    unittest.main()
