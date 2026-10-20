package mcpclient

import (
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func translateResult(res *mcp.CallToolResult, maxTextBytes, maxArtifacts int) Result {
	if res == nil {
		return Result{}
	}
	var out Result
	var textParts []string

	for _, content := range res.Content {
		switch value := content.(type) {
		case *mcp.TextContent:
			textParts = append(textParts, value.Text)
		case *mcp.ImageContent:
			if len(out.Files) < maxArtifacts {
				out.Files = append(out.Files, Artifact{
					Kind:     "image",
					MIMEType: value.MIMEType,
					Data:     append([]byte(nil), value.Data...),
				})
			} else {
				out.Truncated = true
			}
		case *mcp.AudioContent:
			if len(out.Files) < maxArtifacts {
				out.Files = append(out.Files, Artifact{
					Kind:     "audio",
					MIMEType: value.MIMEType,
					Data:     append([]byte(nil), value.Data...),
				})
			} else {
				out.Truncated = true
			}
		default:
			// Unsupported MCP content is deliberately ignored. The bridge only
			// forwards explicitly understood content classes.
		}
	}

	out.Text = strings.Join(textParts, "\n")
	if maxTextBytes >= 0 && len(out.Text) > maxTextBytes {
		out.Text = safeBytePrefix(out.Text, maxTextBytes)
		out.Truncated = true
	}
	return out
}

func safeBytePrefix(value string, limit int) string {
	if limit <= 0 {
		return ""
	}
	if len(value) <= limit {
		return value
	}
	end := limit
	for end > 0 && (value[end]&0xC0) == 0x80 {
		end--
	}
	return value[:end]
}
