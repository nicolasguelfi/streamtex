"""Collections System: Multi-project management and discovery (Phase 2).

This block explains the collections system for organizing multiple projects.
Collections enable project discovery, navigation, and organization.
"""

from streamtex import st_write, st_block, st_space, Style
from streamtex.enums import Tags as t
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details


class BlockStyles:
    """Styles for this block."""
    feature_box = Style(
        "background:rgba(100,150,200,0.1);padding:16px;border-radius:8px;border-left:4px solid rgba(100,150,200,0.5);",
        "feature_box"
    )


bs = BlockStyles


def build():
    """Build the collections system documentation block."""

    st_write(s.project.titles.page_title, "Collections: Multi-Project Management", tag=t.h1, toc_lvl="1")
    st_space("v", 1)

    show_explanation("""
The Collections System (Phase 2) enables organizing multiple projects.
Create a hub where users discover, navigate, and access different projects.
Think: Coursera with multiple courses, or a documentation portal with multiple docs.
    """)

    # ========================================================================
    # WHAT ARE COLLECTIONS?
    # ========================================================================
    st_write(s.project.titles.section_title, "What Are Collections?", toc_lvl="+1")
    st_space("v", 1)

    with st_block(bs.feature_box):
        st_write(s.large, """
A **Collection** is a container for multiple StreamTeX projects.
Each project is a complete application (book, course, documentation).
The collection provides discovery, navigation, and project management.

Examples:
- Training platform with multiple courses
- Documentation portal with different docs
- Learning path with multiple modules
    """)

    st_space("v", 2)

    # ========================================================================
    # COMPONENTS
    # ========================================================================
    st_write(s.project.titles.section_title, "Collections Components", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.project.titles.feature_title, "1. st_collection() - Main Function")
    show_code("""
from streamtex import st_collection, CollectionConfig

config = CollectionConfig(
    title="My Training Platform",
    description="Multiple courses in one place",
    projects=[
        # List of projects
    ]
)

st_collection(config)
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "2. CollectionConfig - Configuration Class")
    show_code("""
from streamtex import CollectionConfig, ProjectMeta

config = CollectionConfig(
    title="Learning Hub",
    description="Organized learning platform",
    projects=[
        ProjectMeta(name="Python Basics", path="projects/python"),
        ProjectMeta(name="Web Development", path="projects/web"),
    ],
    theme="light",  # or "dark"
    show_search=True,  # Enable search across projects
)
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "3. ProjectMeta - Project Metadata")
    show_code("""
from streamtex import ProjectMeta

project = ProjectMeta(
    name="Advanced Python",
    path="projects/advanced-python",
    description="Deep dive into Python",
    icon="🐍",
    author="John Doe",
    version="1.0.0",
    tags=["python", "advanced", "programming"],
    color="#3776ab"  # Project accent color
)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # CONFIGURATION METHODS
    # ========================================================================
    st_write(s.project.titles.section_title, "Configuration Methods", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Method 1: Programmatic (Python)")
    show_code("""
from streamtex import st_collection, CollectionConfig, ProjectMeta

projects = [
    ProjectMeta(
        name="Introduction",
        path="projects/intro",
        description="Get started with basics"
    ),
    ProjectMeta(
        name="Advanced",
        path="projects/advanced",
        description="Deep dive into concepts"
    ),
    ProjectMeta(
        name="Reference",
        path="projects/reference",
        description="API and concepts reference"
    ),
]

config = CollectionConfig(
    title="StreamTeX Learn",
    description="Complete learning path",
    projects=projects
)

st_collection(config)
    """, language="python")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Method 2: TOML Configuration File")
    show_code("""
# collection.toml
[collection]
title = "StreamTeX Learn"
description = "Complete learning path"
theme = "light"

[[projects]]
name = "Introduction"
path = "projects/intro"
description = "Get started with basics"
icon = "📚"

[[projects]]
name = "Advanced"
path = "projects/advanced"
description = "Deep dive into concepts"
icon = "🚀"

# Then in Python:
from streamtex import CollectionConfig, st_collection

config = CollectionConfig.from_toml("collection.toml")
st_collection(config)
    """, language="toml")

    st_space("v", 2)

    # ========================================================================
    # FEATURES
    # ========================================================================
    st_write(s.project.titles.section_title, "Collection Features", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, """
**Project Discovery**
- Browse all available projects
- Filter by tags or categories
- Search project names and descriptions

**Navigation**
- Click to open any project
- Breadcrumb shows collection → project
- Back button returns to collection hub

**Metadata Display**
- Project icon and description
- Author and version information
- Tags for categorization
- Progress indicators (optional)

**Theme Support**
- Light/dark mode for collection hub
- Per-project theming support
- Consistent design across projects

**Project Organization**
- Group related projects
- Feature recommended projects
- Show project progression path
    """)

    st_space("v", 2)

    # ========================================================================
    # PRACTICAL EXAMPLE
    # ========================================================================
    st_write(s.project.titles.section_title, "Complete Example: Training Hub", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
Real-world example: Building a training platform with 3 courses.
    """)

    show_code("""
from streamtex import st_collection, CollectionConfig, ProjectMeta

# Define courses
courses = [
    ProjectMeta(
        name="Python Fundamentals",
        path="projects/python-101",
        description="Learn Python basics",
        icon="🐍",
        author="Alice",
        version="2.0.0",
        tags=["python", "beginner"],
        color="#3776ab"
    ),
    ProjectMeta(
        name="Web Development",
        path="projects/web-dev",
        description="Build web applications",
        icon="🌐",
        author="Bob",
        version="1.5.0",
        tags=["web", "intermediate"],
        color="#FF7C00"
    ),
    ProjectMeta(
        name="Data Science",
        path="projects/data-science",
        description="Data analysis and ML",
        icon="📊",
        author="Carol",
        version="1.0.0",
        tags=["data", "advanced"],
        color="#00A080"
    ),
]

# Create collection
hub_config = CollectionConfig(
    title="Technology Training Hub",
    description="Comprehensive training platform with multiple courses",
    projects=courses,
    theme="dark",
    show_search=True
)

# Display collection
st_collection(hub_config)
    """, language="python")

    st_space("v", 2)

    # ========================================================================
    # BEST PRACTICES
    # ========================================================================
    st_write(s.project.titles.section_title, "Best Practices", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, """
✓ **DO:**
- Use meaningful project names
- Provide descriptive descriptions (100+ chars)
- Assign relevant icons (emoji or Unicode)
- Group related projects together
- Use consistent versioning scheme
- Add helpful tags for discovery
- Set appropriate access permissions

✗ **DON'T:**
- Overcrowd with too many projects (>20)
- Use vague descriptions ("Project 1")
- Mix different topics in one collection
- Change project paths after deployment
- Use broken icon references
- Add too many tags (3-5 is optimal)
    """)

    st_space("v", 2)

    # ========================================================================
    # DEPLOYMENT
    # ========================================================================
    st_write(s.project.titles.section_title, "Deploying Collections", toc_lvl="+1")
    st_space("v", 1)

    show_explanation("""
Collections can be deployed to cloud platforms like other projects.
Use the same deployment methods as single projects.
    """)

    st_write(s.project.titles.feature_title, "Docker Deployment:")
    show_code("""
# Build collection container
docker build --build-arg FOLDER=collection -t my-training-hub .

# Run
docker run -p 8501:8501 my-training-hub
    """, language="bash")

    st_space("v", 1)

    st_write(s.project.titles.feature_title, "Hugging Face Spaces:")
    show_code("""
# Push to HF Space with collection folder
git remote add space https://huggingface.co/spaces/username/my-hub
git push space main
    """, language="bash")

    st_space("v", 2)

    # ========================================================================
    # COMPARISON: PROJECT VS COLLECTION
    # ========================================================================
    st_write(s.project.titles.section_title, "Project vs Collection", toc_lvl="+1")
    st_space("v", 1)

    st_write(s.large, """
**Single Project** (st_book):
- One application/course/documentation
- Self-contained
- Example: "Python Training Course"

**Collection** (st_collection):
- Multiple projects in one hub
- Project discovery and navigation
- Example: "Training Platform" with Python, Web, Data courses

**When to use Collections:**
- Multiple independent projects to manage
- Need centralized project hub
- Want project discovery/search
- Building platform (multi-course, multi-doc)
    """)

    st_space("v", 2)

    show_details("""
Organizing large projects
- Break into logical sub-projects
- Each gets its own entry in collection
- Users navigate to relevant content easily
- Easier to maintain and update individually
    """)
