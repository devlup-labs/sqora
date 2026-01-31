import React, { useRef, useEffect } from 'react'
import { useGLTF, useAnimations } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function MentorModel({ isSpeaking, ...props }) {
  const group = useRef()
  // Path to your model
  const { nodes, materials, animations } = useGLTF('/models/teacher_model.glb')
  const { actions } = useAnimations(animations, group)

  // --- ADJUST LIP SYNC HERE ---
  const LIP_SPEED = 3;        // Lower = Slower mouth movement
  const LIP_INTENSITY = 0.4;  // How wide the mouth opens
  // ----------------------------

  // 1. LIP SYNC LOGIC
  useFrame((state) => {
    // Find the face/head mesh that contains the morph targets
    const faceMesh = Object.values(nodes).find(n => n.morphTargetDictionary);
    
    if (faceMesh) {
      const dict = faceMesh.morphTargetDictionary;
      // Looks for common mouth morph names
      const mouthIndex = dict['mouthOpen'] ?? dict['jawOpen'] ?? dict['viseme_aa'] ?? 0;
      
      if (isSpeaking) {
        // Creates the "yapping" motion
        const wave = Math.abs(Math.sin(state.clock.elapsedTime * LIP_SPEED)) * LIP_INTENSITY;
        faceMesh.morphTargetInfluences[mouthIndex] = wave;
      } else {
        // Smoothly return to closed mouth when silent
        faceMesh.morphTargetInfluences[mouthIndex] = THREE.MathUtils.lerp(
          faceMesh.morphTargetInfluences[mouthIndex], 0, 0.1
        );
      }
    }
  });

  // 2. BASIC ANIMATION (Idle/Talk)
  useEffect(() => {
    const clips = Object.values(actions);
    // Finds animations based on name keywords
    const talkAction = clips.find(a => a.getClip().name.toLowerCase().includes('talk')) || clips[0];
    const idleAction = clips.find(a => a.getClip().name.toLowerCase().includes('idle')) || clips[1];

    if (isSpeaking) {
      idleAction?.fadeOut(0.5);
      talkAction?.reset().fadeIn(0.5).play();
    } else {
      talkAction?.fadeOut(0.5);
      idleAction?.reset().fadeIn(0.5).play();
    }
  }, [isSpeaking, actions]);

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

useGLTF.preload('/animated-female-teacher/source/Teacher Female Narration 01 (1).glb')