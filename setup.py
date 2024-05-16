import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="genv",
    version="1.4.3",
    author="Run.ai",
    author_email="pypi@run.ai",
    description="GPU environment and cluster management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/run-ai/genv",
    packages=setuptools.find_packages(),
    package_data={"genv": ["shims/*", "metrics/export/**/*"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: GPU",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
    ],
    entry_points={
        "console_scripts": [
            "genv = genv.cli.__main__:main",
        ]
    },
    python_requires=">=3.7",
    install_requires="psutil",
    extras_require={
        "admin": ["prometheus_client"],
        "dev": ["black"],
        "monitor": ["prometheus_client"],
        "ray": ["ray", "pynvml"],
    },
)
