class Tag:

    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return self.tag

class Tags:
    ### Enums #####
    div = Tag("div")
    span = Tag("span")

    # Content sectioning
    header = Tag("header")
    section = Tag("section")
    footer = Tag("footer")
    h1 = Tag("h1")
    h2 = Tag("h2")
    h3 = Tag("h3")
    h4 = Tag("h4")
    h5 = Tag("h5")
    h6 = Tag("h6")

    # Text content
    p = Tag("p")
    blockquote = Tag("blockquote")
    cite = Tag("cite")
    code = Tag("code")
    figcaption = Tag("figcaption")
    figure = Tag("figure")
    math = Tag("math")

########################################################################

class ListType:

    def __init__(self, order):
        self.order = order

    def __repr__(self):
        return self.order


class ListTypes:
    ordered = ListType("ol")
    unordered = ListType("ul")
