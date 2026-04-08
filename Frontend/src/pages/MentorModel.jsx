import React, { useRef, useEffect, useMemo } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

// HeadTTS viseme names → mouth morph target weights
// Kokoro viseme set: 'aa','E','I','O','U','PP','SS','TH','CH','FF','kk','nn','RR','DD','sil'
// We map each to { mouthOpen, mouthStretch } target weights
const VISEME_MAP = {
  'aa':  { mouthOpen: 0.9, mouthStretch: 0.1 },  // father
  'E':   { mouthOpen: 0.5, mouthStretch: 0.7 },  // bed
  'I':   { mouthOpen: 0.3, mouthStretch: 0.6 },  // bit
  'O':   { mouthOpen: 0.7, mouthStretch: 0.2 },  // hot
  'U':   { mouthOpen: 0.4, mouthStretch: 0.0 },  // boot (rounded)
  'PP':  { mouthOpen: 0.0, mouthStretch: 0.0 },  // p/b/m (lips closed)
  'SS':  { mouthOpen: 0.1, mouthStretch: 0.5 },  // s/z
  'TH':  { mouthOpen: 0.2, mouthStretch: 0.3 },  // th
  'CH':  { mouthOpen: 0.2, mouthStretch: 0.4 },  // sh/ch/j
  'FF':  { mouthOpen: 0.1, mouthStretch: 0.2 },  // f/v
  'kk':  { mouthOpen: 0.3, mouthStretch: 0.0 },  // k/g
  'nn':  { mouthOpen: 0.1, mouthStretch: 0.1 },  // n/l
  'RR':  { mouthOpen: 0.4, mouthStretch: 0.1 },  // r
  'DD':  { mouthOpen: 0.2, mouthStretch: 0.0 },  // d/t
  'sil': { mouthOpen: 0.0, mouthStretch: 0.0 },  // silence
}

