with st_list(list_type=lt.ordered,
             l_style=s.container.lists.ordered_lowercase,
             li_style=bs.list_item) as l:
    with l.item(): st_write("Item a")
    with l.item(): st_write("Item b")
