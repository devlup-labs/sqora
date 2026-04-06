import React, { useRef, useEffect, useMemo } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function MentorModel({ isSpeaking, ...props }) {
  const group = useRef()
  // Path to your model
  const { nodes, materials, animations } = useGLTF('/models/julia.glb')
  const { actions } = useAnimations(animations, group)
  const actionEntries = useMemo(() => Object.entries(actions || {}), [actions])

  // --- ADJUST LIP SYNC / MOVEMENT HERE ---
  const LIP_SPEED = 7;
  const LIP_INTENSITY = 0.65;
  // ----------------------------

  // 1. LIP SYNC LOGIC (Enhanced for all face meshes)
  useFrame((state) => {
    const t = state.clock.elapsedTime;

    Object.values(nodes).forEach((node) => {
      if (node.morphTargetDictionary && node.morphTargetInfluences) {
        const dict = node.morphTargetDictionary;
        const mouthIndex =
          dict['mouthOpen'] !== undefined ? dict['mouthOpen'] :
            dict['jawOpen'] ?? dict['viseme_aa'];

        if (mouthIndex !== undefined) {
          if (isSpeaking) {
            const wave = (Math.abs(Math.sin(t * LIP_SPEED)) * LIP_INTENSITY) + (Math.sin(t * 7) * 0.1);
            node.morphTargetInfluences[mouthIndex] = THREE.MathUtils.lerp(
              node.morphTargetInfluences[mouthIndex],
              Math.max(0, Math.min(1, wave)),
              0.3
            );
          } else {
            node.morphTargetInfluences[mouthIndex] = THREE.MathUtils.lerp(
              node.morphTargetInfluences[mouthIndex], 0, 0.15
            );
          }
        }
      }
    });
  });

  // 2. PROCEDURAL MOVEMENT (REST POS & SPEAKING/EXPLAINING)
  useFrame((state) => {
    const t = state.clock.elapsedTime

    const bones = {
      leftArm: nodes.LeftArm,
      rightArm: nodes.RightArm,
      leftForeArm: nodes.LeftForeArm,
      rightForeArm: nodes.RightForeArm,
      head: nodes.Head,
      neck: nodes.Neck,
      spine: nodes.Spine,
    }

    // 1. CONFIRMED REST POS (Confirmed by User)
    const restZ = 0.7;
    const restX = 1.2;
    const restY = 0.15;

    // Default target rotations
    let l_Arm_Z = restZ, r_Arm_Z = -restZ;
    let l_Arm_X = restX, r_Arm_X = restX;
    let l_Arm_Y = restY, r_Arm_Y = -restY;

    let l_Fore_X = 0, r_Fore_X = 0;
    let head_Y = 0, head_X = 0, head_Z = 0;
    let neck_y = 0;

    // 2. TEACHER DYNAMICS (if isSpeaking is true)
    if (isSpeaking) {
      // --- HEAD ONLY: SLIGHTLY UP & NODDING ---
      head_X = -0.15 + (Math.sin(t * 2.5) * 0.05);
      head_Y = Math.sin(t * 1.5) * 0.12;
      head_Z = Math.cos(t * 1.1) * 0.05;
      neck_y = Math.sin(t * 1.0) * 0.04;

      // Note: All arm/forearm gestures have been removed per your request.
      // The arms will remain in the confirmed rest position while she speaks.

    } else {
      // Return to Idle/Breathing
      if (bones.spine) {
        bones.spine.rotation.x = Math.sin(t * 0.5) * 0.01;
      }
    }

    // --- APPLY ROTATIONS SMOOTHLY (LERP) ---
    const LERP_FACTOR = 0.05;

    if (bones.leftArm) {
      bones.leftArm.rotation.x = THREE.MathUtils.lerp(bones.leftArm.rotation.x, l_Arm_X, LERP_FACTOR);
      bones.leftArm.rotation.y = THREE.MathUtils.lerp(bones.leftArm.rotation.y, l_Arm_Y, LERP_FACTOR);
      bones.leftArm.rotation.z = THREE.MathUtils.lerp(bones.leftArm.rotation.z, l_Arm_Z, LERP_FACTOR);
    }
    if (bones.rightArm) {
      bones.rightArm.rotation.x = THREE.MathUtils.lerp(bones.rightArm.rotation.x, r_Arm_X, LERP_FACTOR);
      bones.rightArm.rotation.y = THREE.MathUtils.lerp(bones.rightArm.rotation.y, r_Arm_Y, LERP_FACTOR);
      bones.rightArm.rotation.z = THREE.MathUtils.lerp(bones.rightArm.rotation.z, r_Arm_Z, LERP_FACTOR);
    }
    if (bones.leftForeArm) {
      bones.leftForeArm.rotation.x = THREE.MathUtils.lerp(bones.leftForeArm.rotation.x, l_Fore_X, LERP_FACTOR);
    }
    if (bones.rightForeArm) {
      bones.rightForeArm.rotation.x = THREE.MathUtils.lerp(bones.rightForeArm.rotation.x, r_Fore_X, LERP_FACTOR);
    }
    if (bones.head) {
      bones.head.rotation.x = THREE.MathUtils.lerp(bones.head.rotation.x, head_X, LERP_FACTOR);
      bones.head.rotation.y = THREE.MathUtils.lerp(bones.head.rotation.y, head_Y, LERP_FACTOR);
      bones.head.rotation.z = THREE.MathUtils.lerp(bones.head.rotation.z, head_Z, LERP_FACTOR);
    }
    if (bones.neck) {
      bones.neck.rotation.y = THREE.MathUtils.lerp(bones.neck.rotation.y, neck_y, LERP_FACTOR);
    }
  });

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