"""Composite block - groups multiple atomic blocks."""

import streamtex as stx
from streamtex import st_include


bck_deploy_docker = stx.load_atomic_block("bck_deploy_docker", __file__)
bck_deploy_huggingface = stx.load_atomic_block("bck_deploy_huggingface", __file__)
bck_deploy_cloud = stx.load_atomic_block("bck_deploy_cloud", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for this section."""
    st_include(bck_deploy_docker)
    st_include(bck_deploy_huggingface)
    st_include(bck_deploy_cloud)
