import React, { useEffect, useRef } from 'react'
import styled from 'styled-components'

const CanvasContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
  pointer-events: none;
`

const Canvas = styled.canvas`
  display: block;
  width: 100%;
  height: 100%;
`

const MatrixRain: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Matrix characters (mix of ASCII and Japanese)
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()_+-=[]{}|;:,.<>?ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ'
    const fontSize = 14
    const columns = Math.floor(canvas.width / fontSize)

    // Array to store drop positions
    const drops: number[] = Array(columns).fill(0)

    // Initialize drops at random positions
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.floor(Math.random() * canvas.height / fontSize)
    }

    const draw = () => {
      // Create fade effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Set text properties
      ctx.font = `${fontSize}px Fira Code, monospace`
      ctx.textAlign = 'left'

      // Draw characters
      for (let i = 0; i < drops.length; i++) {
        // Pick random character
        const char = chars[Math.floor(Math.random() * chars.length)]
        
        // Set color with slight variations
        const intensity = Math.random()
        if (intensity > 0.98) {
          // Bright flash
          ctx.fillStyle = '#ffffff'
        } else if (intensity > 0.95) {
          // Bright green
          ctx.fillStyle = '#00ff00'
        } else if (intensity > 0.8) {
          // Normal green
          ctx.fillStyle = '#00dd00'
        } else {
          // Dim green
          ctx.fillStyle = '#008800'
        }

        // Draw character
        const x = i * fontSize
        const y = drops[i] * fontSize
        ctx.fillText(char, x, y)

        // Reset drop to top randomly
        if (y > canvas.height && Math.random() > 0.975) {
          drops[i] = 0
        }

        // Move drop down
        drops[i]++
      }
    }

    // Animation loop
    const interval = setInterval(draw, 50)

    return () => {
      clearInterval(interval)
      window.removeEventListener('resize', resizeCanvas)
    }
  }, [])

  return (
    <CanvasContainer>
      <Canvas ref={canvasRef} />
    </CanvasContainer>
  )
}

export default MatrixRain