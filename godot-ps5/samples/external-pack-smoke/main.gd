extends Node2D

# Deliberately built as a SEPARATE downloadable PCK, never part of the
# PPSA99847 native binary. It tests res://, GDScript, Canvas2D, pad and scenes.
# No fonts, audio, PhysicsServer2D, imported textures, or native custom GL.
var frames: int = 0
var previous_cross: bool = false
var background: Color = Color(0.015, 0.065, 0.13)
var accent: Color = Color(0.98, 0.28, 0.66)

func _ready() -> void:
    print("GODOT_PS5_EXTERNAL_MAIN_READY")
    var asset: FileAccess = FileAccess.open("res://palette.json", FileAccess.READ)
    if asset == null:
        print("GODOT_PS5_EXTERNAL_ASSET_FAILED open=", FileAccess.get_open_error())
        get_tree().quit(11)
        return
    var parsed: Variant = JSON.parse_string(asset.get_as_text())
    asset.close()
    if not (parsed is Dictionary):
        print("GODOT_PS5_EXTERNAL_ASSET_FAILED invalid_json")
        get_tree().quit(12)
        return
    var colors: Dictionary = parsed
    if not colors.has("background") or not colors.has("accent"):
        print("GODOT_PS5_EXTERNAL_ASSET_FAILED missing_colors")
        get_tree().quit(13)
        return
    var bg: Array = colors["background"]
    var fg: Array = colors["accent"]
    if bg.size() != 4 or fg.size() != 4:
        print("GODOT_PS5_EXTERNAL_ASSET_FAILED color_size")
        get_tree().quit(14)
        return
    background = Color(float(bg[0]), float(bg[1]), float(bg[2]), float(bg[3]))
    accent = Color(float(fg[0]), float(fg[1]), float(fg[2]), float(fg[3]))
    print("GODOT_PS5_EXTERNAL_ASSET_OK")
    queue_redraw()

func _process(_delta: float) -> void:
    frames += 1
    var cross: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if cross and not previous_cross:
        print("GODOT_PS5_EXTERNAL_GAMEPAD_X")
        accent = Color(0.12, 0.94, 1.0) if accent.r > 0.5 else Color(0.98, 0.28, 0.66)
        queue_redraw()
    previous_cross = cross
    if frames == 180:
        print("GODOT_PS5_EXTERNAL_SCENE_CHANGE_REQUESTED")
        var result: Error = get_tree().change_scene_to_file("res://second.tscn")
        if result != OK:
            print("GODOT_PS5_EXTERNAL_SCENE_CHANGE_FAILED status=", result)
            get_tree().quit(15)

func _draw() -> void:
    draw_rect(Rect2(0, 0, 1920, 1080), background, true)
    draw_rect(Rect2(150, 125, 1620, 830), accent, false, 12.0)
    draw_circle(Vector2(960, 540), 180.0, accent)
    draw_circle(Vector2(960, 540), 125.0, background)
    for i in range(8):
        draw_rect(Rect2(420.0 + i * 145.0, 885, 90, 18), accent, true)
