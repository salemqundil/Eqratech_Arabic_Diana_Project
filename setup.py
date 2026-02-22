from setuptools import setup, find_packages

setup(
    name="fvafk",
    version="0.1.0",
    author="Hussein Hiyassat",
    description="Complete Arabic Natural Language Processing Pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "hypothesis>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fvafk=fvafk.cli.main:main",
        ],
    },
)
