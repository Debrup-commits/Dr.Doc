# Documentation System

This directory contains the markdown documentation files for the ASI:One platform. The documentation is organized into categories and sections, and is rendered dynamically in the frontend.

## Structure

```
docs/
├── overview.md              # ASI:One platform overview
├── quickstart.md            # Developer quickstart guide
├── models.md                # Model selection guide
├── tool-calling.md          # Tool calling documentation
├── agent-chat-protocol.md   # Agent chat protocol specification
└── README.md               # This file
```

## How It Works

1. **Markdown Files**: Documentation content is stored as markdown files in the `docs/` directory
2. **Data Structure**: The `src/lib/docs.ts` file defines the documentation structure and imports content
3. **Dynamic Rendering**: The frontend uses a `MarkdownRenderer` component to parse and display markdown
4. **Dynamic Routing**: Documentation sections are accessible via dynamic routes like `/documentation/[category]/[section]`

## Adding New Documentation

### 1. Create Markdown File

Create a new markdown file in the `docs/` directory:

```markdown
# Your Documentation Title

Your content here with **markdown** formatting.

## Code Examples

```python
def example_function():
    return "Hello, World!"
```

### Lists

- Item 1
- Item 2
- Item 3
```

### 2. Update Documentation Structure

Add your new section to `src/lib/docs.ts`:

```typescript
{
  id: 'your-section',
  title: 'Your Section Title',
  order: 4,
  content: `# Your Documentation Title

Your content here with **markdown** formatting.

## Code Examples

\`\`\`python
def example_function():
    return "Hello, World!"
\`\`\`

### Lists

- Item 1
- Item 2
- Item 3`
}
```

### 3. Add to Category

Add your section to the appropriate category in the `documentation` array:

```typescript
{
  id: 'your-category',
  title: 'Your Category',
  order: 3,
  sections: [
    // ... existing sections
    {
      id: 'your-section',
      title: 'Your Section Title',
      order: 4,
      content: `...`
    }
  ]
}
```

## Markdown Features

The `MarkdownRenderer` component supports:

- **Headers**: `#`, `##`, `###`
- **Bold**: `**text**`
- **Italic**: `*text*`
- **Code blocks**: ````code````
- **Inline code**: `` `code` ``
- **Lists**: `- item` or `* item`
- **Links**: `[text](url)`
- **Line breaks**: Automatic paragraph breaks

## Styling

The markdown content is styled using Tailwind CSS classes:

- Headers use appropriate font sizes and colors
- Code blocks have dark backgrounds with syntax highlighting
- Links are styled with blue colors and hover effects
- Lists have proper spacing and indentation

## Dynamic Routing

Documentation sections are accessible via:

- `/documentation` - Main documentation page
- `/documentation/[category]` - Redirects to first section of category
- `/documentation/[category]/[section]` - Specific documentation section

## Best Practices

1. **Keep content focused**: Each section should cover a specific topic
2. **Use clear headings**: Structure content with proper heading hierarchy
3. **Include examples**: Provide code examples and practical use cases
4. **Test rendering**: Verify that markdown renders correctly in the frontend
5. **Update structure**: Keep the documentation structure in `docs.ts` synchronized

## Content Guidelines

- Use clear, concise language
- Include practical examples
- Provide step-by-step instructions
- Use consistent formatting
- Include relevant links and references
- Keep content up-to-date with API changes

## Maintenance

- Regularly review and update documentation
- Test all code examples
- Verify links and references
- Update the documentation structure when adding new content
- Ensure markdown syntax is correct and consistent
