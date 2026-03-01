with st_list(list_type=lt.unordered, li_style=bs.list_item, align="center") as l:
    with l.item(): st_write("First unordered item")
    with l.item(): st_write("Second unordered item")
    with l.item(): st_write("Third unordered item")
