with st_block(bs.cell + ns("max-width: 300px;")):
    st_write(s.text.wrap.nowrap + s.large,
             "This text has nowrap and will not break even if it overflows")
