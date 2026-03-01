with st_list(list_type=lt.unordered,
             l_style=s.container.lists.g_docs,
             li_style=bs.list_item,
             align="center") as l:
    with l.item():
        st_write("Level 1 symbol")
        with st_list(list_type=lt.unordered,
                     l_style=s.container.lists.g_docs,
                     li_style=bs.list_item) as l2:
            with l2.item():
                st_write("Level 2 symbol")
                with st_list(list_type=lt.unordered,
                             l_style=s.container.lists.g_docs,
                             li_style=bs.list_item) as l3:
                    with l3.item(): st_write("Level 3 symbol")
    with l.item(): st_write("Another level 1")
