"""
Setup script for the Tailscale MCP package.
"""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="tailscalemcp",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="FastMCP 2.10 compliant Tailscale network controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tailscalemcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "tailscalemcp": ["py.typed"],
    },
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Typing :: Typed",
    ],
    entry_points={
        "console_scripts": [
            "tailscalemcp=tailscalemcp.__main__:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/tailscalemcp/issues",
        "Source": "https://github.com/yourusername/tailscalemcp",
    },
)