export function MentorModel({ isSpeaking, visemeSchedule, ...props }) {
  const group = useRef()
  const { nodes, materials, animations } = useGLTF('/models/julia.glb')
  const { actions } = useAnimations(animations, group)

  useEffect(() => {
    if (nodes) {
      console.log('[MentorModel] Nodes loaded:', Object.keys(nodes))
    }
  }, [nodes])

  // ── 1. BLINK ──────────────────────────────────────────────────────────
  const blinkRef = useRef(0)
  const nextBlinkRef = useRef(2)
  const blinkDurationRef = useRef(0.12)

  // ── 2. VISEME LIP SYNC ────────────────────────────────────────────────
  // Current target mouth weights (driven by HeadTTS viseme schedule)
  const targetMouthRef = useRef({ mouthOpen: 0, mouthStretch: 0 })
  const smoothMouthRef = useRef({ mouthOpen: 0, mouthStretch: 0 })
  // AudioContext start time — used for scheduling visemes against clock
  const ttsStartRef = useRef(null)

  // When a new viseme schedule arrives, record the playback start time
  useEffect(() => {
    if (visemeSchedule && visemeSchedule.length > 0) {
      ttsStartRef.current = performance.now() / 1000  // seconds
    } else {
      ttsStartRef.current = null
      targetMouthRef.current = { mouthOpen: 0, mouthStretch: 0 }
    }
  }, [visemeSchedule])

  // ── 3. IDLE / BREATHING ───────────────────────────────────────────────
  const breathRef = useRef(0)

  useFrame((state) => {
    const t = state.clock.elapsedTime

    // ── BLINK ──
    let targetBlink = 0
    if (t > nextBlinkRef.current) {
      const blinkProgress = (t - nextBlinkRef.current) / blinkDurationRef.current
      if (blinkProgress <= 1.0) {
        targetBlink = Math.sin(blinkProgress * Math.PI)
      } else {
        nextBlinkRef.current = t + 2 + Math.random() * 4
      }
    }
    blinkRef.current = THREE.MathUtils.lerp(blinkRef.current, targetBlink, 0.4)

    // ── VISEME LIP SYNC ──
    if (isSpeaking && visemeSchedule && ttsStartRef.current !== null) {
      const elapsed = performance.now() / 1000 - ttsStartRef.current

      // Find the viseme that is currently active (last one whose time <= elapsed)
      let activeViseme = null
      for (let i = visemeSchedule.length - 1; i >= 0; i--) {
        if (elapsed >= visemeSchedule[i].time) {
          activeViseme = visemeSchedule[i].viseme
          break
        }
      }
      const weights = VISEME_MAP[activeViseme] || VISEME_MAP['sil']
      targetMouthRef.current = weights
    } else if (!isSpeaking) {
      targetMouthRef.current = { mouthOpen: 0, mouthStretch: 0 }
    }

    // Smooth the mouth transition
    smoothMouthRef.current.mouthOpen = THREE.MathUtils.lerp(
      smoothMouthRef.current.mouthOpen, targetMouthRef.current.mouthOpen, 0.25
    )
    smoothMouthRef.current.mouthStretch = THREE.MathUtils.lerp(
      smoothMouthRef.current.mouthStretch, targetMouthRef.current.mouthStretch, 0.25
    )

    // ── APPLY MORPH TARGETS ──
    Object.values(nodes).forEach((node) => {
      if (node.morphTargetDictionary && node.morphTargetInfluences) {
        const dict = node.morphTargetDictionary
        const inf = node.morphTargetInfluences

        // Mouth
        const mouthOpen = dict['mouthOpen'] ?? dict['jawOpen'] ?? dict['viseme_aa'] ?? dict['MouthOpen']
        const mouthStretch = dict['mouthStretch'] ?? dict['viseme_O'] ?? dict['MouthSmile']
        if (mouthOpen !== undefined)    inf[mouthOpen]    = smoothMouthRef.current.mouthOpen
        if (mouthStretch !== undefined) inf[mouthStretch] = smoothMouthRef.current.mouthStretch

        // Blink
        const eyeL = dict['eyeBlinkLeft']  ?? dict['Blink_Left']  ?? dict['EyeBlink_L']
        const eyeR = dict['eyeBlinkRight'] ?? dict['Blink_Right'] ?? dict['EyeBlink_R']
        if (eyeL !== undefined) inf[eyeL] = blinkRef.current
        if (eyeR !== undefined) inf[eyeR] = blinkRef.current
      }
    })

    // ── BODY MOVEMENT / IDLE ──
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

    let headX = -0.15, headY = 0.25, headZ = 0
    let neckY = 0
    let spineX = breathY * 0.5

    headX += Math.sin(t * 0.4) * 0.02
    headY += Math.cos(t * 0.3) * 0.03

    if (isSpeaking) {
      headX += Math.sin(t * 3.0) * 0.05
      headY += Math.sin(t * 1.8) * 0.1
      neckY = Math.sin(t * 1.5) * 0.04
    } else {
      headX += Math.sin(t * 0.6) * 0.01
      headY += Math.cos(t * 0.5) * 0.02
    }

    const L = 0.06
    if (bones.head) {
      bones.head.rotation.x = THREE.MathUtils.lerp(bones.head.rotation.x, headX, L)
      bones.head.rotation.y = THREE.MathUtils.lerp(bones.head.rotation.y, headY, L)
    }
    if (bones.neck) bones.neck.rotation.y = THREE.MathUtils.lerp(bones.neck.rotation.y, neckY, L)
    if (bones.spine) bones.spine.rotation.x = THREE.MathUtils.lerp(bones.spine.rotation.x, spineX, L)

    const rZ = 0.7, rX = 1.2, rY = 0.15
    if (bones.leftArm) {
      bones.leftArm.rotation.x = THREE.MathUtils.lerp(bones.leftArm.rotation.x, rX, L)
      bones.leftArm.rotation.y = THREE.MathUtils.lerp(bones.leftArm.rotation.y, rY, L)
      bones.leftArm.rotation.z = THREE.MathUtils.lerp(bones.leftArm.rotation.z, rZ, L)
    }
    if (bones.rightArm) {
      bones.rightArm.rotation.x = THREE.MathUtils.lerp(bones.rightArm.rotation.x, rX, L)
      bones.rightArm.rotation.y = THREE.MathUtils.lerp(bones.rightArm.rotation.y, -rY, L)
      bones.rightArm.rotation.z = THREE.MathUtils.lerp(bones.rightArm.rotation.z, -rZ, L)
    }
  })

  return (
    <group ref={group} {...props} dispose={null}>
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
        return null
      })}
    </group>
  )
}

useGLTF.preload('/models/julia.glb')