# tailscale-mcp (MCPB Bundle)

FastMCP 3.2+ compliant Tailscale network controller with persistent storage

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "tailscale-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "tailscale_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **health**: health
- **api_status**: api_status
- **list_tools**: list_tools
- **call_tool**: call_tool
- **save_settings**: save_settings
- **test_credentials**: test_credentials
- **sampling_status**: sampling_status
- **llm_health**: llm_health
- **chat_completions**: chat_completions
- **log_status**: log_status
- **log_search**: log_search
- **log_export**: log_export
- **main_stdio**: main(stdio)
- **main_http**: main(http)
- **main_sse**: main(sse)
- **tailscale_agentic_workflow**: tailscale_agentic_workflow
- **tailscale_sampling**: tailscale_sampling

## Requirements

- Python 3.12+
- uv
