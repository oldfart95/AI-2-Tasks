# AI-Driven Productivity Shell Tool

A powerful productivity tool that combines natural language task parsing with command generation to help you accomplish tasks more efficiently.

## Overview

This tool merges the capabilities of two projects:

1. **AI-Shell-Agent**: Provides natural language command generation
2. **Taskmaster**: Offers task parsing and execution framework

Together, they form a unified CLI wrapper that:

- Takes free-form natural language input
- Breaks it down into discrete "Verb + Object" tasks
- Generates appropriate shell commands for each task
- Presents suggestions in a REPL, allowing you to approve/modify before execution

## Installation

### Prerequisites

- Python 3.9+ (tested with Python 3.13)
- Git
- Access to OpenAI API or other LLM API (for command generation)

### Setup

1. Clone the repository and its dependencies:

```bash
git clone https://github.com/yourusername/ai-to-tasks.git
cd ai-to-tasks
```

2. Set up a Python virtual environment (recommended):

```bash
# Using conda
conda create -n ai-to-tasks python=3.13
conda activate ai-to-tasks

# OR using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:

```bash
pip install -e .
```

4. Configure API access:

Create a `.env` file in the project root:

```ini
# OpenAI API settings
OPENAI_API_KEY=your_api_key_here
# Or use other supported providers
```

## Usage

Run the tool from the command line:

```bash
ai-tasks
```

This will start the interactive REPL interface where you can:

1. Type natural language requests like:
   - "Find all PDF files in my Documents folder"
   - "Create a backup of my project and compress it"
   - "Show system information and check disk space"

2. The tool will break these down into discrete tasks
3. Generate shell commands for each task
4. Allow you to approve, edit, or skip each command

### Example Session

```
┌─────────────────────────────────────────┐
│  AI-DRIVEN PRODUCTIVITY SHELL TOOL      │
│                                         │
│  Natural Language → Tasks → Commands    │
└─────────────────────────────────────────┘
Type 'exit' or 'quit' to exit, 'help' for help.

>> Find large files in this directory and show disk space

I've broken that down into 2 tasks:
1. Find large files in this directory
2. Show disk space

Processing task: find large files in this directory

AI suggests: find . -type f -size +10M -exec ls -lh {} \;
Explanation: This command searches for files larger than 10MB in the current directory and its subdirectories, then displays them in a human-readable format.

Run this command? (y/N/edit): y

Executing: find . -type f -size +10M -exec ls -lh {} \;

Output:
-rw-r--r-- 1 user group 15M May 6 12:30 ./large_file.zip
-rw-r--r-- 1 user group 22M May 6 12:31 ./backup.tar.gz

✓ Command executed successfully

Processing task: show disk space

AI suggests: df -h
Explanation: The df command shows disk space usage with the -h flag displaying sizes in human-readable format (KB, MB, GB).

Run this command? (y/N/edit): y

Executing: df -h

Output:
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       234G   67G  156G  31% /
tmpfs           3.2G     0  3.2G   0% /dev/shm

✓ Command executed successfully
```

## Customization

You can customize the tool by:

1. Modifying prompts in `cli/task_parser.py` and `cli/command_synthesizer.py`
2. Adjusting the LLM model used in `cli/agent.py`
3. Adding new features to the REPL interface

## Architecture

- **cli/agent.py**: Main CLI wrapper and REPL interface
- **cli/task_parser.py**: Breaks down natural language into verb-object pairs
- **cli/command_synthesizer.py**: Converts verb-object pairs into shell commands
- **ai-agent/**: AI-Shell-Agent repository (LLM integration)
- **task-parser/**: Taskmaster repository (task parsing framework)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 