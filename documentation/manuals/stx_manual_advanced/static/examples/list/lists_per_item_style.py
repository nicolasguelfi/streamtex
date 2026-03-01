with st_list(list_type=lt.unordered, li_style=bs.list_item) as l:
    with l.item(): st_write("Normal item")
    with l.item(style=s.text.colors.coral):
        st_write("Highlighted item (coral override)")
    with l.item(): st_write("Normal item")
