with st_list(list_type=lt.unordered, li_style=bs.list_item, align="center") as l:
    with l.item():
        st_write("Parent item A")
        with st_list(list_type=lt.unordered,
                     li_style=bs.list_item) as l2:
            with l2.item(): st_write("Child A.1")
            with l2.item():
                st_write("Child A.2")
                with st_list(list_type=lt.unordered,
                             li_style=bs.list_item) as l3:
                    with l3.item(): st_write("Grandchild A.2.a")
                    with l3.item(): st_write("Grandchild A.2.b")
    with l.item(): st_write("Parent item B")
