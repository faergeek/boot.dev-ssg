import sys

from utils import copy_static_files, generate_pages_recursive


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    copy_static_files("static", "docs")
    generate_pages_recursive("content", "docs", basepath)


if __name__ == "__main__":
    main()
