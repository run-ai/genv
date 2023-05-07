import setuptools

with open("../README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="genv",
    version="0.10.0",
    author="Run:AI",
    author_email="pypi@run.ai",
    description="GPU Environment Management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/run-ai/genv",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
    ],
)
