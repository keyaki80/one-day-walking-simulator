# Contributing to One Day Walking Simulator

Thank you for your interest in contributing to One Day Walking Simulator! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Operating system and version
   - Python version
   - pygame version
   - Steps to reproduce the issue
   - Expected vs actual behavior

### Suggesting Features

1. **Open an issue** with the "feature request" label
2. **Describe the feature** in detail
3. **Explain the use case** and why it would be beneficial
4. **Consider implementation** if you have ideas

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/one-day-walking-simulator.git
   cd one-day-walking-simulator
   ```
3. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

#### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes**
3. **Test your changes**
   ```bash
   python3 one_day.py
   ```
4. **Follow coding standards** (see below)

#### Coding Standards

- **Python Style**: Follow PEP 8
- **Comments**: Use clear, descriptive comments
- **Functions**: Keep functions focused and well-documented
- **Variables**: Use descriptive variable names
- **Constants**: Use UPPER_CASE for constants

#### Example Code Style

```python
def draw_window_frame_overlay(self, window_rect):
    """
    Draw window frame and cross as overlay - always on top.
    
    Args:
        window_rect (pygame.Rect): Rectangle defining window area
    """
    # Calculate frame thickness based on window scale
    frame_thickness = max(4, int(8 / max(self.window_scale, 0.3)))
    
    # Draw frame with adaptive thickness
    frame_color = (100, 80, 60)  # Brown window frame
    pygame.draw.rect(self.screen, frame_color, window_rect, frame_thickness)
```

#### Testing

- **Manual Testing**: Test your changes thoroughly
- **Edge Cases**: Consider different screen sizes, input values
- **Performance**: Ensure changes don't significantly impact performance

#### Submitting Changes

1. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```
2. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
3. **Create a Pull Request**
   - Use a clear, descriptive title
   - Describe what your changes do
   - Reference any related issues
   - Include screenshots if applicable

## 🎨 Areas for Contribution

### High Priority
- **Performance optimizations**
- **Cross-platform compatibility**
- **Accessibility improvements**
- **Bug fixes**

### Medium Priority
- **New visual effects**
- **Additional customization options**
- **Sound effects and music**
- **Save/load preferences**

### Low Priority
- **Additional themes**
- **Easter eggs**
- **Advanced graphics options**

## 🐛 Bug Reports

When reporting bugs, please include:

```
**Environment:**
- OS: [e.g., macOS 14.0, Windows 11, Ubuntu 22.04]
- Python: [e.g., 3.9.7]
- pygame: [e.g., 2.1.2]

**Steps to Reproduce:**
1. Launch the application
2. Click on input box
3. Type "30"
4. Press Enter
5. [Describe what happens]

**Expected Behavior:**
[What you expected to happen]

**Actual Behavior:**
[What actually happened]

**Screenshots:**
[If applicable, add screenshots]
```

## 📝 Documentation

- **Code comments**: Document complex logic
- **README updates**: Update README.md if you add features
- **Docstrings**: Use clear docstrings for functions and classes

## 🎯 Pull Request Guidelines

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] Changes have been tested manually
- [ ] Documentation has been updated if needed
- [ ] Commit messages are clear and descriptive

### Pull Request Template
```
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested on [OS]
- [ ] Manual testing completed
- [ ] No performance regression

## Screenshots
[If applicable]
```

## 🙏 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes for significant contributions
- GitHub contributors page

## 📞 Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing documentation
- Look at recent pull requests for examples

Thank you for contributing to One Day Walking Simulator! 🌊
