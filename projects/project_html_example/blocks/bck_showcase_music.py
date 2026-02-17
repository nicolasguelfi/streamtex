import streamlit as st

# StreamTeX Block Imports
from streamtex import *
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

# Project Specific Imports
from custom.styles import Styles as s


# URLs used in this block
MUSENET_TRACK = (
    "https://soundcloud.com/openai_audio/sonatina"
    "?in=openai_audio/sets/musenet&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing"
)

MUSENET_RESEARCH = "https://openai.com/research/musenet"

JUKEBOX_FEATURE = "https://jukebox.openai.com/?song=794232841"
JUKEBOX_SAMPLE_LINKS = [
    "https://jukebox.openai.com/?song=787877257",
    "https://jukebox.openai.com/?song=802882084",
]

SUNO_FEATURE = "https://app.suno.ai/create/"
SUNO_SAMPLE_LINKS = [
    "https://suno.com/song/4da4b386-e76e-4465-b6fe-b151b2e6849f",
    "https://app.suno.ai/song/c56ab50e-0f62-4470-8603-814b83d9b6b0",
    "https://app.suno.ai/song/d91cb3a3-a40f-4cf4-9694-f0046ca3e978",
    "https://suno.com/song/ec329950-1a0c-45af-bd12-b46eb7de707f",
    "https://suno.com/song/b483407f-ec6e-4b6d-8626-be734cda0e0c",
]


class BlockStyles:
    """Local styling for the music showcase block."""
    
    # =======================================================
    # EXPLANATION OF HTML STYLE CONVERSION FOR CURSOR AGENT
    # =======================================================

    # Styles '.c3' and '.c6' are functionally the same. Furthermore, while 
    # they contain a lot of styles, all they're doing is adding a black solid border and 5pt padding.
    # Thus, they're grouped into one simple style.
    # Notice how we don't specify the color black for the border. 
    # Black is the default color, so there is no need specify it. 
    # Leaving it like this, also improves dark mode since the black will be 
    # turned into white, as intended. If we had specified the color black, 
    # this would have not happened, which is a problem. 
    # Often in html migrations, less is more.
    cell_border = s.container.borders.solid_border + s.container.paddings.small_padding
    
    # Styles '.c20', '.c8', '.c10' are functionally the same: 
    # at the end of the day, all they do is text-align: center.
    # We could define a special style for that, but since it is an atomic style,
    # we'll instead use 's.center_txt' whenever we should use either of those 3 styles.
    
    # Styles '.c1' ,'.c19', '.c11', '.c16', and '.c12' have a common issue across google docs exports: 
    # It is a style applied to empty <p> and <span> tags. While it is similar 
    # to the previous 3 '.c[n]' styles, since it computationally provides 
    # nothing, we don't even need to consider it. 
    
    # Style '.c18' provides a lot of visuals: the color #1155cc, font-weight: 700 (bold), text-decoration: none and font-size: 72pt. 
    # This is clearly a custom color, and since it may be used in other blocks 
    # within the project, we'll instead define it in `s.project.colors` with a 
    # readeable name like 'denim_blue'.
    # Then, we give a readeable name to the style and aggregate all of the visually contributing styles.
    # Note how we used s.huge (80pt) for the size instead of the listed 72pt. 
    # there is no predefined 72pt style, we could define a new custom one, 
    # but it is prefered to use an existing style that is close enough.
    title = s.project.colors.denim_blue + s.bold + s.huge + s.text.decors.decor_none_text 
    
    # Style '.c9' defines styles that are default (text color black, font style normal, font arial). 
    # The only useful style to explicitely state is 'text-decoration: none',
    # but we can just use 's.text.decors.decor_none_text' when we should use
    # '.c9'.
    
    # Style '.c17' is functionally only defining one style: font-size: 11pt.
    # However, so it the style applied to <p> tags! Since they're the same, we
    # might as well unify them into one style that already exists: s.little. 
    # Whenever we should use either a <p> tag or the 'c.17., we'll just apply s.little.
    
    # Style '.c4' and '.c7' have a lot in common. After all, '.c4' is just '.c7' with an extra 'font-size: 42pt;'. Thus, we can first define '.c7' 
    link_style = s.project.colors.denim_blue + s.text.decors.underline_text
    # and then define '.c4' as an extension of that!
    primary_link = link_style + s.Large # here again, 48pt is the closest to 42pt.
    
    
    # Style '.c21' is applied to the table. It mostly defines one non-default value:
    # 'border-collapse: collapse;'. There is not predefined style in StreamTeX that does that.
    # So we'll just define a completely new one!
    # We'll also take the chance and implement the equal table cell sizing all in one style:
    
    style_fixed_table = Style("table-layout: fixed; width: 100%; border-collapse: collapse;")
    
    # Style '.c15' defines the style for the body of the document. It is defined as:
    # .c15 {
    #     background-color: #ffffff;
    #     max-width: 1152pt;
    #     padding: 36pt 36pt 36pt 36pt
    # }
    # The page's paddings, max-width should all be defined in book.py's st.set_page_config(), 
    # not inside the block! Furthermore, the background color is white, 
    # which is a default color, meaning we should NOT specify it explicitely.
    # Overall, this means that this style should not be implemented at all.
    
    # Style '.c0', while used a lot in all link <a> tags... is just saying
    # that its style is inherited from its parent... which is the default 
    # behavior of CSS styles anyways! This style is providing nothing, and thus
    # is not implemented.
    
    # Style '.c5' defines font size 60pt and bold. 64pt is closest, so we use s.LARGE.
    annotation_text =  s.LARGE + s.bold
    
    # Style '.c2' defines font size 42pt and bold. 48pt is closest, so we use s.Large.
    # However, looking through the document, '.c2' is almost only ever used in tandem with '.c9' (s.text.decors.decor_none_text), thus we can just unify this into one style:
    primary_text = s.Large + s.bold + s.text.decors.decor_none_text
    
    # Style '.c13' is simply defined italic and bold:
    italic_bold = s.italic + s.bold
    
    # Style '.c14' is only ever used in table rows. However, setting the height to 0 contributes nothing to visuals, so it is not implemented.
    
    
    # All of the '.c[n]' styles are converted.
    # However, if we look at how the styles are used in the document, 
    # we quickly see a major pattern:
    # Every <td> uses style '.c3' (cell_border), immediately followed by a <p> 
    # tag using the '.c8' (s.center_txt) style. We can combine these two into a
    # simpler style:
    cell_style = cell_border + s.center_txt
    
    # Additionally, st_grid uses underlying different primitive tags than a <table>.
    # Thus, whenever translating a <table> into a st_grid,
    # the cell_styles must always include `s.container.layouts.vertical_center_layout`
    # to make sure the content inside the table cells are vertically centered.
    cell_style = cell_border + s.center_txt + s.container.layouts.vertical_center_layout
    
    # After all of this thought process and evaluation, what we should expect the BlockStyles to look like is:
    
    
    title = s.project.colors.denim_blue + s.bold + s.huge + s.text.decors.decor_none_text 
    
    link_style = s.project.colors.denim_blue + s.text.decors.underline_text
    primary_link = link_style + s.Large 
    
    italic_bold = s.italic + s.bold
    
    primary_text = s.Large + s.bold + s.text.decors.decor_none_text
    annotation_text =  s.LARGE + s.bold
    
    style_fixed_table = Style("table-layout: fixed; width: 100%; border-collapse: collapse;")
    # combining cell_border into cell_style since it is never used independently
    cell_style = s.container.borders.solid_border + s.container.paddings.small_padding + s.center_txt  + s.container.layouts.vertical_center_layout
    
    
    
    
    

