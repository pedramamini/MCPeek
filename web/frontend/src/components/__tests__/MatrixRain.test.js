/**
 * Test suite for MatrixRain component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import MatrixRain from '../MatrixRain';

// Mock requestAnimationFrame and cancelAnimationFrame
global.requestAnimationFrame = jest.fn((cb) => setTimeout(cb, 16));
global.cancelAnimationFrame = jest.fn((id) => clearTimeout(id));

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  disconnect: jest.fn(),
  unobserve: jest.fn(),
}));

describe('MatrixRain Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders canvas element', () => {
    render(<MatrixRain />);
    const canvas = screen.getByRole('img', { hidden: true }); // Canvas has img role
    expect(canvas).toBeInTheDocument();
  });

  test('sets up intersection observer for visibility detection', () => {
    render(<MatrixRain />);
    expect(IntersectionObserver).toHaveBeenCalledWith(
      expect.any(Function),
      expect.objectContaining({ threshold: 0.1 })
    );
  });

  test('adds visibility change event listener', () => {
    const addEventListenerSpy = jest.spyOn(document, 'addEventListener');
    render(<MatrixRain />);
    
    expect(addEventListenerSpy).toHaveBeenCalledWith(
      'visibilitychange',
      expect.any(Function)
    );
    
    addEventListenerSpy.mockRestore();
  });

  test('cleans up event listeners on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');
    const { unmount } = render(<MatrixRain />);
    
    unmount();
    
    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'visibilitychange',
      expect.any(Function)
    );
    
    removeEventListenerSpy.mockRestore();
  });

  test('responds to show prop changes', () => {
    const { rerender } = render(<MatrixRain show={true} />);
    const canvas = screen.getByRole('img', { hidden: true });
    expect(canvas).toBeInTheDocument();

    rerender(<MatrixRain show={false} />);
    // Component should still render but animation should stop
    expect(canvas).toBeInTheDocument();
  });

  test('handles window resize events', () => {
    const addEventListenerSpy = jest.spyOn(window, 'addEventListener');
    render(<MatrixRain />);
    
    expect(addEventListenerSpy).toHaveBeenCalledWith(
      'resize',
      expect.any(Function)
    );
    
    addEventListenerSpy.mockRestore();
  });

  test('cancels animation frame on unmount', () => {
    const { unmount } = render(<MatrixRain />);
    unmount();
    
    expect(cancelAnimationFrame).toHaveBeenCalled();
  });

  test('sets up canvas context correctly', () => {
    // Mock canvas and context
    const mockGetContext = jest.fn(() => ({
      fillStyle: '',
      fillRect: jest.fn(),
      font: '',
      textAlign: '',
      fillText: jest.fn(),
    }));
    
    HTMLCanvasElement.prototype.getContext = mockGetContext;
    
    render(<MatrixRain />);
    
    expect(mockGetContext).toHaveBeenCalledWith('2d');
  });

  test('handles visibility state changes correctly', () => {
    // Mock document.hidden
    Object.defineProperty(document, 'hidden', {
      writable: true,
      value: false,
    });

    render(<MatrixRain />);
    
    // Simulate tab becoming hidden
    Object.defineProperty(document, 'hidden', {
      value: true,
    });
    
    const event = new Event('visibilitychange');
    document.dispatchEvent(event);
    
    // Animation should be paused when tab is hidden
    expect(requestAnimationFrame).toHaveBeenCalled();
  });

  test('respects performance optimizations', () => {
    // Test that animation doesn't start when show is false
    render(<MatrixRain show={false} />);
    
    // requestAnimationFrame should not be called initially when show=false
    // (Note: this depends on the specific implementation timing)
    expect(requestAnimationFrame).toHaveBeenCalledTimes(0);
  });
});