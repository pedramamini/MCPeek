import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';

const CanvasContainer = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
  pointer-events: none;
`;

const MatrixCanvas = styled.canvas`
  display: block;
  width: 100%;
  height: 100%;
  opacity: 0.15; // Very subtle background effect
`;

interface Drop {
  x: number;
  y: number;
  speed: number;
  opacity: number;
  char: string;
}

const MatrixRain: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drops, setDrops] = useState<Drop[]>([]);
  const animationRef = useRef<number>();

  // Matrix characters (mix of letters, numbers, and some Japanese characters for authenticity)
  const matrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン01';

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initialize drops
    const initDrops = () => {
      const columns = Math.floor(canvas.width / 20); // 20px wide columns
      const newDrops: Drop[] = [];

      for (let i = 0; i < columns; i++) {
        // Randomly start some drops at different positions
        if (Math.random() > 0.7) {
          newDrops.push({
            x: i * 20,
            y: Math.random() * canvas.height,
            speed: Math.random() * 3 + 1,
            opacity: Math.random() * 0.8 + 0.2,
            char: matrixChars[Math.floor(Math.random() * matrixChars.length)]
          });
        }
      }

      setDrops(newDrops);
    };

    initDrops();

    const animate = () => {
      // Clear canvas with fade effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update and draw drops
      setDrops(prevDrops => {
        const updatedDrops = prevDrops.map(drop => {
          // Move drop down
          const newY = drop.y + drop.speed;
          
          // Reset drop if it goes off screen
          if (newY > canvas.height + 20) {
            return {
              ...drop,
              y: -20,
              char: matrixChars[Math.floor(Math.random() * matrixChars.length)],
              opacity: Math.random() * 0.8 + 0.2,
              speed: Math.random() * 3 + 1
            };
          }

          // Occasionally change character
          if (Math.random() > 0.98) {
            return {
              ...drop,
              y: newY,
              char: matrixChars[Math.floor(Math.random() * matrixChars.length)]
            };
          }

          return { ...drop, y: newY };
        });

        // Add new drops occasionally
        if (Math.random() > 0.95) {
          const columns = Math.floor(canvas.width / 20);
          const randomColumn = Math.floor(Math.random() * columns);
          const existingDropInColumn = updatedDrops.find(drop => 
            Math.abs(drop.x - randomColumn * 20) < 10 && drop.y < 50
          );

          if (!existingDropInColumn) {
            updatedDrops.push({
              x: randomColumn * 20,
              y: -20,
              speed: Math.random() * 3 + 1,
              opacity: Math.random() * 0.8 + 0.2,
              char: matrixChars[Math.floor(Math.random() * matrixChars.length)]
            });
          }
        }

        // Draw all drops
        updatedDrops.forEach(drop => {
          ctx.font = '15px Fira Code, monospace';
          ctx.fillStyle = `rgba(0, 255, 0, ${drop.opacity})`;
          ctx.fillText(drop.char, drop.x, drop.y);

          // Draw trail effect
          for (let i = 1; i <= 5; i++) {
            const trailOpacity = drop.opacity * (0.8 - i * 0.15);
            if (trailOpacity > 0.1) {
              ctx.fillStyle = `rgba(0, 255, 0, ${trailOpacity})`;
              ctx.fillText(drop.char, drop.x, drop.y - i * 20);
            }
          }
        });

        return updatedDrops;
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <CanvasContainer>
      <MatrixCanvas ref={canvasRef} />
    </CanvasContainer>
  );
};

export default MatrixRain;