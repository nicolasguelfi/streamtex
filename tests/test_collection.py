"""Tests for st_collection and collection configuration."""

import os
import tempfile
import pytest
from pathlib import Path

from streamtex.collection import (
    CollectionConfig,
    ProjectMeta,
)


class TestProjectMeta:
    """Test ProjectMeta dataclass."""

    def test_create_project_meta(self):
        """Test creating a ProjectMeta instance."""
        project = ProjectMeta(
            title="Test Course",
            description="A test course",
            cover="static/covers/test.png",
            project_url="http://localhost:8502",
            order=1,
        )

        assert project.title == "Test Course"
        assert project.description == "A test course"
        assert project.project_url == "http://localhost:8502"
        assert project.order == 1

    def test_project_meta_defaults(self):
        """Test ProjectMeta with default values."""
        project = ProjectMeta(title="Minimal Course")

        assert project.title == "Minimal Course"
        assert project.description == ""
        assert project.cover == ""
        assert project.project_url == ""
        assert project.order == 0


class TestCollectionConfig:
    """Test CollectionConfig dataclass and TOML parsing."""

    @pytest.fixture
    def temp_toml(self):
        """Create a temporary TOML file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("""
[collection]
title = "University Course Library"
description = "Curated courses for learning"
cards_per_row = 3

[projects.project-aiai18h]
title = "AI & AI 18h"
description = "An 18-hour course on AI"
cover = "static/images/covers/project-aiai18h.png"
project_url = "http://localhost:8502"
order = 1

[projects.project-html-example]
title = "HTML Migration"
description = "Learn to migrate HTML to StreamTeX"
cover = "static/images/covers/project-html-example.png"
project_url = "http://localhost:8503"
order = 2
""")
            f.flush()
            yield f.name

        # Cleanup
        os.unlink(f.name)

    def test_create_collection_config(self):
        """Test creating a CollectionConfig instance."""
        config = CollectionConfig(
            title="My Collection",
            description="A test collection",
            cards_per_row=2,
        )

        assert config.title == "My Collection"
        assert config.description == "A test collection"
        assert config.cards_per_row == 2
        assert len(config.projects) == 0

    def test_collection_config_defaults(self):
        """Test CollectionConfig with default values."""
        config = CollectionConfig()

        assert config.title == "StreamTeX Collection"
        assert config.description == ""
        assert config.cards_per_row == 3

    def test_from_toml_parsing(self, temp_toml):
        """Test parsing a collection.toml file."""
        config = CollectionConfig.from_toml(temp_toml)

        assert config.title == "University Course Library"
        assert config.description == "Curated courses for learning"
        assert config.cards_per_row == 3
        assert len(config.projects) == 2

    def test_from_toml_projects(self, temp_toml):
        """Test that projects are correctly parsed from TOML."""
        config = CollectionConfig.from_toml(temp_toml)

        # Check project 1
        assert "project-aiai18h" in config.projects
        project1 = config.projects["project-aiai18h"]
        assert project1.title == "AI & AI 18h"
        assert project1.description == "An 18-hour course on AI"
        assert project1.project_url == "http://localhost:8502"
        assert project1.order == 1

        # Check project 2
        assert "project-html-example" in config.projects
        project2 = config.projects["project-html-example"]
        assert project2.title == "HTML Migration"
        assert project2.project_url == "http://localhost:8503"
        assert project2.order == 2

    def test_from_toml_projects_ordered(self, temp_toml):
        """Test that projects are ordered by the 'order' field."""
        config = CollectionConfig.from_toml(temp_toml)

        # Projects should be in order
        project_keys = list(config.projects.keys())
        assert project_keys == ["project-aiai18h", "project-html-example"]

    def test_from_toml_missing_file(self):
        """Test that missing TOML file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            CollectionConfig.from_toml("nonexistent.toml")

    def test_from_toml_with_absolute_path(self, temp_toml):
        """Test parsing TOML with absolute path."""
        abs_path = os.path.abspath(temp_toml)
        config = CollectionConfig.from_toml(abs_path)

        assert config.title == "University Course Library"

    def test_from_toml_with_relative_path(self, temp_toml):
        """Test parsing TOML with relative path."""
        # Change to parent directory and use relative path
        original_cwd = os.getcwd()
        try:
            temp_dir = os.path.dirname(temp_toml)
            os.chdir(temp_dir)
            rel_path = os.path.basename(temp_toml)

            config = CollectionConfig.from_toml(rel_path)
            assert config.title == "University Course Library"
        finally:
            os.chdir(original_cwd)

    def test_from_toml_minimal(self):
        """Test parsing a minimal TOML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("""
