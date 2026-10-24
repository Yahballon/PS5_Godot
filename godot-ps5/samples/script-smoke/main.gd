extends Node

# Real Godot 4 VM acceptance marker, already proven on PS5 v0.2.11.
# Keep this emitted immediately, even if pad service isn't available.
var start_ms: int = 0
var pad_seen: bool = false
var cross_down: bool = false

func _ready() -> void:
    print("GODOT_PS5_SMOKE_READY")
    start_ms = Time.get_ticks_msec()
    print("GODOT_PS5_DUALSENSE_TEST_WAITING")

func _process(_delta: float) -> void:
    if Input.get_connected_joypads().has(0) and not pad_seen:
        pad_seen = true
        print("GODOT_PS5_DUALSENSE_CONNECTED")
    var pressed: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if pressed and not cross_down:
        print("GODOT_PS5_DUALSENSE_CROSS_PRESSED")
    cross_down = pressed
    if Time.get_ticks_msec() - start_ms >= 20000:
        print("GODOT_PS5_DUALSENSE_TEST_FINISHED")
        get_tree().quit(0)
