# Image generation prompts — warm indie pixel warehouse

Generated with the built-in imagegen tool on 2026-10-01. The following is the
prompt set used for the selected assets; no API/CLI fallback was used.
Runtime loads only the normalized PNG files in this directory.

## Shared generation prompt

Use case: stylized-concept. Asset type: production PNG pixel-art sprite for a warm indie Sokoban warehouse game. Strict hand-placed low-resolution pixel art on a coarse uniform grid (tile sprites read as 24x24 logical pixels, player as 24x29). Render large crisp nearest-neighbor pixels. Same restrained 12-color palette for every asset: dark #2b211d, #49342b, #6b4935, #996740, #bc884d, honey #dfb653, cream #f1dfac, stone #8b8067, #b2a58a, moss #52633c, #77884b, skin #d5ac78. Light from UPPER LEFT of screen, hard shadows lower-right. Rustic handmade character, matte materials, NO gradients, NO antialiasing, NO blur, NO glossy plastic, NO 3D render, NO text, NO watermark.

## board_frame.png

Shared prompt + Primary request: ONE square overhead ground slab. Plain packed dark brown earth fills center, narrow moss green grassy rim with just 5 small grass tufts near perimeter. Square footprint, step-shaped corners, slight 2-pixel hard dark bottom edge. Slab occupies 94% width/height, transparent 3% outside margins. NO hole or inset playing field. Center at least 90% is uninterrupted calm solid brown earth. Nine-slice suitable, grass stays on edge.
## floor.png

Shared prompt + Primary request: ONE seamlessly tileable flat stone floor square texture. Fully opaque edge to edge. Four large warm gray-brown stone slabs, minimal detail, sparse 1-pixel chips, subdued contrast. NO border or bevel or shadows at outside edges, NO objects.

## wall_top.png

Shared prompt + Primary request: ONE seamlessly tileable square old brick wall top texture. Fully opaque edge to edge. FOUR horizontal rows of rustic brown terracotta bricks with alternating joints, warm cream-brown mortar 1 pixel wide. Identical top and bottom joining edges. NO outer border, no bevel or perspective, no objects.

## wall_front.png

Shared prompt + Primary request: ONE seamlessly horizontally tileable horizontal old brick wall FRONT strip, 6:1 aspect ratio. Fully opaque. One short row of darker brown terracotta bricks with 1 pixel joints, thin warm top edge and dark lower edge. Front view. NO endcaps or left/right outer border.
## goal.png

Shared prompt + Primary request: ONE floor target marker, a small flat honey-yellow square with cream corner markings and a small hollow center diamond, perfectly overhead. Not raised, not a button. Centered occupying 60% square width, transparent everywhere outside marker. Center must have opaque honey color. Hard pixel edges.
## box.png

Shared prompt + Primary request: ONE wooden crate sprite. Orthographic top-down with a short dark brown front face visible below, square footprint. Honey brown timber, diagonal wooden brace across plank top, dark nails at corners, cream highlights on upper-left, hard shadow only below-right. Centered with transparent margins, crate about 84% width and 80% height. NO rounded glossy edges.
## box_goal.png

Use case: precise-object-edit. Edit target: supplied wooden Sokoban pixel sprite. Create its completed-goal variant. Preserve EXACT canvas, framing, silhouette, dimensions, camera, pixel grid, nail positions, diagonal brace direction (upper-left to lower-right), plank pattern and every dark outline. Recolor only the wood to moss green shades #52633c and #77884b, cream upper-left highlights #f1dfac, same dark brown front face #49342b. Add one very clear thick cream check mark at center of top face, fully inside crate. Preserve genuine transparent alpha outside, hard pixel edges, upper-left lighting, no glow, no gradients, no antialiasing. Do not rotate, reshape, resize or move anything. Reference: generated box.png before normalization.
## player_south.png

Shared prompt + Primary request: ONE tiny chibi warehouse worker facing SOUTH toward bottom of screen. Messy brown hair, visible small face with two dark dot eyes, mustard yellow overalls/outfit, cream skin, dark brown boots. Top-down 3/4 overhead RPG camera, compact proportions, two arms visible. Full body centered transparent margins. Feet share bottom alignment, character about 70% width and 85% height. NO hat.
## player_north.png

Shared prompt + Primary request: ONE tiny chibi warehouse worker facing NORTH toward top of screen. Messy brown hair, back of head visible, NO face visible, mustard yellow overalls/outfit, cream skin at hands, dark brown boots. Top-down 3/4 overhead RPG camera, compact proportions, two arms visible. Full body centered transparent margins. Feet share bottom alignment, character about 70% width and 85% height. NO hat.
## player_east.png

Shared prompt + Primary request: ONE tiny chibi warehouse worker facing EAST toward right of screen. Messy brown hair, small profile face and nose point right, mustard yellow overalls/outfit, cream skin, dark brown boots. Top-down 3/4 overhead RPG camera, compact proportions. Full body centered transparent margins. Feet share bottom alignment, character about 60% width and 85% height. NO hat.
## player_west.png

Shared prompt + Primary request: ONE tiny chibi warehouse worker facing WEST toward left of screen. Messy brown hair, small profile face and nose point left, mustard yellow overalls/outfit, cream skin, dark brown boots. Top-down 3/4 overhead RPG camera, compact proportions. Full body centered transparent margins. Feet share bottom alignment, character about 60% width and 85% height. NO hat.

## Technical export

Selected environment assets use the original generated artwork, without the
coarse 8-pixel/12-color conversion. Nearest-neighbor resampling uses a much
finer 2-pixel PNG grid and preserves source RGB shades. Alpha is exported as
0/255 for crisp outlines. Boxes have 112×128 content at (16,28), bottom anchor
y=156. Players preserve their source aspect ratios, have 144-pixel content
height at y=18 and bottom anchor y=162: south 84px wide, north 72px, east/west
80px. They are centered horizontally and no hair, hands or feet are cropped.
Goal content is 80×80 at (32,32). Wall-front white padding is excluded. All
11 final canvas sizes and filenames match the existing runtime contract.

