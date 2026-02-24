"""Composite block — Docker local deployment (Dockerfile + build/run + compose)."""

import streamtex as stx
from streamtex import st_include


bck_dockerfile = stx.load_atomic_block("bck_dockerfile", __file__)
bck_docker_build_run = stx.load_atomic_block("bck_docker_build_run", __file__)
bck_docker_compose = stx.load_atomic_block("bck_docker_compose", __file__)


class BlockStyles:
    """Composite block styles."""
    pass


def build():
    """Include atomic blocks for Docker local deployment."""
    st_include(bck_dockerfile)
    st_include(bck_docker_build_run)
    st_include(bck_docker_compose)
