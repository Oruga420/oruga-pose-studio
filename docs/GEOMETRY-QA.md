# ARCHIVED — Preliminary QA, superseded by olive mannequin refinement

This note records findings from the early pale prototype. Do not restore that palette: the user subsequently requested military olive green plus construction guides. Chest artifact, limb caps, face badge, neck, hands, feet and major reach issues were revised. Small seed target clamps remain reported in per-pose metadata (e.g. reach/T-pose); these are not silent failures. Current source and HANDOFF.md are authoritative.

---

# Geometry QA — initial 24-pose prototype

Reviewed 2026-10-28, before the final continuous-torso refinement. These are development observations, not a claim that the full collection was visually approved.

## Verified improvements

- Single lofted feet are materially cleaner than the initial three-ellipsoid foot.
- Near-zero end-cap rings reduce the initial radial pleating at limb ends.
- Removed chest strip eliminates an unnatural reflective spike.
- Two-bone IK preserves limb lengths in the three preview scenes checked.

## Priority anatomy and presentation refinements

1. Use a continuous torso silhouette, with a gently tapered waist and wider pelvis, rather than three separate blocks.
2. Shorten the visible neck to about 0.06 m. At overall height about 1.84 m, a 0.27 m head reads disproportionately large: reduce head height around 10%.
3. Do not use a separate ellipsoid for a facial plane: it reads as a badge attached to the face. Keep the head featureless or flatten the front of the actual head rings.
4. For a neutral drawing reference, use pale matte material, light background, understated gray articulation accents, and restrained cavity contrast.
5. Permit explicit wrist/hand orientation. Continuing the forearm direction is inadequate for palms on a thigh, hands at hips, pointing and palms-together gestures.
6. Permit foot pitch/roll as well as yaw for running, kneeling, reclining and airborne poses.

## Seed target audit

Distances below use the initial shoulder offset ±0.222 m and arm lengths 0.29 + 0.26 m. Re-run after any proportion change.

| Pose | Finding |
| --- | --- |
| action-punch | Left target exceeds maximum reach by 0.156 m; move wrist y from -0.69 toward approximately -0.52 m, then recheck. |
| stand-reach | Right target exceeds reach by 0.020 m. |
| sit-lean | Both wrists exceed reach by approximately 0.008 m. |
| stand-hands-hips | Wrist targets are within the front pelvis/torso volume. Move outward and forward; inspect actual palm and fingers, not only wrist. |
| sit-upright | Side preview shows hands penetrating thighs. Raise wrists and orient palms down / fingers forward. |

Use a 0.005 m warning threshold for end-effector reach error rather than 0.04 m. Record requested and solved end-effector coordinates separately. IK validity alone does not certify absence of mesh collisions, plausible weight bearing, or hand placement.

## Preview coverage

Inspected front/three-quarter/side outputs for neutral standing, upright seated and running. These three are representative smoke tests only. Review a contact sheet of all 24 seeds, then mixed representative samples from any expanded catalog before calling a larger collection quality-checked.
