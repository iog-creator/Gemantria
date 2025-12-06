#!/bin/bash

# GitHub MCP Wrapper Script
# Provides GitHub operations via GitHub CLI for MCP integration

set -e

echo "🐙 Starting GitHub MCP Integration..."
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if GitHub CLI is available
check_dependencies() {
    print_status "Checking GitHub CLI..."

    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed. Please install it first:"
        echo "  Ubuntu/Debian: sudo apt install gh"
        echo "  macOS: brew install gh"
        echo "  Or download from: https://cli.github.com/"
        exit 1
    fi

    print_success "GitHub CLI found"

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        print_warning "GitHub CLI not authenticated. Run: gh auth login"
        print_warning "Continuing anyway - MCP server will handle authentication errors"
    else
        print_success "GitHub CLI authenticated"
    fi
}

# Check current repository context
check_repository() {
    print_status "Checking repository context..."

    if ! git rev-parse --git-dir &> /dev/null; then
        print_error "Not in a git repository"
        exit 1
    fi

    # Get repository info
    REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "unknown")
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

    print_success "Repository: $REPO_URL"
    print_success "Current branch: $CURRENT_BRANCH"
}

# Create MCP server response
create_mcp_response() {
    cat << EOF
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "github_pr_list",
        "description": "List pull requests with optional filtering",
        "inputSchema": {
          "type": "object",
          "properties": {
            "state": {
              "type": "string",
              "enum": ["open", "closed", "all"],
              "default": "open"
            },
            "limit": {
              "type": "number",
              "default": 10,
              "maximum": 100
            },
            "author": {
              "type": "string",
              "description": "Filter by author"
            }
          }
        }
      },
      {
        "name": "github_pr_view",
        "description": "View details of a specific pull request",
        "inputSchema": {
          "type": "object",
          "properties": {
            "number": {
              "type": "number",
              "description": "PR number"
            }
          },
          "required": ["number"]
        }
      },
      {
        "name": "github_pr_create",
        "description": "Create a new pull request",
        "inputSchema": {
          "type": "object",
          "properties": {
            "title": {
              "type": "string",
              "description": "PR title"
            },
            "body": {
              "type": "string",
              "description": "PR body/description"
            },
            "base": {
              "type": "string",
              "description": "Base branch",
              "default": "main"
            },
            "head": {
              "type": "string",
              "description": "Head branch"
            },
            "draft": {
              "type": "boolean",
              "default": false
            }
          },
          "required": ["title", "body"]
        }
      },
      {
        "name": "github_pr_merge",
        "description": "Merge a pull request",
        "inputSchema": {
          "type": "object",
          "properties": {
            "number": {
              "type": "number",
              "description": "PR number"
            },
            "method": {
              "type": "string",
              "enum": ["merge", "squash", "rebase"],
              "default": "squash"
            },
            "delete_branch": {
              "type": "boolean",
              "default": true
            }
          },
          "required": ["number"]
        }
      },
      {
        "name": "github_issue_list",
        "description": "List issues with optional filtering",
        "inputSchema": {
          "type": "object",
          "properties": {
            "state": {
              "type": "string",
              "enum": ["open", "closed", "all"],
              "default": "open"
            },
            "limit": {
              "type": "number",
              "default": 10,
              "maximum": 100
            },
            "author": {
              "type": "string",
              "description": "Filter by author"
            },
            "assignee": {
              "type": "string",
              "description": "Filter by assignee"
            }
          }
        }
      },
      {
        "name": "github_repo_info",
        "description": "Get repository information",
        "inputSchema": {
          "type": "object",
          "properties": {}
        }
      }
    ]
  }
}
EOF
}

# Handle MCP tool calls
handle_tool_call() {
    local method="$1"
    local params="$2"

    case "$method" in
        "tools/list")
            create_mcp_response
            ;;
        "tools/call")
            # Parse the tool name and arguments from params
            local tool_name=$(echo "$params" | jq -r '.name // empty')
            local tool_args=$(echo "$params" | jq -r '.arguments // "{}"')

            case "$tool_name" in
                "github_pr_list")
                    handle_pr_list "$tool_args"
                    ;;
                "github_pr_view")
                    handle_pr_view "$tool_args"
                    ;;
                "github_pr_create")
                    handle_pr_create "$tool_args"
                    ;;
                "github_pr_merge")
                    handle_pr_merge "$tool_args"
                    ;;
                "github_issue_list")
                    handle_issue_list "$tool_args"
                    ;;
                "github_repo_info")
                    handle_repo_info "$tool_args"
                    ;;
                *)
                    echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32601, \"message\": \"Method not found: $tool_name\"}}" >&2
                    ;;
            esac
            ;;
        *)
            echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32601, \"message\": \"Method not found\"}}" >&2
            ;;
    esac
}

# Tool handlers
handle_pr_list() {
    local args="$1"
    local state=$(echo "$args" | jq -r '.state // "open"')
    local limit=$(echo "$args" | jq -r '.limit // 10')
    local author=$(echo "$args" | jq -r '.author // empty')

    local cmd="gh pr list --state $state --limit $limit --json number,title,author,createdAt,updatedAt"
    if [ -n "$author" ]; then
        cmd="$cmd --author $author"
    fi

    local result=$(eval "$cmd" 2>/dev/null || echo "[]")
    echo "{\"jsonrpc\": \"2.0\", \"result\": $result}"
}

