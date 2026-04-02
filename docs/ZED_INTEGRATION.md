# Zed Editor Integration

The Tailscale MCP Server has been optimized for use with the [Zed](https://zed.dev/) code editor, providing seamless network management capabilities directly within your development environment.

## FastMCP 3.1+ Features

This integration leverages FastMCP 3.1+ features:

- **Conversational Tool Responses**: Tools provide natural language summaries and contextual suggestions
- **Sampling with Tools**: Autonomous orchestration of complex network operations
- **Enhanced Error Handling**: User-friendly error messages with actionable guidance

## Setup

1. **Install Zed**: Download from [zed.dev](https://zed.dev/)

2. **Configure MCP Server**:
   ```json
   // .zed/settings.json
   {
     "mcp": {
       "servers": {
         "tailscale": {
           "command": "python",
           "args": ["-m", "tailscalemcp"],
           "env": {
             "TAILSCALE_API_KEY": "your-api-key",
             "TAILSCALE_TAILNET": "your-tailnet"
           },
           "timeout": 300
         }
       }
     }
   }
   ```

3. **Environment Variables**:
   - `TAILSCALE_API_KEY`: Your Tailscale API key
   - `TAILSCALE_TAILNET`: Your tailnet name

## Available Tools

### Conversational Tools

All tools now provide conversational responses with:
- **Natural summaries**: Human-readable status descriptions
- **Contextual suggestions**: Next steps based on current state
- **Actionable guidance**: Specific commands to try

#### Core Tools
- `get_tailnet_status` - Network overview with health insights
- `manage_tailnet_devices` - Device management with smart suggestions
- `configure_tailnet_network` - DNS and connectivity management
- `manage_tailnet_security` - Security scanning and compliance

#### Advanced Tools
- `configure_tailnet_funnel` - HTTPS tunnel management
- `manage_tailnet_files` - Secure file sharing via Taildrop
- `monitor_tailnet_activity` - Real-time metrics and alerting
- `run_agentic_tailnet_workflow` - SEP-1577 multi-step orchestration (sampling with tools)

### Sampling with Tools

Configure server-side LLM (`TAILSCALE_SAMPLING_BASE_URL`, `TAILSCALE_SAMPLING_MODEL`) or set
`TAILSCALE_SAMPLING_USE_CLIENT_LLM=1` for host sampling. Then use:

```python
run_agentic_tailnet_workflow(
    workflow_prompt="List offline devices and summarize likely causes.",
    available_tools=["manage_tailnet_devices", "get_tailnet_status"],
    max_iterations=5,
)
```

## Workflow Examples

### Network Troubleshooting
1. Ask: "What's the status of my Tailscale network?"
2. Get conversational response with suggestions
3. Follow automated diagnostic workflow

### Device Management
1. Query: "Show me all devices"
2. Receive summary with online/offline counts
3. Get suggestions for offline devices

### Security Audits
1. Command: "Run a security audit"
2. Autonomous multi-step security assessment
3. Receive prioritized recommendations

## Key Benefits

- **Integrated Development**: Network management without leaving Zed
- **Conversational AI**: Natural language responses and guidance
- **Autonomous Operations**: Complex workflows run automatically
- **Real-time Monitoring**: Live network status and alerts

## Best Practices

1. **Use Conversational Queries**: Ask questions naturally rather than using exact tool parameters
2. **Leverage Sampling**: For complex operations, use the sampling tool for autonomous execution
3. **Monitor Continuously**: Use status tools regularly to stay informed of network health
4. **Secure Credentials**: Store API keys securely using Zed's environment variable system

## Troubleshooting

- **Server Won't Start**: Check API credentials and network connectivity
- **Tools Not Available**: Verify MCP server is running in Zed settings
- **Timeout Errors**: Increase timeout value in configuration
- **Permission Issues**: Ensure API key has necessary permissions

## Support

For issues specific to Zed integration:
1. Check Zed's MCP server logs
2. Verify Tailscale MCP server can run independently
3. Test API credentials outside of Zed
4. Review Zed's MCP documentation