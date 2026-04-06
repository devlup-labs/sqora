import React, { useRef, useEffect, useMemo } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function MentorModel({ isSpeaking, ...props }) {
  const group = useRef()
  const speechStrength = useRef(0)
  // Path to your model
  const { nodes, materials, animations } = useGLTF('/models/julia.glb')
  const { actions } = useAnimations(animations, group)
  const actionEntries = useMemo(() => Object.entries(actions || {}), [actions])
  const faceMesh = useMemo(
    () => Object.values(nodes).find((n) => n?.morphTargetDictionary),
    [nodes]
  )
  const handBones = useMemo(() => {
    const bones = {
      leftForeArm: null,
      rightForeArm: null,
      leftHand: null,
      rightHand: null,
    }

    Object.values(nodes).forEach((node) => {
      if (!node?.isBone || !node.name) return
      const name = node.name.toLowerCase()
      if (!bones.leftForeArm && /left.*forearm|forearm.*left/.test(name)) bones.leftForeArm = node
      if (!bones.rightForeArm && /right.*forearm|forearm.*right/.test(name)) bones.rightForeArm = node
      if (!bones.leftHand && /left.*hand|hand.*left/.test(name)) bones.leftHand = node
      if (!bones.rightHand && /right.*hand|hand.*right/.test(name)) bones.rightHand = node
    })

    return bones
  }, [nodes])

  // --- ADJUST LIP SYNC HERE ---
  const LIP_INTENSITY = 0.55 // How wide the mouth opens
  // ----------------------------

  // 1. LIP SYNC LOGIC
  useFrame((state) => {
    speechStrength.current = THREE.MathUtils.lerp(
      speechStrength.current,
      isSpeaking ? 1 : 0,
      isSpeaking ? 0.12 : 0.08
    )

    if (faceMesh) {
      const dict = faceMesh.morphTargetDictionary
      // Looks for common mouth morph names
      const mouthIndex = dict.mouthOpen ?? dict.jawOpen ?? dict.viseme_aa ?? 0

      if (mouthIndex >= 0 && faceMesh.morphTargetInfluences) {
        // Mixed speech wave feels less robotic than one pure sine.
        const t = state.clock.elapsedTime
        const speechWave =
          (0.45 + Math.abs(Math.sin(t * 4.2)) * 0.45 + Math.abs(Math.sin(t * 7.3)) * 0.2)
        const targetMouth = LIP_INTENSITY * speechWave * speechStrength.current
        faceMesh.morphTargetInfluences[mouthIndex] = THREE.MathUtils.lerp(
          faceMesh.morphTargetInfluences[mouthIndex] || 0,
          targetMouth,
          0.22
        )
      }
    }

    // Add subtle conversational arm/hand gestures while speaking.
    const t = state.clock.elapsedTime
    const gesture = speechStrength.current
    const leftForearmRestZ = -0.95
    const rightForearmRestZ = 0.95
    const forearmRestX = -0.15
    const leftHandRestY = 0.08
    const rightHandRestY = 0.08

    if (handBones.leftForeArm) {
      handBones.leftForeArm.rotation.z = THREE.MathUtils.lerp(
        handBones.leftForeArm.rotation.z,
        leftForearmRestZ + Math.sin(t * 2.2) * 0.12 * gesture,
        0.12
      )
      handBones.leftForeArm.rotation.x = THREE.MathUtils.lerp(
        handBones.leftForeArm.rotation.x,
        forearmRestX + Math.sin(t * 1.5 + 0.8) * 0.08 * gesture,
        0.12
      )
    }
    if (handBones.rightForeArm) {
      handBones.rightForeArm.rotation.z = THREE.MathUtils.lerp(
        handBones.rightForeArm.rotation.z,
        rightForearmRestZ + Math.sin(t * 2.5 + 1.1) * 0.14 * gesture,
        0.12
      )
      handBones.rightForeArm.rotation.x = THREE.MathUtils.lerp(
        handBones.rightForeArm.rotation.x,
        forearmRestX + Math.sin(t * 1.7 + 1.4) * 0.08 * gesture,
        0.12
      )
    }
    if (handBones.leftHand) {
      handBones.leftHand.rotation.y = THREE.MathUtils.lerp(
        handBones.leftHand.rotation.y,
        leftHandRestY + Math.sin(t * 3.0) * 0.08 * gesture,
        0.12
      )
    }
    if (handBones.rightHand) {
      handBones.rightHand.rotation.y = THREE.MathUtils.lerp(
        handBones.rightHand.rotation.y,
        rightHandRestY + Math.sin(t * 3.4 + 0.6) * 0.1 * gesture,
        0.12
      )
    }
  })

  // 2. SPEAK/IDLE BLENDING
  useEffect(() => {
    actionEntries.forEach(([name, action]) => {
      const lower = name.toLowerCase()
      const isTalkLike = /talk|speak|speech|chat|gesture/.test(lower)
      const isIdleLike = /idle|stand|breath|waiting/.test(lower)

      if (isSpeaking) {
        action.setEffectiveWeight(isTalkLike ? 1 : isIdleLike ? 0.35 : 0.15)
      } else {
        action.setEffectiveWeight(isIdleLike ? 1 : 0)
      }
    })
  }, [isSpeaking, actionEntries])

  // 3. START ALL ANIMATIONS FROM julia.glb ON MOUNT
  useEffect(() => {
    actionEntries.forEach(([, action]) => {
      action.enabled = true
      action.setLoop(THREE.LoopRepeat, Infinity)
      action.clampWhenFinished = false
      action.reset().play()
    })

    return () => {
      actionEntries.forEach(([, action]) => action.stop())
    }
  }, [actionEntries])

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
            />
          )
        }
        return null;
      })}
    </group>
  )
}

useGLTF.preload('/models/julia.glb')