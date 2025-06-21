import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';

const CanvasContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
  opacity: ${props => props.show ? 0.1 : 0};
  transition: opacity 0.5s ease;
`;

const Canvas = styled.canvas`
  width: 100%;
  height: 100%;
`;

const MatrixRain = ({ show = true }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const [isVisible, setIsVisible] = useState(true);
  const [isTabActive, setIsTabActive] = useState(true);
  
  useEffect(() => {
    // Visibility change detection
    const handleVisibilityChange = () => {
      setIsTabActive(!document.hidden);
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Intersection observer for component visibility
    let observer;
    if (canvasRef.current) {
      observer = new IntersectionObserver(
        ([entry]) => {
          setIsVisible(entry.isIntersecting);
        },
        { threshold: 0.1 }
      );
      observer.observe(canvasRef.current);
    }
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (observer) observer.disconnect();
    };
  }, []);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    // Don't animate if not visible or tab not active
    if (!show || !isVisible || !isTabActive) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
      return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Matrix characters - mix of numbers, letters, and special chars
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン';
    const charArray = chars.split('');
    
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = [];
    
    // Initialize drops
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100; // Start above screen
    }
    
    const draw = () => {
      // Semi-transparent black to create trailing effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#00ff00';
      ctx.font = `${fontSize}px 'Fira Code', monospace`;
      ctx.textAlign = 'center';
      
      for (let i = 0; i < drops.length; i++) {
        // Random character
        const char = charArray[Math.floor(Math.random() * charArray.length)];
        
        // Draw character
        const x = i * fontSize + fontSize / 2;
        const y = drops[i] * fontSize;
        
        // Vary the green color
        const alpha = Math.random() * 0.8 + 0.2;
        ctx.fillStyle = `rgba(0, 255, 0, ${alpha})`;
        ctx.fillText(char, x, y);
        
        // Move drop down
        drops[i]++;
        
        // Reset drop to top randomly
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
      }
    };
    
    const animate = () => {
      // Check if still should animate
      if (!show || !isVisible || !isTabActive) {
        animationRef.current = null;
        return;
      }
      
      draw();
      animationRef.current = requestAnimationFrame(animate);
    };
    
    // Only start animation if visible
    if (show && isVisible && isTabActive) {
      animate();
    }
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [show, isVisible, isTabActive]);
  
  return (
    <CanvasContainer show={show}>
      <Canvas ref={canvasRef} />
    </CanvasContainer>
  );
};

export default MatrixRain;