bs = BlockStyles


def build():
    """Show AI music exemplars with artwork, descriptions, and listening links."""
    with st_block(s.center_txt):
        st_write(bs.title, "Music", toc_lvl="1")
    
    # Constructs the st_block for the "_" links.
    def link_row(urls):
        tuples = [(bs.link_style, "_", urls[0])]
        for i in range(1, len(urls)):
            tuples.append(" ")
            tuples.append((bs.link_style, "_", urls[i]))
        st_write(bs.annotation_text, *tuples)
    
    # Table
    with st_grid(
        cols=2,
        grid_style=bs.style_fixed_table,
        cell_styles= bs.cell_style) as g:
        # Row 1
        with g.cell(): 
            st_image(uri="bck_showcase_music_image_002.png",
                     width  = "302.61px",
                     height = "378.50px")
        with g.cell():
            with st_block(s.little):
                st_write(bs.primary_link, "by MuseNet", link=MUSENET_TRACK)
                st_write(bs.italic_bold,
                    "(", (bs.link_style, "MuseNet", MUSENET_RESEARCH)," music published on SoundCloud)")
        # Row 2
        with g.cell():
            st_image(uri="bck_showcase_music_image_001.jpg",
                     width  = "245.67px",
                     height = "388.00px"
            )
        with g.cell():
            with st_block(s.little):
                st_write(bs.primary_link, "JukeBox", link=JUKEBOX_FEATURE)
                st_write(bs.primary_text, "with voice generation")
                link_row(JUKEBOX_SAMPLE_LINKS)
        # Row 3
        with g.cell():
            st_image(uri="bck_showcase_music_image_003.png",
                    width  = "258.62px",
                    height = "350.00px")
        with g.cell():
            with st_block(s.little):
                st_write(bs.primary_link, "Suno", link=SUNO_FEATURE)
                st_write(bs.primary_text, "with voice generation")
                link_row(SUNO_SAMPLE_LINKS)