---
name: blender-prop-production
description: Create missing narrative props and environment elements in Blender for iClone, using procedural modeling, authored PBR materials, verified scale and asset QA. Apply in both manual and Sleep workflows.
---
# Blender props — reuse the proven local production method

Use when a real staged scene or script beat requires a missing prop or set element. The user authorizes Blender creation as needed; no extra confirmation for ordinary local prop creation. Both modes have the same quality standard. Search the existing asset catalog first; choose Blender for controllable geometry, hard-surface items, furniture, signs, stage elements and structured environments; consider the existing Tidmunz/Hunyuan route for organic shapes where it is more suitable. The old blanket prohibition on Blender-first props is superseded by this instruction.

## Existing evidence and technique
Verified local examples (2026-11-27; do not copy story data into a generic release):
- tools/hair_training_kit.py: worktop, clamp, mannequin, hair, comb teeth and scissors assembled with dimensioned primitives, bevels, smooth curves, UVs and Principled materials; one FBX mesh.
- Existing story props directory: trophy_silver_v2.py and trophy_silver_v3.py, .blend/.fbx and preview PNGs. V3 corrects custom normals, smooths curved silver while keeping wood flat, uses small angle-limited bevels and authored metallic/roughness, lights for reflections, saves a new version.
- stage_retro_v2/build_stage.py: dimensioned wooden platform, stairs, columns, pleated curtains made from actual mesh grids, fabric and wood procedural PNG textures, UV variations, banner geometry, vintage lamps, separate export geometry and preview setup.
These are evidence of the prior method, not reusable fixed machine paths or proof that every asset passed iClone import.

## Discover and run
Locate the actual Blender executable (doctor, installed path). On this machine the installed version was Blender 5.3. Discover existing local Blender skills under the authorized machine's .codex/skills or relevant project .agents/skills. Read blender-core, blender-hardsurface-modeling or blender-environment-kits, blender-pbr-materials, blender-export-pipelines, blender-asset-qa and other relevant skills as needed. Verify their scripts exist before invoking. Use Blender headless in a fresh asset workspace, never reset an open user's working blend. Use a versioned output directory outside published story files and shared read-only library. No hardcoded account/drive paths. Run with --background --python-exit-code 1 --python <script> -- <output dir and parameters>. Keep authored source, .blend, FBX, texture files, QA report and preview.

## Model, review, import
1. Establish required dimensions in metres, intended era/style/materials, actor/prop contact point, reference silhouette and camera viewing distance from the story and actual scene. Plan detail where visible. For hard surfaces use bevels, properly applied transforms and smooth/flat shading by surface; for fabrics use actual folds or appropriate textures. Avoid toy-like generic cubes as final assets.
2. Author Principled BSDF channels, proper UVs and portable PNG textures. Use authored roughness and metallic values; avoid importing glossy metal as grey plastic. Review material preview against intended iClone lighting. Keep visible geometry efficient.
3. Run installed blender-asset-qa/scripts/qa_check.py and inspect actual report; use render profile for render assets. Fix errors and document justified warnings; inspect front/side/back/three-quarter renders and wireframe as applicable. Validate dimensions, normals, clipping, floating islands, material assignment, UV, texture dependencies. Recheck after repairs.
4. Export FBX mesh-only (global_scale=1, apply_unit_scale=True, -Z forward/Y up where applicable), without baked animation unless necessary. Keep portable texture files alongside FBX, and pack textures in .blend. Existing scripts/glb2fbx.py is the approved conversion for GLB; don't double-apply conversion scale.
5. Reuse scripts/ic8_part.py step_props through the current Preview-controlled cast/prop repair path. Existing spec props fields: fbx, pos, yaw, scale. Default 100 applies to metre geometry read as cm, not all assets; verify actual iClone bounds and adjust only once. Watch native Import Settings/Convert All, check new prop identity and material, avoid duplicate imports. Never delete unrelated objects. For new props after staging, use the verified repair path when implemented, otherwise return to the relevant existing Preview step and preserve sound.
6. Inspect actual iClone views at relevant beats, hand grip/attachment or prop contact, scale, occlusion, textures, background. If prop is handled, split independently movable pieces and verify contact through motion rather than merging everything. Update shot plan only after fresh scene evidence. Do not claim success from Blender preview alone.

## Scope and integration
Scene Review identifies gaps, prop preparation/repair resolves them, fresh Scene Review checks the result, Cinematic Replan then selects camera coverage. This is a skill and integration requirement; it does not itself implement a new executable Preview row. No render or approval bypass. Do not overwrite live production while another chat is operating iClone.
