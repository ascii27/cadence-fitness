"""Exercise catalog — the no-equipment, home-friendly set Eva selects from.

Single source of truth for exercise metadata, instructions, and form cues.
Each exercise's visual lives at /exercises/{slug}.svg (served by the SPA).
`low_impact: True` marks joint-friendly movements (joint longevity is the
user's binding constraint).
"""
from __future__ import annotations

# category: push | pull | core | lower | mobility | conditioning
# difficulty: beginner | intermediate | advanced
# unit: reps | seconds | reps_per_side | seconds_per_side

EXERCISES: list[dict] = [
    # ---- PUSH ----
    {
        "slug": "push-up", "name": "Push-up", "category": "push",
        "target": ["chest", "triceps", "shoulders", "core"],
        "difficulty": "intermediate", "low_impact": True, "unit": "reps",
        "instructions": [
            "Start in a high plank, hands just wider than shoulders, body in a straight line.",
            "Bend the elbows to lower your chest toward the floor, elbows about 45° from your body.",
            "Press back up to full extension without letting the hips sag or pike.",
        ],
        "cues": ["Brace the core so the body moves as one plank", "Keep the neck long — look slightly ahead"],
    },
    {
        "slug": "knee-push-up", "name": "Knee Push-up", "category": "push",
        "target": ["chest", "triceps", "shoulders"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Kneel and walk the hands forward into a plank from the knees.",
            "Keep a straight line from head to knees; lower the chest under control.",
            "Press back up, keeping the hips from sagging.",
        ],
        "cues": ["Hips stay in line with the torso", "Full range — chest close to the floor"],
    },
    {
        "slug": "incline-push-up", "name": "Incline Push-up", "category": "push",
        "target": ["chest", "triceps", "shoulders"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Place your hands on a sturdy counter or table edge, body in a straight line.",
            "Lower the chest to the surface with elbows tucked ~45°.",
            "Press back up to full extension.",
        ],
        "cues": ["Higher surface = easier", "Keep glutes and core engaged"],
    },
    {
        "slug": "diamond-push-up", "name": "Diamond Push-up", "category": "push",
        "target": ["triceps", "chest"],
        "difficulty": "advanced", "low_impact": True, "unit": "reps",
        "instructions": [
            "In a plank, bring the hands together forming a diamond with thumbs and index fingers.",
            "Lower the chest toward the hands, elbows tracking close to the body.",
            "Press back up fully.",
        ],
        "cues": ["Elbows stay tight to the ribs", "Stop if it bothers the wrists — widen the hands slightly"],
    },
    {
        "slug": "pike-push-up", "name": "Pike Push-up", "category": "push",
        "target": ["shoulders", "triceps"],
        "difficulty": "advanced", "low_impact": True, "unit": "reps",
        "instructions": [
            "From a downward-dog shape, hips high, walk the feet in so the torso is near vertical.",
            "Bend the elbows to lower the crown of the head toward the floor.",
            "Press back up to straight arms.",
        ],
        "cues": ["The more vertical the torso, the harder", "Control the descent — protect the neck"],
    },
    # ---- PULL / POSTERIOR ----
    {
        "slug": "superman", "name": "Superman", "category": "pull",
        "target": ["lower back", "glutes", "upper back"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Lie face down, arms extended overhead, legs straight.",
            "Lift the arms, chest, and legs off the floor simultaneously.",
            "Hold briefly at the top, then lower with control.",
        ],
        "cues": ["Lengthen, don't just crank up — reach long", "Gaze down to keep the neck neutral"],
    },
    {
        "slug": "prone-yt-raise", "name": "Prone Y-T Raise", "category": "pull",
        "target": ["upper back", "rear delts", "lower traps"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Lie face down, forehead resting down, arms overhead in a Y.",
            "Lift the arms in the Y, then lower; next rep make a T (arms out to the sides).",
            "Alternate Y and T, squeezing the shoulder blades each time.",
        ],
        "cues": ["Thumbs up to externally rotate", "Small range, big squeeze — no momentum"],
    },
    {
        "slug": "reverse-snow-angel", "name": "Reverse Snow Angel", "category": "pull",
        "target": ["upper back", "rear delts"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Lie face down, arms by your sides, palms down, chest lightly lifted.",
            "Sweep the arms overhead along the floor, then back down to the hips.",
            "Keep the arms hovering just above the ground the whole time.",
        ],
        "cues": ["Move slowly through the full arc", "Keep the shoulders down away from the ears"],
    },
    {
        "slug": "bird-dog", "name": "Bird Dog", "category": "pull",
        "target": ["core", "lower back", "glutes"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps_per_side",
        "instructions": [
            "Start on hands and knees, spine neutral.",
            "Extend the opposite arm and leg until both are level with the torso.",
            "Return under control and switch sides.",
        ],
        "cues": ["Keep the hips square — don't rotate", "Reach long rather than high"],
    },
    # ---- CORE ----
    {
        "slug": "plank", "name": "Forearm Plank", "category": "core",
        "target": ["core", "shoulders", "glutes"],
        "difficulty": "beginner", "low_impact": True, "unit": "seconds",
        "instructions": [
            "Rest on the forearms and toes, elbows under the shoulders.",
            "Form a straight line from head to heels and hold.",
            "Breathe steadily without letting the hips drop or pike.",
        ],
        "cues": ["Squeeze glutes and brace the abs", "Push the floor away through the forearms"],
    },
    {
        "slug": "side-plank", "name": "Side Plank", "category": "core",
        "target": ["obliques", "core", "shoulders"],
        "difficulty": "intermediate", "low_impact": True, "unit": "seconds_per_side",
        "instructions": [
            "Lie on your side, forearm under the shoulder, legs stacked.",
            "Lift the hips to form a straight line from head to feet.",
            "Hold, then repeat on the other side. Drop a knee to regress.",
        ],
        "cues": ["Stack the shoulders and hips", "Lift the bottom hip toward the ceiling"],
    },
    {
        "slug": "hollow-hold", "name": "Hollow Hold", "category": "core",
        "target": ["core", "hip flexors"],
        "difficulty": "intermediate", "low_impact": True, "unit": "seconds",
        "instructions": [
            "Lie on your back, arms overhead, legs straight.",
            "Press the low back into the floor and lift the shoulders and legs a few inches.",
            "Hold the dish shape; bend the knees or lower the arms to regress.",
        ],
        "cues": ["Low back stays glued to the floor", "Long and tight, not crunched"],
    },
    {
        "slug": "dead-bug", "name": "Dead Bug", "category": "core",
        "target": ["core", "deep abdominals"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps_per_side",
        "instructions": [
            "Lie on your back, arms reaching to the ceiling, hips and knees at 90°.",
            "Lower the opposite arm and leg toward the floor without arching the back.",
            "Return and alternate sides.",
        ],
        "cues": ["Ribs down, low back pressed flat", "Move slowly — exhale as you extend"],
    },
    {
        "slug": "bicycle-crunch", "name": "Bicycle Crunch", "category": "core",
        "target": ["obliques", "abs"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Lie on your back, hands behind the head, shoulders lifted.",
            "Bring one knee in while rotating the opposite elbow toward it.",
            "Switch sides in a smooth pedaling motion.",
        ],
        "cues": ["Rotate from the torso, not the neck", "Control the tempo — quality over speed"],
    },
    {
        "slug": "leg-raise", "name": "Lying Leg Raise", "category": "core",
        "target": ["lower abs", "hip flexors"],
        "difficulty": "intermediate", "low_impact": True, "unit": "reps",
        "instructions": [
            "Lie on your back, legs straight, hands under the hips for support.",
            "Lift the legs to vertical, keeping them straight.",
            "Lower under control without letting the low back arch.",
        ],
        "cues": ["Stop lowering before the back lifts off", "Bend the knees to regress"],
    },
    {
        "slug": "russian-twist", "name": "Russian Twist", "category": "core",
        "target": ["obliques", "abs"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Sit with knees bent, heels down, leaning back to a strong tabletop torso.",
            "Clasp the hands and rotate them to tap beside each hip.",
            "Keep the chest tall as you twist side to side.",
        ],
        "cues": ["Rotate the ribcage, not just the arms", "Lift the feet to progress"],
    },
    # ---- LOWER ----
    {
        "slug": "bodyweight-squat", "name": "Bodyweight Squat", "category": "lower",
        "target": ["quads", "glutes", "hamstrings"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Stand with feet shoulder-width, toes slightly out.",
            "Sit the hips back and down, keeping the chest up and heels down.",
            "Drive through the floor to stand tall, squeezing the glutes.",
        ],
        "cues": ["Knees track over the toes", "Go only as deep as you can stay pain-free"],
    },
    {
        "slug": "reverse-lunge", "name": "Reverse Lunge", "category": "lower",
        "target": ["quads", "glutes", "hamstrings"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps_per_side",
        "instructions": [
            "Stand tall, then step one foot back and lower the back knee toward the floor.",
            "Keep the front shin vertical and the torso upright.",
            "Drive through the front heel to return to standing.",
        ],
        "cues": ["Step back, not down — easier on the knees than forward lunges", "Control the descent"],
    },
    {
        "slug": "split-squat", "name": "Split Squat", "category": "lower",
        "target": ["quads", "glutes"],
        "difficulty": "intermediate", "low_impact": True, "unit": "reps_per_side",
        "instructions": [
            "Set up in a long staggered stance, back heel lifted.",
            "Lower straight down until the back knee nears the floor.",
            "Press up through the front foot; keep the torso tall.",
        ],
        "cues": ["Most of the weight on the front foot", "Knee stays in line with the toes"],
    },
    {
        "slug": "glute-bridge", "name": "Glute Bridge", "category": "lower",
        "target": ["glutes", "hamstrings", "core"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Lie on your back, knees bent, feet flat and hip-width.",
            "Press through the heels to lift the hips into a straight line.",
            "Squeeze the glutes at the top, then lower with control.",
        ],
        "cues": ["Posterior tilt — don't arch the low back", "Drive from the heels"],
    },
    {
        "slug": "single-leg-glute-bridge", "name": "Single-leg Glute Bridge", "category": "lower",
        "target": ["glutes", "hamstrings", "core"],
        "difficulty": "intermediate", "low_impact": True, "unit": "reps_per_side",
        "instructions": [
            "Lie on your back, one knee bent, the other leg extended.",
            "Press through the planted heel to lift the hips level.",
            "Lower with control and complete the reps before switching.",
        ],
        "cues": ["Keep the hips even — don't let one side drop", "Squeeze the working glute at the top"],
    },
    {
        "slug": "wall-sit", "name": "Wall Sit", "category": "lower",
        "target": ["quads", "glutes"],
        "difficulty": "beginner", "low_impact": True, "unit": "seconds",
        "instructions": [
            "Lean your back against a wall and slide down to thighs near parallel.",
            "Knees over the ankles, feet flat.",
            "Hold the position, breathing steadily.",
        ],
        "cues": ["Press the whole back into the wall", "Raise the hips slightly to regress"],
    },
    {
        "slug": "calf-raise", "name": "Calf Raise", "category": "lower",
        "target": ["calves"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "Stand tall, feet hip-width, near a wall for balance.",
            "Rise onto the balls of the feet as high as possible.",
            "Lower the heels slowly to the floor (or below, off a step).",
        ],
        "cues": ["Pause at the top", "Slow eccentric — 2–3 seconds down"],
    },
    {
        "slug": "lateral-lunge", "name": "Lateral Lunge", "category": "lower",
        "target": ["glutes", "quads", "adductors"],
        "difficulty": "intermediate", "low_impact": True, "unit": "reps_per_side",
        "instructions": [
            "Stand tall, then step wide to one side and sit that hip back.",
            "Keep the stepping knee over the foot and the other leg straight.",
            "Push back to the center and alternate sides.",
        ],
        "cues": ["Chest up, hips back", "Keep both feet flat and pointing forward"],
    },
    # ---- MOBILITY ----
    {
        "slug": "cat-cow", "name": "Cat–Cow", "category": "mobility",
        "target": ["spine", "core"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps",
        "instructions": [
            "On hands and knees, inhale and drop the belly, lifting the chest and tailbone (cow).",
            "Exhale and round the spine, tucking the chin and tailbone (cat).",
            "Flow slowly with the breath.",
        ],
        "cues": ["Move one vertebra at a time", "Let the breath lead the motion"],
    },
    {
        "slug": "kneeling-hip-flexor-stretch", "name": "Kneeling Hip-flexor Stretch", "category": "mobility",
        "target": ["hip flexors", "quads"],
        "difficulty": "beginner", "low_impact": True, "unit": "seconds_per_side",
        "instructions": [
            "Kneel on one knee with the other foot planted in front.",
            "Tuck the pelvis and gently shift the hips forward until you feel a stretch in the back-leg hip.",
            "Hold, breathing, then switch sides.",
        ],
        "cues": ["Squeeze the back glute to deepen it", "Stay tall — don't lean forward"],
    },
    {
        "slug": "thoracic-rotation", "name": "Thoracic Rotation", "category": "mobility",
        "target": ["upper back", "spine"],
        "difficulty": "beginner", "low_impact": True, "unit": "reps_per_side",
        "instructions": [
            "On hands and knees, place one hand behind the head.",
            "Rotate that elbow down under the body, then open it up toward the ceiling.",
            "Follow the elbow with your eyes; repeat, then switch sides.",
        ],
        "cues": ["Rotate from the mid-back, not the low back", "Move slowly through the full range"],
    },
    {
        "slug": "childs-pose", "name": "Child's Pose", "category": "mobility",
        "target": ["lower back", "hips", "shoulders"],
        "difficulty": "beginner", "low_impact": True, "unit": "seconds",
        "instructions": [
            "From hands and knees, sit the hips back toward the heels.",
            "Reach the arms long in front and rest the forehead down.",
            "Breathe into the back and relax.",
        ],
        "cues": ["Widen the knees for more hip room", "Let the shoulders soften"],
    },
    {
        "slug": "downward-dog", "name": "Downward Dog", "category": "mobility",
        "target": ["hamstrings", "calves", "shoulders"],
        "difficulty": "beginner", "low_impact": True, "unit": "seconds",
        "instructions": [
            "From a plank, lift the hips up and back into an inverted V.",
            "Press the chest toward the thighs and the heels toward the floor.",
            "Pedal the feet to ease into the calves and hamstrings.",
        ],
        "cues": ["Long spine — bend the knees if the back rounds", "Spread the fingers and press the floor away"],
    },
    # ---- CONDITIONING ----
    {
        "slug": "marching-high-knees", "name": "Marching High Knees", "category": "conditioning",
        "target": ["hip flexors", "core", "cardio"],
        "difficulty": "beginner", "low_impact": True, "unit": "seconds",
        "instructions": [
            "Stand tall and march in place, driving one knee up to hip height at a time.",
            "Swing the opposite arm with each step.",
            "Keep it a march (one foot down) for a low-impact pace, or jog to progress.",
        ],
        "cues": ["Stay tall and light on the feet", "Brace the core as the knee rises"],
    },
    {
        "slug": "jumping-jack", "name": "Jumping Jack", "category": "conditioning",
        "target": ["full body", "cardio"],
        "difficulty": "beginner", "low_impact": False, "unit": "seconds",
        "instructions": [
            "Stand with feet together, arms at your sides.",
            "Jump the feet wide while raising the arms overhead.",
            "Jump back to the start and repeat at a steady rhythm.",
        ],
        "cues": ["Land softly through the whole foot", "Step one foot at a time (step-jack) for a low-impact version"],
    },
    {
        "slug": "mountain-climber", "name": "Mountain Climber", "category": "conditioning",
        "target": ["core", "shoulders", "cardio"],
        "difficulty": "intermediate", "low_impact": True, "unit": "seconds",
        "instructions": [
            "Start in a high plank, body in a straight line.",
            "Drive one knee toward the chest, then switch quickly.",
            "Keep the hips low and the shoulders over the wrists.",
        ],
        "cues": ["Don't let the hips bounce up", "Slow the pace to keep it low-impact"],
    },
    {
        "slug": "burpee", "name": "Burpee", "category": "conditioning",
        "target": ["full body", "cardio"],
        "difficulty": "advanced", "low_impact": False, "unit": "reps",
        "instructions": [
            "From standing, squat and place the hands down, then hop or step back to a plank.",
            "Optionally add a push-up, then hop or step the feet back in.",
            "Stand and reach up (add a jump to progress).",
        ],
        "cues": ["Step in/out instead of hopping to spare the joints", "Keep a braced core in the plank"],
    },
]


def by_slug(slug: str) -> dict | None:
    for ex in EXERCISES:
        if ex["slug"] == slug:
            return ex
    return None
