# A.I.r Bubbles — Game Rules (Suika + Temperature)

Canon as of temp-gauge build. Suika merges plus HOT/COLD temperature layer.

**Notation:** H[4] = hot tier-4, C[4] = cold tier-4, N[4] = normal tier-4.
Written as: H[4]+H[4] = +8P, Size 5. P = temp gauge change, Size = resulting bubble tier.
Score is always Size x combo. Merges only ever happen between equal tiers.

## Spawning

1. Bubbles 1-5 show up at the right rates (small ones common, big ones rare)
   - Tech: game.gd _roll_spawn_tier, 45/30/17/6/2 percent, never 6+
2. Hot / cold / normal show up at the right rates
   - Tech: game.gd HOT_PROB 0.20, COLD_PROB 0.25, plus _roll_temp_type
3. Firing takes the ready bubble and readies a fresh random one, and you can't machine-gun fire
   - Tech: game.gd _launch_current_bubble, current takes next, new next rolled, 0.18s cooldown

## Merging

4. Only identical numbers merge (2+2, not 2+3), up to 10+10
   - Tech: game.gd _on_bubble_body_entered, tier must match, tier below 11
5. Two Apex 11s bounce and stay forever instead of disappearing like classic Suika
   - In classic Suika two watermelons vanish. Here 11+11 collide as solids (r=124,
     diameter 248 in a 400-wide chamber) and clog the board. No score, no temp change.
   - Tech: tier-match guard excludes 11, physics bounce handles the rest
6. A merge can't trigger twice from one bump
   - Tech: merging flag locks the pair
7. The old pair disappears and the next number up appears halfway between them
   - Tech: midpoint spawn tier N+1, parents freed and removed from active_bubbles

## Scoring

8. You score the number you just made, times your combo count. Fast chains pay more.
   - First merge in a chain pays x1. Every further merge within 0.95s of the last one
     raises the count (x2, x3...). Example: Size 5 made at combo 2 pays 10 lake points.
   - Tech: pts = next times combo_count, lake_size adds pts, total_merges plus 1
9. The 0.95s combo window is real wall-clock time, not physics time
   - Gravity, damp and bounce decide whether bubbles touch in time, but the window itself
     is a fixed 0.95 seconds counted every frame.
   - Tech: time adds delta in _process, combo compares time minus last_merge_time
10. Biggest tier, Apex popup and fanfare are exact
    - highest_tier becomes the new max. Normal merge shows "+N" (or "+N COMBO xK").
      Apex shows "+11 APEX TITAN!" in gold at 1.4x size, plus 36 gold particles,
      plus the 4-chord supernova sound, plus a big camera punch (trauma 0.90).
    - Tech: highest_tier, popups array, _spawn_supernova_fx, supernova_stream, camera_trauma

## Temperature

11. Two hots heat double, and the new bubble comes out safe
    - Example: H[4]+H[4] = +8P, Size 5, child normal
    - Tech: temperature adds 2 times tier_self
12. A hot merging with a normal heats single, and comes out safe
    - Example: H[4]+N[4] = +4P, Size 5, child normal
    - Tech: temperature adds 1 times tier_self
13. Two colds cool double, and the new bubble comes out normal like hot merges
    - Example: C[4]+C[4] = -8P, Size 5, child normal
    - Tech: temperature minus 2 times tier_self floored at 0, child forced normal
14. A cold merging with a normal cools once, then it is spent
    - Example: C[4]+N[4] = -4P, Size 5, child normal
    - Tech: minus tier_self floored at 0, child normal
15. Hot plus cold still grows the bubble and scores, but leaves temp alone
    - Example: H[1]+C[1] = 0P, Size 2, child normal, full points paid
    - Tech: tier merge, score and Lake stream run as normal, temp block skipped
16. Two normals do nothing to the gauge
    - Example: N[3]+N[3] = 0P, Size 4, child normal
    - Tech: delta 0, child normal
17. The gauge never goes below zero
    - Example: TEMP 2 plus C[5]+C[5] (= -10P) goes to 0, not negative
    - Tech: maxf(0, temperature minus N)
18. You only see a HEAT or COOL popup when the gauge actually moved
    - Tech: plus-N HEAT in red, N COOL in blue, nothing for 0P merges
19. Reference arithmetic in the new notation
    - H[4]+H[4] = +8P, Size 5. H[4]+N[4] = +4P, Size 5. C[4]+C[4] = -8P, Size 5.
      C[4]+N[4] = -4P, Size 5. H[1]+C[1] = 0P, Size 2. N[3]+N[3] = 0P, Size 4.
      Score in each case = Size x combo.

## Losing

20. At 20 the game warns you, at 30 it blows up
    - Tech: TEMP_WARN 20, TEMP_BURST 30, HUD shows STABLE, WARNING, BURST
21. Blowing up ends the run with an explosion screen that offers restart
    - Supernova burst at the fatal merge, trauma 1.0, scrim plus OVERHEAT BURST text
      showing temp, lake, merges and tier, and a Press R to Restart prompt.
    - Tech: game.gd _trigger_overheat, R reloads scene
22. Stacking too low still ends the run the old way
    - Bubbles float UP and pile at the surface. The dashed red line near the bottom vent
      is the overflow limit. Settled bubbles (older than 0.6s and barely moving) sitting
      below that line for 3 seconds straight end the run. Bubbles just passing through
      don't count, and the timer drains 2x fast when the pile clears.
    - Tech: DANGER_Y 80, age over 0.6s and slow (vel under 70), 3.0s countdown, 2x relief drain

## Reset and pause

23. Restart gives you a clean slate
    - Tech: R reloads scene, TEMP back to 0, overheat false, launcher re-rolled
24. Pause freezes everything and nothing merges while paused or game-over
    - Tech: P toggles, time and merges and danger frozen

## Visual, check by looking

25. Hot has steam plus orange ring, cold has frost plus blue ring, normal is clean
    - Tech: _draw_styled_bubble
26. Gauge fills with temp, pulses past 20, shows the number
    - Tech: _draw_temp_gauge, fill temp over 30, lines at 20 and 30
27. Next and launcher previews show the temp type
    - Tech: _draw_next_box and _draw_launcher_preview
28. Instructions panel fits and title pulses when hot
    - Tech: _draw_rules_panel, VENT STARTER PACK
