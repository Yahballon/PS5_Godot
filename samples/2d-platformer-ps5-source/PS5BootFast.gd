extends Control
# M12c production fast boot for the ORIGINAL G2P Studios platformer.
# Remove M12b's six gated probes and load Level_01 only ONCE.
# This logs real milliseconds to isolate native PS5 PCK I/O and scene setup.
const ORIGINAL_LEVEL := "res://Scenes/Levels/Level_01.tscn"
var _start_ms: int = 0
var _load_started: bool = false
var _frames: int = 0
var _status: Label

func _ready() -> void:
    _start_ms = Time.get_ticks_msec()
    get_tree().set_meta("godot_ps5_m12c_boot_ms", _start_ms)
    print("GODOT_PS5_M12C_BOOT_READY ts_ms=", _start_ms)
    _status = Label.new()
    _status.name = "FastBootStatus"
    _status.text = "GODOT PS5 / PLATFORMER\nLOADING LEVEL 1"
    _status.position = Vector2(80, 95)
    _status.size = Vector2(1550, 180)
    _status.add_theme_font_size_override("font_size", 36)
    _status.add_theme_color_override("font_color", Color(0.11, 0.93, 0.88))
    add_child(_status)
    queue_redraw()

func _process(_delta: float) -> void:
    # Render one frame with readable status before potentially expensive
    # synchronous resource loading. No redundant image/font/player probing.
    _frames += 1
    if _load_started or _frames < 2:
        return
    _load_started = true
    set_process(false)
    var before := Time.get_ticks_msec()
    print("GODOT_PS5_M12C_LEVEL_LOAD_BEGIN elapsed_ms=", before - _start_ms)
    var resource := ResourceLoader.load(ORIGINAL_LEVEL)
    var after := Time.get_ticks_msec()
    print("GODOT_PS5_M12C_LEVEL_LOAD_DONE duration_ms=", after - before,
          " total_ms=", after - _start_ms)
    if not (resource is PackedScene):
        _status.text = "PLATFORMER LEVEL LOAD ERROR\nCHECK GODOT LOG"
        _status.add_theme_color_override("font_color", Color(1, 0.2, 0.3))
        print("GODOT_PS5_M12C_LEVEL_LOAD_FAIL")
        return
    print("GODOT_PS5_M12C_SCENE_SWITCH_BEGIN")
    var result: Error = get_tree().change_scene_to_packed(resource)
    print("GODOT_PS5_M12C_SCENE_SWITCH_REQUESTED rc=", result,
          " elapsed_ms=", Time.get_ticks_msec() - _start_ms)
    if result != OK:
        _status.text = "PLATFORMER SCENE SWITCH ERROR"
        _status.add_theme_color_override("font_color", Color(1, 0.2, 0.3))
        print("GODOT_PS5_M12C_SCENE_SWITCH_FAIL rc=", result)

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, get_viewport_rect().size), Color(0.012,0.026,0.052), true)
    draw_rect(Rect2(Vector2(80,60), Vector2(1380,12)), Color(0.94,0.18,0.52), true)
