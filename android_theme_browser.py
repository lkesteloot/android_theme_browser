
import sys
import argparse
import os.path
import re
import xml.etree.ElementTree
import glob

VALUES_RE = re.compile(r"values-v(\d+)")

class ValuesDir(object):
    def __init__(self, pathname):
        self.pathname = pathname

        filename = os.path.basename(pathname)

        if filename == "values":
            self.api = 0
        else:
            match = VALUES_RE.match(filename)
            if match:
                self.api = int(match.group(1))
            else:
                # Other "v" qualifier, such as "vi".
                self.api = None

class Item(object):
    def __init__(self, item, namespace):
        self.name = item.attrib["name"]
        self.value = item.text

        if ":" not in self.name:
            self.name = namespace + self.name

class Theme(object):
    def __init__(self, style, pathname, namespace):
        self.pathname = pathname
        self.name = namespace + style.attrib["name"]

        # Resolve parent name.
        self.parent_name = style.attrib.get("parent")
        if self.parent_name == "":
            # Explicit no parent.
            self.parent_name = None
        elif self.parent_name is None:
            # Implicit parent.
            parts = self.name.split(".")
            if len(parts) == 1:
                # Not a warning, this is fine.
                ## sys.stderr.write("Warning: Can't infer parent of %s\n" % self.name)
                self.parent_name = None
            else:
                self.parent_name = ".".join(parts[:-1])

        # Strip unnecessary prefix.
        if self.parent_name is not None and self.parent_name.startswith("@style/"):
            self.parent_name = self.parent_name[7:]

        # Add implicit namespace.
        if self.parent_name is not None and ":" not in self.parent_name:
            self.parent_name = namespace + self.parent_name

        items = [Item(item, namespace) for item in style if item.tag == "item"]
        self.item_map = dict((item.name, item) for item in items)

    def resolve_parenting(self, name_to_theme):
        if self.parent_name is None:
            self.parent = None
        else:
            self.parent = name_to_theme.get(self.parent_name)
            if self.parent is None:
                sys.stderr.write("Error: Can't find parent %s of %s (%s)\n" % (self.parent_name, self.name, self.pathname))
                sys.exit(1)

    def dump(self, out, name_to_theme, attr):
        out.write("%s (%s):\n" % (self.name, self.pathname))

        # Show theme ancestry.
        theme = self.parent
        while theme is not None:
            out.write("    %s (%s)\n" % (theme.name, theme.pathname))
            theme = theme.parent

        out.write("\n")

        # Union of all items.
        theme = self
        item_names = set()
        while theme is not None:
            item_names = item_names.union(set(theme.item_map.keys()))
            theme = theme.parent

        # List them all in alphabetical order.
        for item_name in sorted(item_names):
            if attr is None or attr == item_name:
                out.write("    %s\n" % item_name)

                # Walk up the tree.
                theme = self
                while theme is not None:
                    item = theme.item_map.get(item_name)
                    if item is not None:
                        out.write("        %s (%s, %s)\n" % (item.value, theme.name, theme.pathname))
                    theme = theme.parent

        out.write("\n")

def load_file(pathname, namespace):
    resources = xml.etree.ElementTree.parse(pathname).getroot()
    if resources.tag != "resources":
        sys.stderr.write("Error: File %s is not a resource\n" % pathname)
        sys.exit(1)

    return [Theme(style, pathname, namespace) for style in resources if style.tag == "style"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('res_dirs', metavar="DIR", nargs="+", help="res directories")
    parser.add_argument('--theme', metavar="THEME", help="theme to dump (default: all)")
    parser.add_argument('--attr', metavar="ATTR", help="attribute to dump (default: all)")
    parser.add_argument('--api', type=int, metavar="API", help="API level (default: most recent)")
    args = parser.parse_args()

    # Load the themes into a map by name.
    name_to_theme = {}
    for res_dir in args.res_dirs:
        namespace = "android:" if "/sdk/" in res_dir else ""

        # Find the most recent value dir that is <= API. Note that our glob
        # here is sloppy because the directories might combine multiple
        # qualifiers.
        values_dirs = [ValuesDir(pathname) for pathname in glob.glob(os.path.join(res_dir, "values-v*"))]

        # Insert default directory.
        values_dirs.insert(0, ValuesDir(os.path.join(res_dir, "values")))

        # Filter valid dirs.
        values_dirs = [values_dir for values_dir in values_dirs if values_dir.api is not None]

        # Filter by our API version.
        if args.api is not None:
            values_dirs = [values_dir for values_dir in values_dirs if values_dir.api <= args.api]

        # Sort by API version.
        values_dirs.sort(key=lambda values_dir: values_dir.api)

        for values_dir in values_dirs:
            pathnames = glob.glob(os.path.join(values_dir.pathname, "themes*.xml"))

            for pathname in pathnames:
                sys.stderr.write("Info: Loading file %s\n" % pathname)
                themes = load_file(pathname, namespace)
                for theme in themes:
                    name_to_theme[theme.name] = theme

    sys.stdout.write("\n")

    # Resolve parenting.
    for theme in name_to_theme.values():
        theme.resolve_parenting(name_to_theme)

    # Dump all the themes.
    if args.theme is None:
        for theme in name_to_theme.values():
            theme.dump(sys.stdout, name_to_theme, args.attr)
    else:
        theme = name_to_theme.get(args.theme)
        if theme is None:
            sys.stderr.write("Theme not found: %s" % args.theme)
            sys.exit(1)

        theme.dump(sys.stdout, name_to_theme, args.attr)

main()