handle_pr_view() {
    local args="$1"
    local number=$(echo "$args" | jq -r '.number')

    if [ -z "$number" ] || [ "$number" = "null" ]; then
        echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32602, \"message\": \"Missing PR number\"}}" >&2
        return
    fi

    local result=$(gh pr view "$number" --json number,title,body,author,createdAt,updatedAt,state,mergeable,reviewDecision 2>/dev/null || echo "{}")
    echo "{\"jsonrpc\": \"2.0\", \"result\": $result}"
}

handle_pr_create() {
    local args="$1"
    local title=$(echo "$args" | jq -r '.title')
    local body=$(echo "$args" | jq -r '.body')
    local base=$(echo "$args" | jq -r '.base // "main"')
    local head=$(echo "$args" | jq -r '.head // empty')
    local draft=$(echo "$args" | jq -r '.draft // false')

    if [ -z "$title" ] || [ "$title" = "null" ]; then
        echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32602, \"message\": \"Missing PR title\"}}" >&2
        return
    fi

    if [ -z "$body" ] || [ "$body" = "null" ]; then
        echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32602, \"message\": \"Missing PR body\"}}" >&2
        return
    fi

    local cmd="gh pr create --title \"$title\" --body \"$body\" --base $base"
    if [ -n "$head" ] && [ "$head" != "null" ]; then
        cmd="$cmd --head $head"
    fi
    if [ "$draft" = "true" ]; then
        cmd="$cmd --draft"
    fi

    local result=$(eval "$cmd" 2>&1)
    if [ $? -eq 0 ]; then
        # Extract PR number from output
        local pr_url=$(echo "$result" | grep -E "https://github.com/[^/]+/[^/]+/pull/[0-9]+" | head -1)
        if [ -n "$pr_url" ]; then
            local pr_number=$(echo "$pr_url" | grep -oE "[0-9]+$")
            echo "{\"jsonrpc\": \"2.0\", \"result\": {\"url\": \"$pr_url\", \"number\": $pr_number, \"success\": true}}"
        else
            echo "{\"jsonrpc\": \"2.0\", \"result\": {\"output\": \"$result\", \"success\": true}}"
        fi
    else
        echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32000, \"message\": \"$result\"}}" >&2
    fi
}

handle_pr_merge() {
    local args="$1"
    local number=$(echo "$args" | jq -r '.number')
    local method=$(echo "$args" | jq -r '.method // "squash"')
    local delete_branch=$(echo "$args" | jq -r '.delete_branch // true')

    if [ -z "$number" ] || [ "$number" = "null" ]; then
        echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32602, \"message\": \"Missing PR number\"}}" >&2
        return
    fi

    local cmd="gh pr merge $number --$method"
    if [ "$delete_branch" = "true" ]; then
        cmd="$cmd --delete-branch"
    fi

    local result=$(eval "$cmd" 2>&1)
    if [ $? -eq 0 ]; then
        echo "{\"jsonrpc\": \"2.0\", \"result\": {\"success\": true, \"output\": \"$result\"}}"
    else
        echo "{\"jsonrpc\": \"2.0\", \"error\": {\"code\": -32000, \"message\": \"$result\"}}" >&2
    fi
}

handle_issue_list() {
    local args="$1"
    local state=$(echo "$args" | jq -r '.state // "open"')
    local limit=$(echo "$args" | jq -r '.limit // 10')
    local author=$(echo "$args" | jq -r '.author // empty')
    local assignee=$(echo "$args" | jq -r '.assignee // empty')

    local cmd="gh issue list --state $state --limit $limit --json number,title,author,createdAt,updatedAt"
    if [ -n "$author" ]; then
        cmd="$cmd --author $author"
    fi
    if [ -n "$assignee" ]; then
        cmd="$cmd --assignee $assignee"
    fi

    local result=$(eval "$cmd" 2>/dev/null || echo "[]")
    echo "{\"jsonrpc\": \"2.0\", \"result\": $result}"
}

handle_repo_info() {
    local result=$(gh repo view --json name,description,owner,isPrivate,createdAt,updatedAt,pushedAt 2>/dev/null || echo "{}")
    echo "{\"jsonrpc\": \"2.0\", \"result\": $result}"
}

# Display connection information
show_connection_info() {
    echo ""
    echo "🐙 GitHub MCP Integration Started!"
    echo "=================================="
    echo ""
    echo "🔧 Available Tools:"
    echo "  • github_pr_list - List pull requests"
    echo "  • github_pr_view - View PR details"
    echo "  • github_pr_create - Create new PR"
    echo "  • github_pr_merge - Merge PR"
    echo "  • github_issue_list - List issues"
    echo "  • github_repo_info - Get repo info"
    echo ""
    echo "📋 Usage in Cursor:"
    echo "  Use GitHub operations through MCP tools"
    echo ""
    echo "🛑 To stop: Ctrl+C"
}

# Main MCP server loop
main() {
    check_dependencies
    check_repository
    show_connection_info

    print_status "Starting MCP server (stdio mode)..."

    # Read from stdin, write to stdout (stdio mode)
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            # Parse the JSON-RPC request
            local method=$(echo "$line" | jq -r '.method // empty' 2>/dev/null)
            local params=$(echo "$line" | jq -r '.params // "{}"' 2>/dev/null)
            local id=$(echo "$line" | jq -r '.id // null' 2>/dev/null)

            if [ -n "$method" ]; then
                handle_tool_call "$method" "$params"
            fi
        fi
    done
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}Shutting down GitHub MCP...${NC}"; exit 0' INT TERM

# Run main function
main

