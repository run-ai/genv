import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="genv",
    version="0.12.0",
    author="Run:AI",
    author_email="pypi@run.ai",
    description="GPU Environment Management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/run-ai/genv",
    packages=setuptools.find_packages(),
    package_data={"genv": ["shims/*", "metrics/export/**/*"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
    ],
    entry_points={
        "console_scripts": [
            "genv = genv.cli.__main__:main",
        ]
    },
    extras_require={"monitor": ["prometheus_client"]},
)