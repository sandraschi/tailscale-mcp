# How to View Mermaid Diagrams in Cursor

Cursor doesn't render Mermaid diagrams in the editor by default. Here are several ways to view them:

## Option 1: Online Mermaid Live Editor (Easiest)

1. Copy the Mermaid code from the diagram (everything between the ` ```mermaid` and ` ``` ` markers)
2. Go to https://mermaid.live/
3. Paste the code into the editor
4. See the rendered diagram instantly!

**Quick tip**: You can also use the Mermaid Live Editor API to create shareable links.

## Option 2: VS Code Markdown Preview (Cursor Compatible)

Since Cursor is based on VS Code, you can use VS Code extensions:

1. **Install Markdown Preview Mermaid Support extension**:
   - Open Extensions (Ctrl+Shift+X)
   - Search for "Markdown Preview Mermaid Support"
   - Install the extension
   - Restart Cursor

2. **View the diagram**:
   - Open the `.md` file with the Mermaid diagram
   - Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) to open Markdown preview
   - The diagram should render!

## Option 3: Use a Local Mermaid CLI Tool

Install Mermaid CLI to render diagrams locally:

```powershell
# Install via npm
npm install -g @mermaid-js/mermaid-cli

# Render a markdown file with Mermaid diagrams
mmdc -i docs\MERMAID_DIAGRAM_EXAMPLE.md -o docs\diagram.png

# Or render just the Mermaid code
mmdc -i diagram.mmd -o diagram.png
```

## Option 4: GitHub/GitLab Preview

1. Push your markdown file to GitHub or GitLab
2. View it in the web interface
3. GitHub and GitLab automatically render Mermaid diagrams!

## Option 5: Obsidian (If You Use It)

1. Open the markdown file in Obsidian
2. Obsidian has built-in Mermaid support
3. The diagram will render automatically

## Option 6: Create a Standalone HTML Viewer

Create a simple HTML file to view the diagram:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({startOnLoad:true});</script>
</head>
<body>
    <div class="mermaid">
graph TB
    %% Your Mermaid code here
    dev0["My-Laptop\n🟢 Online"]
    style dev0 fill:#90EE90
    </div>
</body>
</html>
```

Open the HTML file in a browser to see the rendered diagram.

## Recommended Workflow

For quick viewing while developing:
1. **Use Mermaid Live Editor** (https://mermaid.live/) - fastest for quick checks
2. **Install Markdown Preview extension** - best for integrated viewing in Cursor
3. **Use GitHub preview** - best for documentation and sharing

## Testing the Diagram

To test if your Mermaid diagram is valid:

1. Copy the Mermaid code from `MERMAID_DIAGRAM_EXAMPLE.md`
2. Paste it into https://mermaid.live/
3. If it renders correctly, the diagram syntax is valid!

## Quick Reference

- **Mermaid Live Editor**: https://mermaid.live/
- **Mermaid Documentation**: https://mermaid.js.org/
- **Mermaid CLI**: `npm install -g @mermaid-js/mermaid-cli`

---

**Last Updated**: 2025-11-24

