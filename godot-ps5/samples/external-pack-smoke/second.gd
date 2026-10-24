extends Node2D

var frames: int = 0
var previous_cross: bool = false
var accent: Color = Color(0.12, 0.94, 1.0)

func _ready() -> void:
    print("GODOT_PS5_EXTERNAL_SECOND_SCENE_READY")
    queue_redraw()

func _process(_delta: float) -> void:
    frames += 1
    var cross: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if cross and not previous_cross:
        print("GODOT_PS5_EXTERNAL_SECOND_SCENE_GAMEPAD_X")
        accent = Color(0.98, 0.28, 0.66) if accent.g > 0.5 else Color(0.12, 0.94, 1.0)
        queue_redraw()
    previous_cross = cross
    if frames >= 240:
        print("GODOT_PS5_EXTERNAL_FINISHED")
        get_tree().quit(0)

func _draw() -> void:
    draw_rect(Rect2(0, 0, 1920, 1080), Color(0.075, 0.025, 0.115), true)
    draw_rect(Rect2(90, 90, 1740, 900), accent, false, 16.0)
    draw_circle(Vector2(960, 540), 215, accent)
    draw_rect(Rect2(850, 430, 220, 220), Color(0.075, 0.025, 0.115), true)
