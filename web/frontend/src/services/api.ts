import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request/Response interfaces
export interface MCPEndpoint {
  url: string
  api_key?: string
  auth_header?: string
}

export interface CommandResult {
  success: boolean
  data?: any
  error?: string
  execution_time?: number
}

export interface DiscoverRequest {
  endpoint: MCPEndpoint
  verbosity: number
}

export interface ToolRequest {
  endpoint: MCPEndpoint
  tool_name: string
  parameters?: Record<string, any>
}

export interface ResourceRequest {
  endpoint: MCPEndpoint
  uri: string
}

export interface PromptRequest {
  endpoint: MCPEndpoint
  name: string
  arguments?: Record<string, any>
}

// API Functions
export const healthCheck = async (): Promise<CommandResult> => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check failed:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Health check failed'
    }
  }
}

export const discoverEndpoint = async (request: DiscoverRequest): Promise<CommandResult> => {
  try {
    const response = await api.post('/discover', request)
    return response.data
  } catch (error) {
    console.error('Discover failed:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Discovery failed'
    }
  }
}

export const executeTool = async (request: ToolRequest): Promise<CommandResult> => {
  try {
    const response = await api.post('/tool', request)
    return response.data
  } catch (error) {
    console.error('Tool execution failed:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Tool execution failed'
    }
  }
}

export const readResource = async (request: ResourceRequest): Promise<CommandResult> => {
  try {
    const response = await api.post('/resource', request)
    return response.data
  } catch (error) {
    console.error('Resource read failed:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Resource read failed'
    }
  }
}

export const getPrompt = async (request: PromptRequest): Promise<CommandResult> => {
  try {
    const response = await api.post('/prompt', request)
    return response.data
  } catch (error) {
    console.error('Prompt request failed:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Prompt request failed'
    }
  }
}

export const clearSessions = async (): Promise<CommandResult> => {
  try {
    const response = await api.delete('/sessions')
    return response.data
  } catch (error) {
    console.error('Clear sessions failed:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Clear sessions failed'
    }
  }
}

// Main command executor
export const executeCommand = async (
  command: string, 
  options: {
    endpoint: MCPEndpoint
    args: string[]
  }
): Promise<CommandResult> => {
  const { endpoint, args } = options

  switch (command) {
    case 'discover':
      const verbosity = args.includes('-vvv') ? 3 : args.includes('-vv') ? 2 : args.includes('-v') ? 2 : 1
      return await discoverEndpoint({ endpoint, verbosity })
    
    case 'tool':
      const toolName = args[0]
      let toolParams = {}
      if (args[1]) {
        try {
          toolParams = JSON.parse(args[1])
        } catch (error) {
          return {
            success: false,
            error: 'Invalid JSON parameters for tool command'
          }
        }
      }
      return await executeTool({ endpoint, tool_name: toolName, parameters: toolParams })
    
    case 'resource':
      return await readResource({ endpoint, uri: args[0] })
    
    case 'prompt':
      const promptName = args[0]
      let promptArgs = {}
      if (args[1]) {
        try {
          promptArgs = JSON.parse(args[1])
        } catch (error) {
          return {
            success: false,
            error: 'Invalid JSON arguments for prompt command'
          }
        }
      }
      return await getPrompt({ endpoint, name: promptName, arguments: promptArgs })
    
    default:
      return {
        success: false,
        error: `Unknown command: ${command}`
      }
  }
}

// Utility function to test API connection
export const testConnection = async (): Promise<boolean> => {
  try {
    const result = await healthCheck()
    return result.success
  } catch {
    return false
  }
}