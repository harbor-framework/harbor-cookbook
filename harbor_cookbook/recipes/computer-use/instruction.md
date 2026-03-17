# Computer Use Task

You have access to a virtual desktop through MCP tools:

**Screen:**
- `screenshot` — capture the current screen (returns an image)

**Mouse:**
- `left_click(x, y)` — left-click at pixel coordinates
- `right_click(x, y)` — right-click at pixel coordinates
- `middle_click(x, y)` — middle-click at pixel coordinates
- `double_click(x, y)` — double-click at pixel coordinates
- `triple_click(x, y)` — triple-click (e.g. to select a line)
- `left_click_drag(start_x, start_y, end_x, end_y)` — click and drag
- `mouse_move(x, y)` — move cursor without clicking
- `scroll(x, y, direction, clicks)` — scroll up or down
- `cursor_position` — get current cursor coordinates

**Keyboard:**
- `type_text(text)` — type a string of text
- `press_key(key)` — press a key or combo (e.g. `Return`, `ctrl+c`)
- `hold_key(key, duration)` — hold a key for a duration

**Utility:**
- `wait(seconds)` — pause before next action

Your task:

1. Take screenshots and interact with the application on the desktop
2. The application has a multi-step challenge — you will need to navigate through it
3. Find the secret code revealed at the end of the challenge
4. Write **only the secret code value** to `/app/secret.txt`

Write the value exactly as displayed, with no additional formatting or whitespace.
