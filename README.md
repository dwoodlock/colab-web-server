# colab-web-server

A lightweight helper library for teaching and demonstrations in Google Colab.

**Credit:** This entire repository was written by [Claude Code](https://claude.com/claude-code).

## Installation

In a Colab notebook:

```python
!git clone https://github.com/your-org/colab-web-server.git
import sys
sys.path.insert(0, "/content/colab-web-server")

from web_server import server
