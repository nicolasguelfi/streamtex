with st_list(list_type=lt.ordered,
             li_style=bs.list_item) as l:
    with l.item(): st_write("Step one")
    with l.item(): st_write("Step two")
    with l.item(): st_write("Step three")
