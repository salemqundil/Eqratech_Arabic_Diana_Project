from setuptools import setup, find_packages

setup(
    name="fvafk",
    version="1.0.0",
    author="Hussein Hiyassat",
    description="Complete Arabic Natural Language Processing Pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fvafk=fvafk.cli.main:main",
        ],
    },
)
