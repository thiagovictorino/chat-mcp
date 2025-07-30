# Contributing to Multi-Agent Communication Platform (MCP)

Thank you for your interest in contributing to MCP! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
1. Check the [existing issues](https://github.com/YOUR_USERNAME/chat-mcp/issues) to avoid duplicates
2. Collect relevant information:
   - MCP version
   - Python/Node.js versions
   - Operating system
   - Steps to reproduce
   - Error messages and logs

### Suggesting Features

1. Check if the feature has already been suggested
2. Open a new issue with the `enhancement` label
3. Clearly describe the feature and its use cases
4. Explain why this feature would be useful

### Pull Request Process

1. **Setup Development Environment**
   ```bash
   # Fork and clone the repository
   git clone https://github.com/YOUR_USERNAME/chat-mcp.git
   cd chat-mcp
   
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Install frontend dependencies
   cd ui && npm install
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Write meaningful commit messages
   - Add or update tests as needed
   - Update documentation

4. **Testing**
   ```bash
   # Backend tests
   pytest tests/
   pytest --cov=mcp_server tests/
   
   # Linting
   flake8 mcp_server/
   black mcp_server/ --check
   mypy mcp_server/
   
   # Frontend tests
   cd ui
   npm test
   npm run lint
   ```

5. **Submit Pull Request**
   - Push your branch to your fork
   - Open a PR against the `main` branch
   - Fill out the PR template
   - Link related issues

## Development Guidelines

### Python Code Style

- Follow PEP 8
- Use type hints where possible
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names

Example:
```python
from typing import List, Optional

async def create_channel(
    name: str, 
    description: Optional[str] = None,
    max_agents: int = 50
) -> Channel:
    """Create a new communication channel.
    
    Args:
        name: Unique channel name
        description: Optional channel description
        max_agents: Maximum number of agents allowed
        
    Returns:
        The created Channel instance
    """
    # Implementation
```

### JavaScript/React Code Style

- Use ES6+ features
- Prefer functional components with hooks
- Use TypeScript for new components
- Follow Airbnb style guide

Example:
```typescript
interface MessageProps {
  content: string;
  author: string;
  timestamp: Date;
}

const Message: React.FC<MessageProps> = ({ content, author, timestamp }) => {
  // Component implementation
};
```

### Commit Messages

Follow the conventional commits specification:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Maintenance tasks

Example:
```
feat: add message search functionality

- Implement full-text search for channel messages
- Add search UI component with filters
- Update API to support search queries
```

### Testing

- Write tests for new features
- Maintain or increase code coverage
- Use meaningful test names
- Test edge cases

Example:
```python
async def test_channel_creation_with_invalid_name():
    """Test that channel creation fails with invalid names."""
    with pytest.raises(ValueError):
        await create_channel("")  # Empty name
        
    with pytest.raises(ValueError):
        await create_channel("a" * 101)  # Too long
```

## Project Structure

```
chat-mcp/
├── mcp_server/         # Backend MCP server
│   ├── services/       # Business logic
│   ├── tools/          # MCP tool implementations
│   ├── api/            # REST API endpoints
│   └── models/         # Data models
├── ui/                 # React frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── services/   # API clients
│   │   └── utils/      # Utilities
│   └── public/
├── tests/              # Test suite
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
└── docs/              # Documentation
```

## Getting Help

- Join our [Discussions](https://github.com/YOUR_USERNAME/chat-mcp/discussions)
- Check the [documentation](./docs)
- Ask questions in issues with the `question` label

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- The contributors page

Thank you for contributing to MCP! 🎉