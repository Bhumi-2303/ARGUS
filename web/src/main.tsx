import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Guard for React 19 + @react-three/drei Html portal unmount race condition:
// When rapidly switching 3D scenes, drei's Html cleanup and React 19 commitDeletionEffects
// both attempt to unmount portal DOM containers. If the child is already detached,
// avoid throwing an unhandled NotFoundError DOMException.
if (typeof Node !== 'undefined' && Node.prototype) {
  const originalRemoveChild = Node.prototype.removeChild;
  Node.prototype.removeChild = function <T extends Node>(child: T): T {
    if (child.parentNode !== this) {
      return child;
    }
    return originalRemoveChild.call(this, child) as T;
  };
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