## Light character refinement — selected variants

The following identity-preserving edit was applied separately to each original
player direction using the built-in imagegen tool. Each original full-resolution
character was the edit target; the coarse runtime sprite was not used as input.

Use case: identity-preserve. Edit target: supplied pixel-art Sokoban worker. The user loves this generated character and wants ONLY a SMALL simplification, about 10-15 percent fewer tiny interior shading marks. Preserve at least 85-90 percent of its detail and charm. Keep the EXACT direction, overhead camera, pose, proportions, full-body silhouette, framing, canvas, transparency and upper-left lighting. Keep the messy brown hair including distinctive tufts, the face and dark eyes if visible, cream sleeves, mustard yellow overalls including straps/pocket, both hands, and both dark brown boots. Only merge a few isolated highlight/noise pixels into slightly cleaner hair and trouser shading clusters. Keep the existing fine pixel size and the original rich warm shades. Do NOT make a chunky low-resolution version; do NOT enlarge pixel blocks, quantize to a tiny fixed palette, remove facial features, crop the hair or feet, compress/stretch the body, redesign clothing, add objects, or change orientation. Transparent background, full character in frame, crisp hard pixel edges, no gradients, no blur, no glow, no antialiasing.

Direction invariant appended per request: facing SOUTH / NORTH / EAST / WEST.

## Calmer environment refinement — selected runtime assets

Edited with the built-in imagegen tool on 2026-10-01 from the existing four
runtime environment PNGs. These prompts supersede the initial environment
prompts above; the seven player/crate/goal PNGs were not edited.

### Shared edit instructions

Use case: precise-object-edit. Production pixel-art texture for the existing warm indie Sokoban warehouse. Edit the supplied target only. Preserve its handcrafted matte pixel-art language and upper-left lighting, with hard darker edges toward lower right. Fine authored 2x2 PNG pixel grid, crisp nearest-neighbor edges, restrained earthy browns, warm stone cream-gray and moss. NO blur, antialiasing, glow, gradient, glossy effects, text or watermark. The player and crates are separate assets and must not appear here.

### floor.png

Target: current floor.png, 144x144, fully opaque. Replace the four small slabs with EXACTLY ONE large square stone slab occupying the whole canvas edge to edge. It represents ONE movement cell. There must be NO horizontal or vertical division inside it, NO central cross, NO inset plate or extra outside margin. Light warm cream-gray stone, main color around #b9af98 with gentle shade clusters around #afa58e and #c3baa4, clearly lighter than the input. A very thin subdued perimeter seam (about 2 PNG pixels) defines the cell, seam tone close to the stone, never dark black. Broad nearly quiet center with ONLY two tiny restrained worn edge chips. No speckles or repeated cracks. Flat overhead tile, seamless when repeated, no perspective/bevel/raised button. Keep fine visual character; don't render as vector art.

### wall_top.png

Target: current wall_top.png, 144x144, fully opaque edge to edge. Replace the eight small brick rows with EXACTLY FOUR equal horizontal brick rows, each row 36px high in the final 144px tile. Larger rustic old terracotta-brown bricks in muted shades around #866447 and #927151; alternating vertical joints in a periodic running-bond pattern. Thin subdued mortar near #9a8064, close in brightness to the brick, NOT pale cream or bright yellow. Horizontal/vertical repeat must join seamlessly with no framed tile edge. Keep a few broad gentle wear clusters, remove isolated bright flecks and dense small scratches. No per-tile outline, bevel, ledge, front face, transparent padding, grid overlay, symbols or objects. The tile is the continuous flat top texture and stays much calmer than crates.

### board_frame.png

Target: current board_frame.png, 512x512 with genuine transparent outside corners. Keep EXACT canvas, outline/silhouette, footprint, alpha framing, ground thickness and nine-slice structure. Make soil and rim calmer: mostly quiet muted warm brown earth around #715340, merge the many scattered dots into a few broad low-contrast color clusters, simplify moss to softly defined groups, keep only five small distinct grass tufts along the edge. Preserve the narrow moss border and hard lower/right edge. At least central 85 percent is calm unobstructed packed earth. NO inset hole, additional frame, buildings, paving, objects. Genuine transparent alpha outside; don't crop or enlarge the slab.

### wall_front.png

Input 1 is the edit target: existing wall_front.png, a 144x24 horizontal strip (6:1). Input 2 is the selected calmer wall_top, style and color reference only. Create a matching DARKER exposed FRONT edge for those large old bricks. EXACT one thin brick row, three long bricks across 144px, staggered periodic vertical joints, full 6:1 rectangle filled to all four edges, no padding. Muted matte brown around #62462f with restrained mortar around #765c42. A thin upper-left edge, hard dark lower edge, lower overall brightness than reference wall top. Only a few large quiet shade clusters, no scattered flecks. Preserve 144x24 final footprint and horizontal tiling with no endcaps or outside frame. No white background, no transparency, no additional rows, no beveled button.

### Selected export

Nearest-neighbor down/up sampling to a 2x2 PNG pixel grid preserves source
RGB shades, with alpha thresholded to 0/255. Final sizes remain 512x512 for
the frame, 144x144 for floor and wall top, and 144x24 for the front. The
front strip is cropped from source rows 165..558 to exclude generated black
padding. No character, crate or goal is cropped, resized or recolored.
The scene uses integer art-pixel scaling only when it retains at least 95%
of the largest fit; otherwise the whole scene is fitted with nearest-neighbor.
