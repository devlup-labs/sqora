// AI Mentor page component
// This is a simple page for the AI Mentor feature - will be expanded later
import React from 'react'
import Header from '../components/Header'
import './Page.css'

function AIMentor() {
  return (
    <div className="app">
      {/* Header component containing logo and authentication buttons */}
      <Header />
      
      {/* Main content area for AI Mentor page */}
      <main className="page-content">
        <div className="page-container">
          <h1 className="page-title">AI Mentor</h1>
          <p className="page-description">
            Welcome to AI Mentor. This page will be developed further.
          </p>
        </div>
      </main>
    </div>
  )
}


export default AIMentor



// import React, { useRef, useEffect } from 'react'
// import { useGLTF, useAnimations } from '@react-three/drei'

// export function MentorModel({ isSpeaking, ...props }) {
//   const group = useRef()
//   // Load your downloaded model
//   const { nodes, materials, animations } = useGLTF('/path-to-your-model.glb')
//   const { actions } = useAnimations(animations, group)

//   useEffect(() => {
//     // Play "Talking" animation when AI is responding, otherwise "Idle"
//     const actionName = isSpeaking ? 'TalkingAnimation' : 'IdleAnimation'
//     actions[actionName]?.reset().fadeIn(0.5).play()
//     return () => actions[actionName]?.fadeOut(0.5)
//   }, [isSpeaking])

//   return (
//     <group ref={group} {...props} dispose={null}>
//       <primitive object={nodes.Hips} />
//       <skinnedMesh 
//         geometry={nodes.Wolf3D_Body.geometry} 
//         material={materials.Wolf3D_Body} 
//         skeleton={nodes.Wolf3D_Body.skeleton} 
//       />
//       {/* Head mesh contains the Morph Targets for Lips */}
//       <skinnedMesh
//         name="Wolf3D_Head"
//         geometry={nodes.Wolf3D_Head.geometry}
//         material={materials.Wolf3D_Head}
//         skeleton={nodes.Wolf3D_Head.skeleton}
//         morphTargetDictionary={nodes.Wolf3D_Head.morphTargetDictionary}
//         morphTargetInfluences={nodes.Wolf3D_Head.morphTargetInfluences}
//       />
//     </group>
//   )
// }
