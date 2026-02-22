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
      #674ea7 -> s.project.colors.purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "7. Practice LLM Development Tools ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.1. Chapter : First steps with LangChain ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Introduction to LangChain (official docs) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://python.langchain.com/docs/get_started/introduction")
        with g.cell():
            st_write(s.project.doc.tables.cell, "How to install LangChain (official docs) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://python.langchain.com/docs/get_started/installation")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Official LangChain blog (regularly updated with SOTA techniques) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://blog.langchain.dev/")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.2. Chapter : Prompt Engineering ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Prompt Templates (official docs) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://python.langchain.com/docs/modules/model_io/prompts/prompt_templates/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Prompt Engineering Guide with extensive resources ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.promptingguide.ai/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Prompt Engineering Overview (VIDEO) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=dOxUroR57xs")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Getting Started with Prompt Engineering (NOTEBOOK) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/dair-ai/Prompt-Engineering-Guide/blob/main/notebooks/pe-lecture.ipynb")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.3. Chapter : Chains in LangChain ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Introduction to Chains ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://python.langchain.com/docs/modules/chains/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Comprehensive Guide to Using Chains ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.analyticsvidhya.com/blog/2023/10/a-comprehensive-guide-to-using-chains-in-langchain/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "LangChain Hub ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://smith.langchain.com/hub")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.4. Chapter : Retrieval ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Retrieval introduction (official docs) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://python.langchain.com/docs/modules/data_connection/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Hallucinations and the solution with the RAG technique ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.pinecone.io/learn/retrieval-augmented-generation/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Introduction to the RAG technique and vector databases ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.analyticsvidhya.com/blog/2023/11/rag-langchain-and-vector-databases/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "LangChain Cookbook with many RAG notebooks ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/langchain-ai/langchain/tree/master/cookbook")
        with g.cell():
            st_write(s.project.doc.tables.cell, "RAG: From Theory to LangChain Implementation ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://betterprogramming.pub/harnessing-retrieval-augmented-generation-with-langchain-2eae65926e82")
        with g.cell():
            st_write(s.project.doc.tables.cell, "What is a Vector Database ? (blog post) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.pinecone.io/learn/vector-database/")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.5. Chapter : Memory ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Memory (official docs)")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://python.langchain.com/docs/modules/memory/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Conversational Memory for LLMs with LangChain ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.pinecone.io/learn/series/langchain/langchain-conversational-memory/")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Introduction to memory types in LangChain ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://sonery.medium.com/4-memory-types-of-langchain-to-enhance-the-performance-of-llms-bda339d2e904")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "7.6. Advanced Material - Bonus ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    with st_grid(cols=2, grid_style=s.project.doc.grids.gap) as g:
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "Description ")
        with g.cell():
            st_write(s.project.doc.tables.header + s.project.colors.purple + s.bold, "data ")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (RAG paper) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://arxiv.org/abs/2005.11401")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Harnessing RAG ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://betterprogramming.pub/harnessing-retrieval-augmented-generation-with-langchain-2eae65926e82")
        with g.cell():
            st_write(s.project.doc.tables.cell, "LangChain CookBook: 9 Use Cases (VIDEO) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://www.youtube.com/watch?v=vGP4pQdCocw")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Brex's Prompt Engineering Guide ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://github.com/brexhq/prompt-engineering")
        with g.cell():
            st_write(s.project.doc.tables.cell, "Hallucinations with LLMs (WIKIPEDIA) ")
        with g.cell():
            st_write(s.project.doc.tables.cell + s.project.colors.link_blue + s.bold, "link", link="https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)")
    st_space(size=1)
    st_space(size=1)
