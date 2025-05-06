from setuptools import setup, find_packages

setup(
    name="ai-to-tasks",
    version="0.1.0",
    description="AI-driven productivity shell tool combining natural language task parsing and command generation",
    author="AI Developer",
    author_email="ai@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv>=1.0.0",
        "langchain-core>=0.1.0",
        "prompt_toolkit>=3.0.0",
        "rich>=13.0.0",
        "pyzmq>=25.0.0",
        "gevent>=23.9.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-tasks=cli.agent:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
) 