[collection]
title = "Minimal Collection"

[projects.minimal-project]
title = "Minimal Project"
project_url = "http://localhost:8502"
""")
            f.flush()
            temp_file = f.name

        try:
            config = CollectionConfig.from_toml(temp_file)

            assert config.title == "Minimal Collection"
            assert config.description == ""
            assert config.cards_per_row == 3
            assert len(config.projects) == 1
            assert "minimal-project" in config.projects
        finally:
            os.unlink(temp_file)

    def test_from_toml_empty_projects(self):
        """Test parsing TOML with no projects."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("""
[collection]
title = "Empty Collection"
""")
            f.flush()
            temp_file = f.name

        try:
            config = CollectionConfig.from_toml(temp_file)

            assert config.title == "Empty Collection"
            assert len(config.projects) == 0
        finally:
            os.unlink(temp_file)

    def test_from_toml_missing_collection_section(self):
        """Test parsing TOML without [collection] section."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("""
[projects.project-1]
title = "Project 1"
project_url = "http://localhost:8502"
""")
            f.flush()
            temp_file = f.name

        try:
            config = CollectionConfig.from_toml(temp_file)

            # Should use defaults
            assert config.title == "StreamTeX Collection"
            assert len(config.projects) == 1
        finally:
            os.unlink(temp_file)

    def test_add_project_manually(self):
        """Test adding projects manually to config."""
        config = CollectionConfig(title="Custom Collection")

        project1 = ProjectMeta(
            title="Course 1",
            project_url="http://localhost:8502",
            order=1,
        )
        project2 = ProjectMeta(
            title="Course 2",
            project_url="http://localhost:8503",
            order=2,
        )

        config.projects["course1"] = project1
        config.projects["course2"] = project2

        assert len(config.projects) == 2
        assert config.projects["course1"].title == "Course 1"


class TestCollectionIntegration:
    """Integration tests for collection workflow."""

    @pytest.fixture
    def multi_toml(self):
        """Create a realistic multi-project TOML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("""
[collection]
title = "Complete University Library"
description = "All courses offered in 2025"
cards_per_row = 3

[projects.ai-course]
title = "AI & Machine Learning"
description = "A comprehensive course on AI"
cover = "static/covers/ai.png"
project_url = "http://localhost:8502"
order = 1

[projects.web-dev]
title = "Web Development"
description = "Build web applications"
cover = "static/covers/web.png"
project_url = "http://localhost:8503"
order = 2

[projects.data-science]
title = "Data Science"
description = "Analytics and visualization"
cover = "static/covers/data.png"
project_url = "http://localhost:8504"
order = 3
""")
            f.flush()
            yield f.name

        os.unlink(f.name)

    def test_full_collection_workflow(self, multi_toml):
        """Test loading and accessing a full collection."""
        config = CollectionConfig.from_toml(multi_toml)

        # Verify collection metadata
        assert config.title == "Complete University Library"
        assert config.cards_per_row == 3

        # Verify all projects loaded
        assert len(config.projects) == 3

        # Verify project ordering
        project_list = list(config.projects.items())
        assert project_list[0][0] == "ai-course"
        assert project_list[1][0] == "web-dev"
        assert project_list[2][0] == "data-science"

        # Verify project properties
        web_dev = config.projects["web-dev"]
        assert web_dev.title == "Web Development"
        assert web_dev.order == 2

    def test_collection_with_missing_urls(self):
        """Test handling projects without project_url."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write("""
[collection]
title = "Test"

[projects.incomplete-project]
title = "Incomplete"
""")
            f.flush()
            temp_file = f.name

        try:
            config = CollectionConfig.from_toml(temp_file)

            project = config.projects["incomplete-project"]
            assert project.project_url == ""  # Empty, not None
            assert project.title == "Incomplete"
        finally:
            os.unlink(temp_file)
