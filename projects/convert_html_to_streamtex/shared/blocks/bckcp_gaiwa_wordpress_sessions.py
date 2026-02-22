import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #1155cc -> s.project.colors.link_blue
      #434343 -> s.project.colors.gray
      #666666 -> s.project.colors.gray
    """
    pass

bs = BlockStyles

def build():
    st_write(s.project.doc.titles.h1, "WORPRESS Session", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "1. Useful Information", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.titles.h2, "1.1. Working together ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Don’t be afraid to ask any questions (even if they seem stupid).")
        with lst.item():
            st_write("Bookmark the links to your learner instance")
        with lst.item():
            st_write("The practical sessions demand a bit of creativity, if you don’t have any ideas about what to build, you can build a recipe website (like the demos) by copy and pasting recipes from websites you find on the web. The goal is for you to practice, the content is only for the chatbot to reply with a specific content.")
    st_write(s.project.doc.titles.h2, "1.2. Demo website ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "We provide two versions of the demo website that you can reference and use for the practical sessions. They are basic (content-wise), but show you what is possible with WordPress.")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "Demo ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.bold, "Link ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Basic")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue, "https://demo-mini.gaiwa.ros.lu", link="https://demo-mini.gaiwa.ros.lu")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Advanced")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue, "https://demo.gaiwa.ros.lu", link="https://demo.gaiwa.ros.lu")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "1.3. Access wordpress learner instances ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Visit ",
        (s.project.doc.links.link_body + s.project.colors.link_blue, "https://learnerXX.gaiwa.ros.lu", "https://learnerXX.gaiwa.ros.lu"),
        " where XX should be replaced with your learner number (e.g. 01 to 20, note the leading zero for single digit learner numbers).",
    )
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "1.3.1. Course Credentials ", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "Visit ",
        (s.project.doc.links.link_body + s.project.colors.link_blue, "https://learnerXX.gaiwa.ros.lu/wp-admin", "https://learnerXX.gaiwa.ros.lu/wp-admin"),
        ". ",
    )
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, "Username ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "admin ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Password ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "GAIWA588009 ")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "2. Wordpress Admin interface", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.paragraphs.p_body, "The admin interface in WordPress serves as the control panel where users can manage their website’s content, appearance, functionality, and settings. It provides access to posts, pages, media, themes, plugins, users, and general site configurations through an intuitive dashboard. This area is restricted to authorized users with appropriate roles and permissions.")
    st_write(s.project.doc.titles.h2, "2.1. Access", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        "The admin interface can be accessed by going to ",
        (s.project.doc.links.link_body + s.project.colors.link_blue, "https://learnerXX.gaiwa.ros.lu/wp-admin", "https://learnerXX.gaiwa.ros.lu/wp-admin"),
        ". ",
    )
    st_image(uri="illustration_gaiwa-wordpress-sessions_img79.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Go to ",
                (s.project.doc.links.link_body + s.project.colors.link_blue, "https://learnerXX.gaiwa.ros.lu/wp-admin", "https://learnerXX.gaiwa.ros.lu/wp-admin"),
            )
        with lst.item():
            st_write("Enter your username and password and click the “Log In” button.")
    st_write(s.project.doc.titles.h2, "2.2. Dashboard", tag=t.h2, toc_lvl="+1")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img65.png")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "For the purpose of this course, we will not dive into it more. However, for a real-world WordPress site, it is useful to set up the dashboard to quickly judge the health of the site. ")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "2.2.1. Admin Toolbar ", tag=t.h3)
    st_image(uri="illustration_gaiwa-wordpress-sessions_img99.png")
    st_write(s.project.doc.paragraphs.p_body, "The (Admin) Toolbar in WordPress is a floating menu bar that provides quick access to essential administrative functions, such as site customization, content creation, user management, and updates. It appears at the top of the screen for logged-in users with the appropriate permissions, streamlining navigation between the front end and the admin area. ")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "2.2.2. Sidebar ", tag=t.h3)
    st_image(uri="illustration_gaiwa-wordpress-sessions_img100.png")
    st_write(s.project.doc.paragraphs.p_body, "The Admin Sidebar in WordPress is a vertical menu located on the left side of the Admin Area, providing quick access to key sections such as Posts, Pages, Media, Appearance, Plugins, Users, and Settings. It helps users efficiently navigate and manage their website, with expandable menus for better organization and ease of use. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "3. Wordpress Posts", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.paragraphs.p_body, "Posts in WordPress are dynamic content entries, typically used for blogs, news updates, and regularly updated content. They are organized by categories and tags, making them easy to navigate and discover. Posts appear in reverse chronological order on a website’s blog page and support comments, social sharing, and RSS feeds. They are crucial for engagement, SEO, and AI crawlers, as they provide fresh, indexed content that improves search visibility and user retention. ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "How to access posts? ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("In the sidebar, click on the “Posts” item. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img117.png")
    st_image(uri="illustration_agent-building-workflow-summary_img10.png")
    st_write(s.project.doc.titles.h2, "3.1. Create a post", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the “Add New Post” page. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img102.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The page should look like this: ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img97.png")
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, "Refer to the ", (s.project.colors.link_blue, "Block Editor"), " section to learn how to create and update content on a given post.")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "3.2. Update posts", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Go to the “Posts” page in the admin sidebar. ")
        with lst.item():
            st_write("Click on the title of the post you would like to edit. ")
    st_image(uri="illustration_deep-learning-part-2_img20.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Edit your post and then click “Save” in the right sidebar to update the post. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img105.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "3.3. Delete posts", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "There are two options to delete posts, either one by one or in bulk.")
    st_write(s.project.doc.titles.h3, "3.3.1. Deleting individual posts", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("On the “Posts” page, move the mouse over the post that you want to delete. The “Trash” text should appear. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img128.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the “Trash” text on the post you want to delete. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img61.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The post should now be deleted.")
    st_write(s.project.doc.titles.h3, "3.3.2. Bulk deleting posts", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "With this method multiple posts can be deleted at once. If you unintentionally delete a post, do not worry, the post is in the trash bin and can still be retrieved. ")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Select the posts you would like to delete by clicking on the checkboxes next to the titles of the post. ")
    st_image(uri="illustration_practice-quasible-quick-start_img58.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Bulk actions”. A dropdown menu will appear with multiple options. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img36.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Move to Trash”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img68.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Finally, click on “Apply” to confirm the deletion of the posts. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img120.png")
    st_space(size=1)
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.bold, "Note"), ": This moves the post into the trash. In order to permanently delete the post, you have to click on “Trash” (as explained in ", (s.project.colors.link_blue, "7.5.3.1. States in the posts list"), ") and follow the same procedure as described in this section to delete permanently (either using the individual or bulk method). ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "3.4. Post states & visibility", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Posts can be in multiple states, namely: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Draft"),
                ": The post is in its initial phases of being written. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Pending"),
                ": On a WordPress installation with multiple admins, this state is used to indicate that the post needs to be reviewed by someone else before it can be published. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Private:"),
                " The post is finished, but is not published. This state is useful for retracting posts, but not deleting them. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Scheduled:"),
                " A post can be published on a given date. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Published:"),
                " The post is publicly visible. ",
            )
    st_write(s.project.doc.titles.h3, "3.4.1. States in the posts list", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "When changing the state of a post, the “Posts” page in the admin interface may not show the post (for instance, once a post has been deleted). Using the state filter (as seen below), you can filter the posts that have been set to different states. ")
    st_image(uri="illustration_agentic-ai-overview_img15.png")
    st_write(s.project.doc.titles.h1, "4. Wordpress Categories and Tags", tag=t.h1, toc_lvl="1")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Categories and Tags"),
        " in WordPress are tools for organizing content. Both improve site navigation, enhance user experience, and help visitors find related content easily. They are crucial for SEO as they create structured internal linking, improve content discoverability, and help search engines understand topic relevance, leading to better indexing and rankings. Proper use prevents duplicate content issues and enhances user engagement. ",
    )
    st_space(size=1)
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.bold, "What is SEO? "), "SEO (Search Engine Optimization) in WordPress refers to the practice of optimizing a website’s content, structure, and performance to improve its visibility in search engine results. It involves techniques like keyword optimization, meta tags, fast loading speeds, mobile-friendliness, and structured internal linking. Effective SEO helps attract more organic traffic, enhances user experience, and increases a site's ranking on search engines like Google. ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "When would you use categories vs. tags: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Categories:"),
                " Organize posts hierarchically, e.g. for a travel blog this could be Continents which would then include Asia, Africa, North/South America, etc. ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Tags:"),
                " Keywords that are loosely related, e.g. for a travel blog this could be: beach, mountains, etc. ",
            )
    st_write(s.project.doc.titles.h2, "4.1. Categories", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Categories in WordPress help organize content by grouping related posts, improving site navigation and user experience. They enhance SEO by creating structured taxonomies that allow search engines and AI crawlers to understand content relevance, relationships, and hierarchy. This improves indexing, helps with keyword rankings, and enables AI-driven search engines to deliver more accurate results. Structured categories also contribute to better content recommendations and featured snippets in search engines. ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "4.1.1. Category list", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("In the sidebar, click on “Pages” ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img117.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Under “Pages”, click on “Categories” ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img133.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "4.1.2. Create categories", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "In this section, we explain how to add categories to your WordPress site. However, categories are meaningless if they are not assigned to a post. In ",
        (s.project.colors.link_blue, "Block Editor"),
        ", we will explain how you can add the categories that you learn to create here to posts. ",
    )
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Under “Posts” > “Categories”, you can immediately type in the name, slug and description of the category. The slug is usually a lowercase version of the name that does not contain any spaces (or the spaces are replaced with hyphens). This will appear in the URL bar of your web browser. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img134.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("(Optional) You can also define a “Parent Category” which represents the family to which the category that you are adding belongs to. For example, you could create a category called “Continents” (with the appropriate slug and description). After this, you would then create a category “Europe” and assign the “Continents” parent category to it. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img106.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Finally, click on “Add New Category” to create it. ")
    st_image(uri="illustration_deep-learning-part-2_img10.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "4.1.3. Delete categories", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Move the mouse over the category that you would like to delete. For example, here we want to delete the category that we just created (“Continents”). Click on “Delete”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img107.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Confirm that you want to delete the category. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img93.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The category should now be deleted. ")
    st_space(size=1)
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.bold, "Note:"), " You can follow the same procedure for deleting categories as you did for deleting posts (as described in ", (s.project.colors.link_blue, "7.5.2. Delete posts"), ") with either the individual method (as demonstrated here) or using the bulk selection. ")
    st_space(size=1)
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.bold, "Note:"), " Deleting a category will not delete the posts that are assigned a category. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "4.2. Tags", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Tags in WordPress are a way to categorize content based on specific keywords or topics, providing a more detailed and flexible way to connect related posts. Unlike categories, tags are non-hierarchical and help users and search engines find content with shared themes. They improve site navigation, enhance SEO by allowing AI crawlers to index related topics effectively, and contribute to better content recommendations and search rankings. ")
    st_write(s.project.doc.titles.h3, "4.2.1. Tags list", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("In the sidebar, click on “Pages”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img117.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Under “Pages”, click on “Tags”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img126.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The page should look as follows: ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img64.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "4.2.2. Create tags", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("On the tags page, enter in a name, slug and description.The slug is usually a lowercase version of the name that does not contain any spaces (or the spaces are replaced with hyphens). This will appear in the URL bar of your web browser. For example, here we chose to create a “Beach” tag. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img90.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the “Add New Tag” button to save the tag. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img109.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "4.2.3. Delete tags", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Move the mouse over the tag that you would like to delete in the list on the right. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img2.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the “Delete” text that appears. ")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Confirm the deletion. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img69.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "5. Wordpress Pages", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.paragraphs.p_body, "Pages in WordPress are static content types used for essential, timeless information such as About, Contact, Services, or Homepage. Unlike posts, they are not organized by categories or tags and do not appear in chronological order. Pages help structure a website’s layout, improve navigation, and enhance user experience. They are crucial for SEO as they provide foundational content that AI crawlers use to understand site hierarchy and relevance. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "5.1. Pages list", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Go to the “Pages” section in the Admin sidebar. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img81.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "5.2. Create pages", tag=t.h2, toc_lvl="+1")
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, "Refer to the ", (s.project.colors.link_blue, "Block Editor"), " section to learn how to create and update content on a given page.")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Go to the “Pages” section in the Admin sidebar. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img104.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "The ",
                (s.project.colors.link_blue, "Block Editor"),
                " will be shown. You can add the title and content of your page. ",
            )
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img41.png")
    st_write(s.project.doc.titles.h2, "5.3. Update a page", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the title of the page you would like to edit. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img116.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The block editor for this page will be shown. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img41.png")
    st_write(s.project.doc.titles.h2, "5.4. Delete pages", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        "The deletion method for pages is similar to the one for pages. Refer to ",
        (s.project.colors.link_blue, "5.5.2. Delete posts"),
        " for additional methods of deleting pages (make sure to perform them on the pages). ",
    )
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Move the mouse over the page you would like to delete. ")
    st_image(uri="illustration_bck-showcase-local-models_img2.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Trash” to move the page to the trash. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "6. Wordpress Block Editor", tag=t.h1, toc_lvl="1")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img31.png")
    st_write(s.project.doc.titles.h2, "6.1. Block Editor Components", tag=t.h2, toc_lvl="+1")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img111.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Block Inserter:"),
                " Easily add different types of blocks to the page. ",
            )
    st_image(uri="illustration_practice-quasible-quick-start_img59.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Document Overview:"),
                " Provides an outline of the document as well as a list view. ",
            )
    st_image(uri="illustration_gaiwa-wordpress-sessions_img89.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Settings:"),
                " Access the settings of either the currently selected block or the page/post settings (publishing status, etc.). This will be covered in more detail in the ",
                (s.project.colors.link_blue, "Settings"),
                " section. ",
            )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.2. Block basics", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3, "6.2.1. Quickly add block", tag=t.h3)
    st_image(uri="illustration_gaiwa-wordpress-sessions_img73.png")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Another way to change the block if you don’t know which block you want it to press the “+” icon at the right of the last block (you might need to move the mouse under the last block to see it). ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img46.png")
    st_write(s.project.doc.titles.h3, "6.2.2. Block bar", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "The block bar appears when you type content in a paragraph or move your mouse over the block. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img25.png")
    st_write(s.project.doc.paragraphs.p_body, "Using the block bar, you can edit the properties of the block (such as alignment, color, etc.) as well as transform the block type into another block type. ")
    st_image(uri="illustration_practice-quasible-quick-start_img53.png")
    st_write(s.project.doc.paragraphs.p_body, "The block bar also allows you to delete any kind of block easily, by clicking on the 3 vertical dots on the right of the block bar. ")
    st_image(uri="illustration_agentic-ai-overview_img12.png")
    st_write(s.project.doc.titles.h2, "6.3. Text blocks", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3, "6.3.1. Paragraph", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Paragraphs are the default block type, so you do not need to do anything special to add them. Using the block bar, you can change the style of the text (by selecting the text you want to stylise) to make it bold, italic, as well as change the alignment of the text (and much more). ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img40.png")
    st_write(s.project.doc.titles.h3, "6.3.2. Heading", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "The ",
        (s.italic, "Heading"),
        " block allows you to choose the type of heading (H1 to H6) which allows you to structure your text. The same style options from the ",
        (s.italic, "Paragraph"),
        " also apply here. ",
    )
    st_image(uri="illustration_deep-learning-part-2_img24.png")
    st_write(s.project.doc.titles.h3, "6.3.3. List", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "You can quickly create a list by typing a “-” at the beginning of a paragraph. This will transform the paragraph into a list. In the block bar, you can also indent and outdent list elements. As for the paragraph and heading, the same styling options apply. ")
    st_space(size=1)
    st_image(uri="illustration_gaiwa-wordpress-sessions_img84.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.3.4. Table", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "When choosing a table from your preferred method of adding a block, you have to specify the number of columns and rows beforehand. ")
    st_image(uri="illustration_agentic-ai-overview_img14.png")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "The same formatting options apply as for the previous blocks. However, there are additional options for the table. You can insert rows and columns before & after your current selection inside the table (the cell that contains the text cursor) as well as delete rows and columns. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img118.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.4. Links", tag=t.h2, toc_lvl="+1")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Select the text that you want to add the link to. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img35.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Type in or paste the link into the URL bar. ")
    st_image(uri="illustration_practice-quasible-quick-start_img56.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Press the “Enter” key to set the link. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img119.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.5. Media: Images and Video", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3, "6.5.1. Images", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Using one of the methods to add a block, choose “Image”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img108.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("You are presented two 3 options, either to upload an Image (which will make it available in the Media Library for later), either choosing an image from the Media Library or adding an image from a URL (link). If you already uploaded an image, you can skip to step 4, otherwise follow the step below.")
        with lst.item():
            st_write("Click on “Upload” and select the image from your computer. Once selected, the image will start uploading. ")
    st_image(uri="illustration_aiai-image-test_img1.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("In case you already uploaded an image, you can selected “Media Library”. You will be presented with the following screen. From there you can select the image and press “Select” to insert it into the post/page. ")
    st_image(uri="illustration_aiai-image-test_img1.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Your image should appear after a couple of seconds. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.5.2. Videos", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Video files ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Using your preferred method to add a block, add a “Video” block. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img115.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Similar to the Images, you can either upload the video by clicking “Upload” and choosing a file from your computer or you can use the Media Library if you already uploaded the file.")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The video should appear once it is fully uploaded. ")
    st_image(uri="illustration_agentic-ai-overview_img13.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "YouTube videos ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Using your preferred method to add a block, add a “YouTube Embed URL” block. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img74.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Copy the YouTube link and click on “Embed”. The YouTube video should appear. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img77.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.6. Layout", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "WordPress offers different types of layouts to arrange your content. ")
    st_space(size=1)
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, "Note: Make sure to open the ", (s.project.colors.link_blue, "Document Overview"), " to allow selecting the cells of the different layout types in an easier fashion. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.6.1. Columns", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Columns allow you to organize content horizontally ")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Add a column from the Block Inserter (or another method discussed above) and choose the layout that you would like to use (e.g. 33/66). ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img85.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Now you can add blocks to each column. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img67.png")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "The outline view can also help here to select the different columns in order to add the wanted block type (e.g. an image, etc.). ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img86.png")
    st_write(s.project.doc.titles.h4, "6.6.1.1. Tips", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "You can also use the Document Overview’s List View to manipulate the columns. This makes it easier to delete the entire columns block. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img48.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "6.7. Stacks", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Stacks allow you to organize content vertically. They work in a similar fashion to the columns block. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img78.png")
    st_write(s.project.doc.paragraphs.p_body, "Note how the blocks in the stack are grouped together when selecting any block inside of it. ")
    st_write(s.project.doc.paragraphs.p_body, "You can also click on the “+” icon to add another block to the stack. 	 ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img39.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.7.1. Grid", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "A grid allows you to define a certain number of columns with overflowing content wrapping onto the next rows with the same number of columns as defined. ")
    st_space(size=1)
    st_image(uri="illustration_gaiwa-wordpress-sessions_img101.png")
    st_write(s.project.doc.titles.h4, "6.7.1.1. Resizing the columns of a grid", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("After filling in the first two blocks with a block of your choice, you can resize the first block (by clicking on it) to take up one or more columns by dragging the circle on the right further to the right. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img92.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("This should result in the following: ")
    st_image(uri="illustration_practice-quasible-quick-start_img57.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("You can keep adding blocks using the Document Overview’s List view using the dropdown menu of one of the blocks in the Grid (using “Add after”).  ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img62.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.7.2. Separator", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "The separator visually separates the two blocks as shown on the screenshot below. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img123.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.7.3. Spacer", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "A spacer allows you to add some space between two blocks. The spacer is also resizable, so you can choose how much space should be between two blocks. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img113.png")
    st_write(s.project.doc.titles.h2, "6.8. Settings", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3, "6.8.1. Location", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "The settings can always be accessed from the navigation bar at the top of the screen on the right (left of the “Publish” button). ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img43.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.8.2. Post settings", tag=t.h3)
    st_space(size=1)
    st_image(uri="illustration_gaiwa-wordpress-sessions_img114.png")
    st_space(size=1)
    st_write(
        s.project.doc.paragraphs.p_body,
        "For the blog post, multiple settings can be changed, such as the featured image which appears at the top of the post (usually under the title). In addition, you can also change the publish status (which is discussed in more detail in ",
        (s.project.colors.link_blue, "Post states & visibility"),
        "). Finally, you can move the post to the trash from the post sidebar as well. ",
    )
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img42.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h4, "6.8.2.1. Categories & Tags", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "At the bottom of the post settings, the categories and tags can be found. Here you can add and select the categories and tags for this post. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img94.png")
    st_write(s.project.doc.titles.h3, "6.8.3. Page settings", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "The settings for the page are similar to the post, except that for pages you cannot define categories or tags. ")
    st_image(uri="illustration_agentic-ai-overview_img11.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "6.8.4. Block", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "The block settings vary per block (make sure to select one in the block editor). As such, we will only cover the most common properties for most blocks. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img132.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h4, "6.8.4.1. Text blocks", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Text blocks can be customized to change the text color & background as well as the typography size (the font that is used is determined by the theme). It is also possible to add a border as well as some spacing around the text (padding & margin). ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img95.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "7. Wordpress Customisations ", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.titles.h2, "7.1. Home page", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "The default home page of WordPress can be changed to any other page that you have published as follows: ")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Go to “Settings” in the WordPress admin panel. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img96.png")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Reading” in the submenu of the settings. ")
    st_image(uri="illustration_bck-showcase-local-models_img7.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Under “Your homepage displays”, select “A static page” ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img75.png")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("In the dropdown menu (next to “Homepage”), select the page that you want to replace the current home page with. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img125.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Save your changes after you are done. ")
    st_image(uri="illustration_bck-showcase-local-models_img3.png")
    st_write(s.project.doc.paragraphs.p_body, "Your homepage should now be updated! ")
    with st_grid(cols=1, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.cell, (s.bold, "Note:"), " You may need to follow the instructions in the ", (s.project.doc.links.link_body + s.project.colors.link_blue, "Site navigation", "https://docs.google.com/document/d/1nuMfWoKlVamhXODSKicPKvu3Ipn_vjFbPI07BRmrQQs/edit?tab=t.0#heading=h.j7rjzfyo2x6f"), " section to change how your blog can be accessed. ")
    st_write(s.project.doc.titles.h2, "7.2. Themes", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Themes in WordPress control the design, layout, and appearance of a website without altering its content. They provide templates and customization options for colors, fonts, and layouts, allowing users to create a unique and professional look. Themes also ensure responsiveness, performance optimization, and a consistent user experience across devices. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "7.2.1. Theme selection", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("In the sidebar, click on the “Appearance” item. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img34.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "7.2.2. Install a new theme", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the “Add New Theme” button. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img37.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the search bar or explore the theme selection (here we’re installing the Kadence theme). ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img38.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Move the mouse over the theme you would like to install. A “Install” button should appear. Hint: you can also click on the preview of the theme to see how it would look. ")
    st_image(uri="illustration_ethics-introduction-all_img5.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Once it’s installed, you can immediately activate the theme. ")
    st_image(uri="illustration_practice-quasible-quick-start_img54.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Visit your website to see your new theme. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "7.2.3. Customize theme", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "In general, customizing a WordPress theme is dependent on the theme itself, as different themes may offer different features. However, there are some theme settings that apply to all themes. These can be accessed as follows. ")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("On the currently activated theme (the first one), click on “Customize” ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img88.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("From here you can customize most aspects of the site. Feel free to explore the settings that you can change for your theme. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img70.png")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.3. Site navigation", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        "Changing the site navigation is theme dependent, but can either be found under “Appearance” in the admin interface under “Menus” or you have to follow the instructions to ",
        (s.project.colors.link_blue, "customize the active theme"),
        ". ",
    )
    st_image(uri="illustration_gaiwa-wordpress-sessions_img121.png")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Make sure to follow the instructions of the WordPress website to determine how to change the menus for your theme: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "https://wordpress.com/support/menus/", link="https://wordpress.com/support/menus/")
    st_write(s.project.doc.titles.h2, "7.4. Plugins", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Plugins allow WordPress to be extended with new features. ")
    st_write(s.project.doc.titles.h3, "7.4.1. Location", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("In the sidebar, click on the “Plugins” item. ")
    st_image(uri="illustration_deep-learning-part-2_img23.png")
    st_write(s.project.doc.titles.h3, "7.4.2. Installation", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Add New Plugin”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img80.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Search or select a plugin you would like to install. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img29.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Install Now” to install the plugin. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img127.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Activate the plugin. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img32.png")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "7.4.2.1. Useful plugins ", tag=t.h4)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Forms: ",
                (s.project.doc.links.link_body + s.project.colors.link_blue, "WPForms", "https://wpforms.com/"),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "AI chatbot: Chatbase (the installation of this plugin is discussed in the ",
                (s.project.colors.link_blue, "Chatbase section"),
                ") ",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "8. WordPress AI Plugins", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.titles.h2, "8.1. Chatbase ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.1.1. Sign up ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Go to ",
                (s.project.doc.links.default + s.project.colors.link_blue, "https://www.chatbase.co/", "https://www.chatbase.co/"),
                " and click the “Try for Free” button.",
            )
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img28.png")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click the “Google” button to sign up with Google.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img87.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Follow the instructions to complete the sign up.")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "8.1.1.1. Chatbot creation ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Create a new chatbot by clicking on “New Chatbot”.")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img44.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.1.2. Sources", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "8.1.2.1. Adding a website ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Immediately after creating a chatbot, some content needs to be provided for the chatbot to have a knowledge base.")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Website” on the left part of the page.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img129.png")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Enter the URL of your WordPress website (e.g. ",
                (s.project.doc.links.default + s.project.colors.link_blue, "https://learner01.gaiwa.ros.lu", "https://learner01.gaiwa.ros.lu"),
                ", make sure to change the learner number with your own) and press “Fetch links”.",
            )
    st_image(uri="illustration_gaiwa-wordpress-sessions_img103.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Once Chatbase has fetched the contents of your website, you most likely have to remove some pages as there is a limit for the number of characters you can use as the knowledge base for your chatbot. You can do this by deleting some pages and making sure to stay under the 400.000 character limit. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img20.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Notice how the character limit is now respected. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img49.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("You can now click on the “Create Chatbot” button. This will create the chatbot and you will be able to interact with it from the Chatbase interface. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img83.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.1.3. Chatbot ID & Visibility ", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "The chatbot ID is required for the WordPress installation to know which chatbot should be displayed on the website.")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("After following the instructions to sign up for Chatbase and creating a chatbot. Select your chatbot and then go to the “Settings” page.")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img45.png")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Security”.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img63.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Change the “Visibility” to public. Click on the toggle switch below the text “Only allow the frame and widget on specific domains”. Type in the domain of your learner website (e.g. learner01.gaiwa.ros.lu) under “Allowed domains”. Your screen should look like the following:")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img124.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Go back to the “General” settings and copy the Chatbot ID required to finalise the WordPress installation.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img112.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Make sure to copy the Chatbot ID for the next steps.")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.1.4. WordPress setup ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "8.1.4.1. Plugin installation ", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "In the sidebar on the right, click on “Plugins” and then “Add New Plugin”.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img71.png")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "2. Type in “Chatbase” into the Search Plugin field, followed by “Install Now” on the Chatbase plugin.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img82.png")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Wait for the plugin to be fully installed. The “Install Now” button will change to “Activate”. Click on that button. The plugin should now be installed and activated.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img110.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Settings” in the sidebar. Then click on “Chatbase Options”.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img98.png")
    st_space(size=1)
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Make sure that you have your Chatbase ID (otherwise go back and follow the steps in ",
                (s.project.colors.link_blue, "Chatbot ID & Visibility"),
                "). Paste your Chatbot ID and click “Save Changes”.",
            )
    st_image(uri="illustration_bck-showcase-local-models_img6.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Your chatbot should be visible on your website now.")
    st_image(uri="illustration_bck-showcase-local-models_img9.png")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "8.2. Quasible ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.2.1. Quasible Agent ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "8.2.1.1. Authentication ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Sign in” to connect to Quasible.")
    st_image(uri="illustration_agentic-ai-overview_img16.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Log in with your Google account.")
    st_image(uri="illustration_deep-learning-part-2_img19.png")
    st_write(s.project.doc.titles.h4, "8.2.1.2. Workspace", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Find your learner workspace and open it.")
    st_image(uri="illustration_bck-showcase-local-models_img5.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h4, "8.2.1.3. Crawl a website", tag=t.h4)
    st_write(s.project.doc.paragraphs.p_body, "Before you begin this step, make sure that you already have a least some content on the website, otherwise your chatbot will not have enough information to respond to your questions later on.")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on “Upload” to add your learner WordPress website.")
    st_image(uri="illustration_deep-learning-part-2_img22.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Make sure to select “Link”.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img131.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Enter in your learner website URL (e.g. ",
                (s.project.doc.links.default + s.project.colors.link_blue, "https://learner01.gaiwa.ros.lu", "https://learner01.gaiwa.ros.lu"),
                "). Make sure your link includes https:// or http://. Select “Crawl entire website” and select that you own the rights to the content on the website. At the end, click on “Import”.",
            )
    st_image(uri="illustration_bck-showcase-local-models_img8.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click the “New document” dropdown, then click on “Agent”.")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img47.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("The interface should look like the following now:")
    st_image(uri="illustration_agentic-ai-overview_img18.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Set the context of your agent to the website that we just added to Quasible.")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img60.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("(Optional) Next, add a persona to the chatbot.")
    st_image(uri="illustration_practice-quasible-quick-start_img55.png")
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "8.2.1.4. Publish your agent ", tag=t.h4)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Go to the “General” tab and turn on the “Public agent” switch. ")
    st_image(uri="illustration_ethics-introduction-all_img21.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the “Share” button and copy the link. ")
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img33.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Keep the link that you have just copied for the next steps.")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "8.2.2. WordPress Setup ", tag=t.h3)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Log into the WordPress admin interface (as described in ",
                (s.project.colors.link_blue, "WordPress Access"),
                ")",
            )
        with lst.item():
            st_write("Click on “Settings” in the sidebar, then on “Quasible”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img91.png")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Click on the “Add New Agent” button. ")
    st_image(uri="illustration_ethics-introduction-all_img24.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Enter in the Agent ID (which is the last part after the last slash in the URL you copied from before, e.g. if your URL was ",
                (s.project.doc.links.link_body + s.project.colors.link_blue, "https://quasible.ai/embed/abcd", "https://quasible.ai/embed/abcd"),
                ", the Agent ID is ",
                (s.italic, "abcd"),
                "). You can also provide a name to your agent. ",
            )
    st_image(uri="illustration_agentic-ai-overview_img17.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Next, make sure to enable your agent on your website by clicking on “Enable Quasible on the front-end”. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img72.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Now when you open your learner WordPress instance (e.g., ",
                (s.project.doc.links.link_body + s.project.colors.link_blue, "https://learner01.gaiwa.ros.lu", "https://learner01.gaiwa.ros.lu"),
                "), you should see the Quasible icon appear at the bottom right of your website. ",
            )
    st_image(uri="illustration_deep-learning-part-4-c-transformers_img30.png")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("When clicking on the Quasible icon, you will see the familiar Quasible chatbot that you have configured in the previous steps. ")
    st_image(uri="illustration_gaiwa-wordpress-sessions_img66.png")
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "9. Wordpress Practical sessions", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.titles.h2, "9.1. Session 1 ", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Description:")
    st_write(s.project.doc.paragraphs.p_body, "Participants familiarize themselves with the WordPress admin interface ")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Goals: ")
    st_write(s.project.doc.paragraphs.p_body, "Create a clone of the Begereiles Mini Website. ")
    st_write(s.project.doc.paragraphs.p_body, "At the end of this session, participants should know how to do the following: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Access the admin panel for WordPress and how to connect to it with their credentials. ")
        with lst.item():
            st_write("Create, update & delete posts. ")
        with lst.item():
            st_write("Create, update & delete pages. ")
        with lst.item():
            st_write("Create, update & delete categories & tags. ")
        with lst.item():
            st_write("Be familiar with the block editor. ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Exercises:")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Access ")
        with lst.item():
            pass
        with lst.item():
            st_write("Posts ")
        with lst.item():
            pass
        with lst.item():
            st_write("Pages ")
        with lst.item():
            pass
        with lst.item():
            st_write("Categories and Tags ")
        with lst.item():
            pass
        with lst.item():
            st_write("Block editor ")
        with lst.item():
            pass
        with lst.item():
            st_write("(Advanced) Create a contact page with columns as basic component ")
        with lst.item():
            pass
        with lst.item():
            st_write("(Advanced) Create an images gallery page with images and videos ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "9.2. Session 2 ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Description:"),
        " First experimental chatbot session, first personas and integration into WordPress ",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Goals: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "C",
                "reate a chatbot in either Quasible or Chatbase ",
            )
        with lst.item():
            st_write("Understand the limits of LLM chatbots ")
        with lst.item():
            st_write("Build Chatbot v1 ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Based on content from an existing website (demo) ")
        with lst.item():
            st_write("No persona or 1-2 personas ")
        with lst.item():
            st_write("Only with Quasible / Chatbase ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Exercises:")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Build a simple ChatBot agent with the content from the demo-mini.gaiwa.ros.lu ")
        with lst.item():
            pass
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Brainstorming session about what the issues are with this simple ChatBot agent and what can be done to improve this. ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Duration: 25 minutes ")
        with lst.item():
            st_write("Whole class ")
        with lst.item():
            pass
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("What are the key takeaways from LLM chatbots? ")
    st_space(size=1)
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("(optional) Improve your agent based on the discussion with the class ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "9.3. Session 3 ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Description:"),
        " First prototype of Website + Chatbot ",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Goals: ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Have the v1 version of the website content and the ChatBot  ")
        with lst.item():
            st_write("Deploy the ChatBot on your website ")
        with lst.item():
            st_write("Build ChatBot v1 ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Quasible chatbot + WP content ")
        with lst.item():
            st_write("Big persona with all capabilities inside ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Exercises: ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Define objective of MYWOP WordPress website content (30 minutes) ")
        with lst.item():
            pass
        with lst.item():
            st_write("Work on Website content (30 minutes) ")
        with lst.item():
            pass
        with lst.item():
            st_write("Define the chatbot expertise (20 minutes) ")
        with lst.item():
            st_write("Write the prompts for the persona (30 minutes) ")
        with lst.item():
            st_write("Test the chatbot (20 minutes) ")
        with lst.item():
            pass
        with lst.item():
            st_write("Integrate the chatbot into your website (10 minutes) ")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "ADVISE - Follow an interactive approach for your ChatBot: ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("No prompt ")
        with lst.item():
            st_write("Very basic prompt (with persona) ")
        with lst.item():
            st_write("More advanced prompt (with two personas, in-sequence and not in-sequence) ")
        with lst.item():
            st_write("More detailed prompt (with 3 personas)")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "9.4. Session 4 ", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Description:"),
        " Second iteration of Website + Chatbot ",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Goals: ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Work on second iteration ")
        with lst.item():
            pass
        with lst.item():
            st_write("Discuss altogether about the challenges of building a chatbot ")
        with lst.item():
            st_write("Build Chatbot v2 ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Quasible chatbot + WP content ")
        with lst.item():
            st_write("Context dependent on participant  ")
        with lst.item():
            st_write("3 personas that work in-sequence")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Exercises: ")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Create 3 chatbots (with the following personas) ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Moderator persona: limit types of questions that can be answered, e.g. filter good/bad questions ")
        with lst.item():
            st_write("Commercial persona: Promote services on the website ")
        with lst.item():
            st_write("Technical support persona: Explain also technical knowledge of website, e.g. to solve a problem ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "9.5. Session 5", tag=t.h2, toc_lvl="+1")
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Description:"),
        " Third iteration of Website + Chatbot ",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Goals: ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Experiment the impact of website content evaluation on GenAI ChatBots")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Exercises:")
    with st_list(list_type=lt.ordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Add a lot more MYWOP content. ")
        with lst.item():
            st_write("Re-engineer the 3 chatbots from the previous session. ")
        with lst.item():
            st_write("(Optional) Create a Q&A chatbot agent that maps any user question to a static question database and outputs the predefined answer ")
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                "Prepare for the Final Presentations & Peer Feedback (30 minutes)",
                (s.bold, "Format:"),
                " Each participant (or group) presents their Website + Chatbot project. Suggested presentation points include: ",
            )
        with lst.item():
            pass
    st_write(s.project.doc.titles.h1, "10. References", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.titles.h2, "10.1. Real-world WordPress websites", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Here are some real world websites that use WordPress.")
    st_write(s.project.doc.titles.h3, "10.1.1. News", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "Meta Newsroom", link="https://about.fb.com/news/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "Time Magazine", link="https://time.com/")
    st_write(s.project.doc.titles.h3, "10.1.2. Music", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "The Rolling Stones", link="https://rollingstones.com/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "Taylor Swift", link="https://rollingstones.com/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "Jay-Z", link="https://lifeandtimes.com/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "Katy Perry", link="https://www.katyperry.com/")
    st_write(s.project.doc.titles.h3, "10.1.3. Aerospace agencies", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "NASA", link="https://www.nasa.gov/")
    st_write(s.project.doc.titles.h2, "10.2. Recipe websites", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.titles.h3, "10.2.1. English", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.allrecipes.com/", link="https://www.allrecipes.com/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.simplyrecipes.com/", link="https://www.simplyrecipes.com/")
    st_write(s.project.doc.titles.h3, "10.2.2. French", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.cuisineaz.com/", link="https://www.cuisineaz.com/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.marmiton.org/", link="https://www.marmiton.org/")
    st_write(s.project.doc.titles.h3, "10.2.3. German", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.chefkoch.de/", link="https://www.chefkoch.de/")
        with lst.item():
            st_write(s.project.doc.links.default + s.project.colors.link_blue, "https://www.lecker.de/", link="https://www.lecker.de/")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Wordpress usage statistics")
    st_write(s.project.doc.paragraphs.p_body, "https://www.wpzoom.com/blog/wordpress-statistics")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.project.doc.links.link_body + s.project.colors.link_blue, "WordPress Support", link="https://wordpress.com/support/")
    st_space(size=1)
