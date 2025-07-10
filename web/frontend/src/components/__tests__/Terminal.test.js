/**
 * Test suite for Terminal component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import Terminal from '../Terminal';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('Terminal Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders terminal with welcome message', () => {
    render(<Terminal />);
    
    expect(screen.getByText(/Welcome to MCPeek Web Terminal/)).toBeInTheDocument();
    expect(screen.getByText(/Type "help" for available commands/)).toBeInTheDocument();
  });

  test('displays help command correctly', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    fireEvent.change(input, { target: { value: 'help' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText(/Available commands:/)).toBeInTheDocument();
      expect(screen.getByText(/discover/)).toBeInTheDocument();
      expect(screen.getByText(/tool/)).toBeInTheDocument();
    });
  });

  test('handles endpoint setting correctly', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    fireEvent.change(input, { target: { value: 'endpoint http://test.com' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText(/Endpoint set to: http:\/\/test.com/)).toBeInTheDocument();
    });
  });

  test('handles API key setting with masking', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    fireEvent.change(input, { target: { value: 'auth test-api-key-123' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText(/API key set/)).toBeInTheDocument();
    });

    // Check status shows masked key
    fireEvent.change(input, { target: { value: 'status' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText(/API Key: \*\*\*set\*\*\*/)).toBeInTheDocument();
    });
  });

  test('validates JSON parameters in tool command', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    
    // Set endpoint first
    fireEvent.change(input, { target: { value: 'endpoint http://test.com' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    // Try invalid JSON
    fireEvent.change(input, { target: { value: 'tool test_tool {invalid json}' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText(/Error: Invalid JSON parameters/)).toBeInTheDocument();
    });
  });

  test('makes proper API calls with headers', async () => {
    const mockResponse = {
      data: {
        success: true,
        data: { tools: [], resources: [] }
      }
    };
    mockedAxios.post.mockResolvedValue(mockResponse);

    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    
    // Set endpoint and auth
    fireEvent.change(input, { target: { value: 'endpoint http://test.com' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    fireEvent.change(input, { target: { value: 'auth test-key' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    // Make discover call
    fireEvent.change(input, { target: { value: 'discover' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/discover',
        expect.objectContaining({
          endpoint: 'http://test.com',
          verbosity: 0,
          tool_tickle: false
        }),
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-API-Key': 'test-key'
          })
        })
      );
    });
  });

  test('handles API errors gracefully', async () => {
    const mockError = {
      response: {
        data: {
          success: false,
          error: 'Connection failed'
        }
      }
    };
    mockedAxios.post.mockRejectedValue(mockError);

    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    
    // Set endpoint
    fireEvent.change(input, { target: { value: 'endpoint http://test.com' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    // Try discover command
    fireEvent.change(input, { target: { value: 'discover' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText(/Network error:/)).toBeInTheDocument();
    });
  });

  test('supports command history navigation', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    
    // Enter a few commands
    fireEvent.change(input, { target: { value: 'help' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    
    fireEvent.change(input, { target: { value: 'status' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    // Navigate history with arrow keys
    fireEvent.keyDown(input, { key: 'ArrowUp', code: 'ArrowUp' });
    expect(input.value).toBe('status');

    fireEvent.keyDown(input, { key: 'ArrowUp', code: 'ArrowUp' });
    expect(input.value).toBe('help');
  });

  test('provides command autocomplete suggestions', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    
    // Type partial command
    fireEvent.change(input, { target: { value: 'dis' } });

    await waitFor(() => {
      expect(screen.getByText(/discover/)).toBeInTheDocument();
    });
  });

  test('clears terminal on clear command', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    
    // Enter clear command
    fireEvent.change(input, { target: { value: 'clear' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    // Welcome message should be gone
    await waitFor(() => {
      expect(screen.queryByText(/Welcome to MCPeek Web Terminal/)).not.toBeInTheDocument();
    });
  });

  test('validates tool execution parameters', async () => {
    render(<Terminal />);
    
    const input = screen.getByPlaceholderText(/Enter command/);
    
    // Set endpoint
    fireEvent.change(input, { target: { value: 'endpoint http://test.com' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    // Try tool without name
    fireEvent.change(input, { target: { value: 'tool' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText(/Usage: tool <tool_name>/)).toBeInTheDocument();
    });
  });
});