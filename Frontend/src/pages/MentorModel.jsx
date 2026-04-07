import React, { useRef, useEffect, useMemo, useState } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function MentorModel({ isSpeaking, analyser, ...props }) {
  const group = useRef()
  const { nodes, materials, animations } = useGLTF('/models/julia.glb')
  const { actions } = useAnimations(animations, group)

  // Debugging: Log nodes structure on mount to confirm bone names
  useEffect(() => {
    if (nodes) {
       console.log("[MentorModel] Nodes loaded:", Object.keys(nodes));
    }
  }, [nodes])

  // ----------------------------
  // 1. BLINK LOGIC (Procedural)
  // ----------------------------
  const blinkRef = useRef(0)
  const nextBlinkRef = useRef(2) // Start first blink after 2s
  const blinkDurationRef = useRef(0.12) // How long eyes stay closed

  // ----------------------------
  // 2. LIP SYNC / VSYNC LOGIC
  // ----------------------------
  const frequencyData = useMemo(() => new Uint8Array(512), [])
  const influenceRef = useRef(0)
  const LIP_INTENSITY = 1.1; // Slightly higher for impact

  // ----------------------------
  // 3. IDLE / BREATHING LOGIC
  // ----------------------------
  const breathRef = useRef(0)

  useFrame((state) => {
    const t = state.clock.elapsedTime
    
    // --- 1. PROCEDURAL BLINKING ---
    let targetBlink = 0
    if (t > nextBlinkRef.current) {
       // Start blinking
       const blinkProgress = (t - nextBlinkRef.current) / blinkDurationRef.current
       if (blinkProgress <= 1.0) {
          // Sinusoidal blink for smooth closure/opening
          targetBlink = Math.sin(blinkProgress * Math.PI)
       } else {
          // Finished blink, schedule next one (random 2-6 seconds)
          nextBlinkRef.current = t + 2 + Math.random() * 4
       }
    }
    blinkRef.current = THREE.MathUtils.lerp(blinkRef.current, targetBlink, 0.4)

    // --- 2. ENHANCED LIP SYNC (VSync) ---
    let targetInfluence = 0
    if (isSpeaking) {
      if (analyser) {
        analyser.getByteFrequencyData(frequencyData)
        
        // Sum low-mid frequencies for better mouth impact
        let sum = 0
        const sampleSize = 25
        for (let i = 0; i < sampleSize; i++) {
            // Apply slight weight to lower frequencies
            sum += frequencyData[i] * (1.1 - i / sampleSize)
        }
        const average = sum / sampleSize
        
        // Map average (roughly 0-255) to 0.0-1.0 range
        targetInfluence = Math.min(1.2, (average / 35) * LIP_INTENSITY);
        
        // Safety: Micro-jitters while speaking to keep mouth "alive"
        if (targetInfluence < 0.15) {
          targetInfluence = (Math.abs(Math.sin(t * 15)) * 0.2) * LIP_INTENSITY
        }
      } else {
        // Fallback procedural movement if no analyser
        targetInfluence = (Math.abs(Math.sin(t * 12)) * 0.4) * LIP_INTENSITY
      }
    }
    
    // Smooth transition for lip sync
    influenceRef.current = THREE.MathUtils.lerp(influenceRef.current, targetInfluence, 0.6)

    // --- APPLY FACIAL MORPHS ---
    Object.values(nodes).forEach((node) => {
      if (node.morphTargetDictionary && node.morphTargetInfluences) {
        const dict = node.morphTargetDictionary
        const influence = node.morphTargetInfluences
        
        // Mouth targets: mapping to multiple if they exist for better "VSync" feel
        const mouthOpen = dict['mouthOpen'] ?? dict['jawOpen'] ?? dict['viseme_aa'] ?? dict['MouthOpen']
        const mouthStretch = dict['mouthStretch'] ?? dict['viseme_O'] ?? dict['MouthSmile']
        
        if (mouthOpen !== undefined) influence[mouthOpen] = influenceRef.current
        if (mouthStretch !== undefined) influence[mouthStretch] = influenceRef.current * 0.3

        // Blink targets
        const eyeL = dict['eyeBlinkLeft'] ?? dict['Blink_Left'] ?? dict['EyeBlink_L']
        const eyeR = dict['eyeBlinkRight'] ?? dict['Blink_Right'] ?? dict['EyeBlink_R']
        if (eyeL !== undefined) influence[eyeL] = blinkRef.current
        if (eyeR !== undefined) influence[eyeR] = blinkRef.current
      }
    })

    // --- 3. PROCEDURAL BODY MOVEMENT (NATURAL IDLE) ---
    // Subtle breathing cycle (chest/spine)
    const breathIntensity = isSpeaking ? 0.02 : 0.01
    const breathFreq = isSpeaking ? 1.5 : 0.8
    const breathY = Math.sin(t * breathFreq) * breathIntensity
    
    const bones = {
      head: nodes.Head,
      neck: nodes.Neck,
      spine: nodes.Spine,
      leftArm: nodes.LeftArm,
      rightArm: nodes.RightArm,
    }

    // Default target rotations
    let headX = -0.15, headY = 0.25, headZ = 0 // Tilted UP (X negative) and RIGHT (Y positive)
    let neckY = 0
    let spineX = breathY * 0.5

    // Idle swaying / Presence (Micro-movements)
    headX += Math.sin(t * 0.4) * 0.02
    headY += Math.cos(t * 0.3) * 0.03
    
    if (isSpeaking) {
      // More active head movement while speaking (HeadTTS style)
      headX += Math.sin(t * 3.0) * 0.05; // Emphasis nod
      headY += Math.sin(t * 1.8) * 0.1;  // Natural swaying
      neckY = Math.sin(t * 1.5) * 0.04;
    } else {
      // Natural idle sway
      headX += Math.sin(t * 0.6) * 0.01
      headY += Math.cos(t * 0.5) * 0.02
    }
    
    // Smoothly apply to bones
    const LERP_FACTOR = 0.06
    if (bones.head) {
      bones.head.rotation.x = THREE.MathUtils.lerp(bones.head.rotation.x, headX, LERP_FACTOR);
      bones.head.rotation.y = THREE.MathUtils.lerp(bones.head.rotation.y, headY, LERP_FACTOR);
    }
    if (bones.neck) {
      bones.neck.rotation.y = THREE.MathUtils.lerp(bones.neck.rotation.y, neckY, LERP_FACTOR);
    }
    if (bones.spine) {
      bones.spine.rotation.x = THREE.MathUtils.lerp(bones.spine.rotation.x, spineX, LERP_FACTOR);
    }

    // Arms in confirmed rest position
    const restZ = 0.7, restX = 1.2, restY = 0.15;
    if (bones.leftArm) {
      bones.leftArm.rotation.x = THREE.MathUtils.lerp(bones.leftArm.rotation.x, restX, LERP_FACTOR);
      bones.leftArm.rotation.y = THREE.MathUtils.lerp(bones.leftArm.rotation.y, restY, LERP_FACTOR);
      bones.leftArm.rotation.z = THREE.MathUtils.lerp(bones.leftArm.rotation.z, restZ, LERP_FACTOR);
    }
    if (bones.rightArm) {
      bones.rightArm.rotation.x = THREE.MathUtils.lerp(bones.rightArm.rotation.x, restX, LERP_FACTOR);
      bones.rightArm.rotation.y = THREE.MathUtils.lerp(bones.rightArm.rotation.y, -restY, LERP_FACTOR);
      bones.rightArm.rotation.z = THREE.MathUtils.lerp(bones.rightArm.rotation.z, -restZ, LERP_FACTOR);
    }
  })

  return (
    <group ref={group} {...props} dispose={null}>
      {/* Renders the skeleton and meshes exactly as they are in the GLB file */}
      {nodes.Hips && <primitive object={nodes.Hips} />}

      {Object.entries(nodes).map(([name, node]) => {
        if (node.isSkinnedMesh) {
          return (
            <skinnedMesh
              key={name}
              geometry={node.geometry}
              material={node.material}
              skeleton={node.skeleton}
              morphTargetDictionary={node.morphTargetDictionary}
              morphTargetInfluences={node.morphTargetInfluences}
              castShadow
              receiveShadow
            />
          )
        }
        return null;
      })}
    </group>
  )
}

useGLTF.preload('/models/julia.glb')