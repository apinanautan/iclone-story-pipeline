# iClone 8 face lighting: avoiding half-white / half-black faces

Sources: iClone 8 manual (manual.reallusion.com/iclone-8, Scene > Light) and a Reallusion forum thread. Researched 2026-11-21.

## Why one side goes white and the other black
- Only a **key light** (one strong light from the side, e.g. the sun / a Directional) lights one side; the other side gets only ambient → black.
- Raising **Multiplier** on that light makes the contrast worse (manual: Multiplier raises strength AND contrast).
- Shadow darkness = **Global Darkness Multiplier** (Visual Settings, whole project) × per-light **Darkness**. Either at 0 cancels the other.

## Fix (never replace scene lights — add only, rules.md)
1. **Fill light** in front of the face, on the dark side or straight-on: low strength, roughly half the key or less (pipeline: `face_light_multiplier` 0.15, `lx, ly = 0` in ic8_cams.py).
2. Use a **Spotlight** for the fill. Turn its **Shadow off**, keep **Range** short with **Decay** on, and set **Falloff** high (soft edge) so it lights only the face, not the set.
3. Forum tip: put a weak, shadowless spotlight in front of each character's face. **Linkage > Pick Parent** attaches it to the head so it follows the face.
4. Lift the shadow side with brighter **Ambient** colour or **IBL** (Atmosphere), never black/dark-grey ambient.
5. Check the **Shadow Map** settings in Visual Settings:
   - **Soft Shadow** on.
   - **Shadow Range** Manual, smaller (Auto stretches the map → jagged shadows).
   - **Opacity** lower if shadows are too black.
6. Avoid pure-white light; a warm ~4750 K tint reads more naturally.
7. Skin still glowing white: check the **SSS** (Sub-surface Scattering) settings on the skin material.

## Manual pages
- Lighting_and_shadow.htm, Increasing_Light_Contrast_with_Multiplier.htm, Darkening_Shadows.htm
- Self_Cast_Shadow_Option.htm, Intensity_Beam_and_Falloff.htm, Link_for_a_Spotlight.htm, Ambient_Light.htm
- All under https://manual.reallusion.com/iclone-8/Content/ENU/8.0/20-Scene/Light/
- Forum: https://forum.reallusion.com/PrintTopic552241.aspx
