import React, { useEffect, useRef } from 'react'
import styled from 'styled-components'

const MatrixContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
`

const MatrixCanvas = styled.canvas`
  width: 100%;
  height: 100%;
  opacity: 0.15;
`

interface MatrixRainProps {
  intensity?: number
  speed?: number
}

const MatrixRain: React.FC<MatrixRainProps> = ({ 
  intensity = 0.8, 
  speed = 50 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Set canvas size
    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)
    
    // Matrix characters (mix of Japanese katakana, hiragana, and some ASCII)
    const matrixChars = [
      'ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ',
      'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト',
      'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
      'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', 'ユ', 'ヨ', 'ラ', 'リ',
      'ル', 'レ', 'ロ', 'ワ', 'ヲ', 'ン',
      'あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ',
      'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と',
      'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ',
      'ま', 'み', 'む', 'め', 'も', 'や', 'ゆ', 'よ', 'ら', 'り',
      'る', 'れ', 'ろ', 'わ', 'を', 'ん',
      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
      'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
      'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
      'U', 'V', 'W', 'X', 'Y', 'Z'
    ]
    
    const fontSize = 14
    const columns = Math.floor(canvas.width / fontSize)
    
    // Array to track the y position of each column
    const drops: number[] = []
    
    // Initialize drops
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100 // Start at random positions above the screen
    }
    
    let lastTime = 0
    
    const draw = (currentTime: number) => {
      // Control animation speed
      if (currentTime - lastTime < speed) {
        animationRef.current = requestAnimationFrame(draw)
        return
      }
      lastTime = currentTime
      
      // Create trailing effect by filling with semi-transparent black
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      ctx.font = `${fontSize}px 'Fira Code', monospace`
      
      // Draw the characters
      for (let i = 0; i < drops.length; i++) {
        // Random green color variations
        const greenIntensity = Math.random()
        if (greenIntensity > 0.95) {
          // Bright flash
          ctx.fillStyle = '#ffffff'
          ctx.shadowColor = '#ffffff'
          ctx.shadowBlur = 10
        } else if (greenIntensity > 0.8) {
          // Bright green
          ctx.fillStyle = '#00ff00'
          ctx.shadowColor = '#00ff00'
          ctx.shadowBlur = 5
        } else if (greenIntensity > 0.6) {
          // Medium green
          ctx.fillStyle = '#00cc00'
          ctx.shadowColor = '#00cc00'
          ctx.shadowBlur = 2
        } else {
          // Dark green
          ctx.fillStyle = '#008800'
          ctx.shadowColor = '#008800'
          ctx.shadowBlur = 0
        }
        
        // Pick a random character
        const char = matrixChars[Math.floor(Math.random() * matrixChars.length)]
        
        // Draw the character
        ctx.fillText(char, i * fontSize, drops[i] * fontSize)
        
        // Reset shadow
        ctx.shadowBlur = 0
        
        // Randomly reset the drop to the top
        if (drops[i] * fontSize > canvas.height && Math.random() > 1 - intensity) {
          drops[i] = 0
        }
        
        // Move the drop down
        drops[i]++
      }
      
      animationRef.current = requestAnimationFrame(draw)
    }
    
    // Start the animation
    animationRef.current = requestAnimationFrame(draw)
    
    return () => {
      window.removeEventListener('resize', resize)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [intensity, speed])
  
  return (
    <MatrixContainer>
      <MatrixCanvas ref={canvasRef} />
    </MatrixContainer>
  )
}

export default MatrixRain