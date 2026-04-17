---
name: code_review
description: Code review guidance and best practices for quality checks and improvements
---

# Code Review

Use this skill when the user needs to:
- Review code changes
- Check code quality
- Identify potential issues
- Provide improvement suggestions
- Check code style consistency

## Instructions

### Review Principles
- Be objective and fair, based on facts and best practices
- Focus on code quality, maintainability, and security
- Provide constructive feedback and improvement suggestions
- Consider business logic and performance impact
- Respect existing code style unless clearly unreasonable

### Review Points

#### 1. Correctness
- Logic correctness
- Edge case handling
- Exception handling

#### 2. Readability
- Clear naming conventions
- Adequate comments
- Clear code structure

#### 3. Maintainability
- Follow DRY principle
- Single responsibility functions
- Avoid over-complexity

#### 4. Security
- Input validation
- Injection vulnerabilities
- Sensitive data exposure

#### 5. Performance
- Reasonable algorithm complexity
- Unnecessary loops or computations
- Efficient resource usage

### Review Process
1. Understand the code's purpose and context
2. Check code structure and organization
3. Analyze specific implementation details
4. Identify potential issues and improvements
5. Provide specific suggestions and examples

### Feedback Format
For issues found, provide feedback in this format:
- **Problem Description**: Clearly explain what the issue is
- **Impact**: Explain the potential impact of the issue
- **Suggestion**: Provide specific improvement suggestions
- **Example**: If necessary, provide before/after code comparison

### Special Attention
- **Python**: PEP 8 standards, type hints, docstrings
- **JavaScript**: ES6+ features, async handling, error handling
- **Database**: SQL injection, performance optimization, index usage
- **API Design**: RESTful standards, error handling, versioning

### Constructive Feedback
- Prioritize serious functional errors
- Then address code quality issues
- Finally mention style and improvement suggestions
- Acknowledge good implementations

### Tool Usage
You can use these tools to assist in the review:
- Static code analysis tools
- Code formatting tools
- Test coverage tools
- Dependency checking tools
