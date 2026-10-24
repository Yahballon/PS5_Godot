extends Node
# PS5-only input adapter for AdilDevStuff/2D-Platformer-Starter-Kit.
# Keeps original "Left"/"Right"/"Jump" action names and original game scripts.
# Actual DualSense -> Godot joy button/axes is handled by PS5 native Bridge.
var _previous_scene: String = ""
var _ticks: int = 0

func _enter_tree() -> void:
    for name in ["Left", "Right", "Jump"]:
        if not InputMap.has_action(name):
            InputMap.add_action(name)
    _axis("Left", -1.0)
    _axis("Right", 1.0)
    _button("Left", JOY_BUTTON_DPAD_LEFT)
    _button("Right", JOY_BUTTON_DPAD_RIGHT)
    _button("Jump", JOY_BUTTON_A)
    print("GODOT_PS5_M12_INPUT_READY DualSense left-stick DPad CROSS")

func _axis(action: String, direction: float) -> void:
    var event := InputEventJoypadMotion.new()
    event.device = 0
    event.axis = JOY_AXIS_LEFT_X
    event.axis_value = direction
    InputMap.action_add_event(action, event)

func _button(action: String, index: JoyButton) -> void:
    var event := InputEventJoypadButton.new()
    event.device = 0
    event.button_index = index
    InputMap.action_add_event(action, event)

func _physics_process(_delta: float) -> void:
    _ticks += 1
    var scene := get_tree().current_scene
    if scene == null:
        return
    if scene.name != _previous_scene:
        _previous_scene = scene.name
        print("GODOT_PS5_M12_SCENE_READY ", _previous_scene)
        var player := scene.get_node_or_null("Player")
        if player is CharacterBody2D:
            print("GODOT_PS5_M12_PLAYER_FOUND position=", player.global_position)
            var ground := scene.get_node_or_null("Level/Ground") as TileMapLayer
            var traps := scene.get_node_or_null("Level/Traps") as TileMapLayer
            if ground == null or traps == null:
                print("GODOT_PS5_M12D_NAV_VERIFY_FAIL missing_layer")
            elif ground.navigation_enabled or traps.navigation_enabled:
                print("GODOT_PS5_M12D_NAV_VERIFY_FAIL enabled=1")
            else:
                print("GODOT_PS5_M12D_NAV_DISABLED_CONFIRMED scene=", _previous_scene,
                      " physics_ground=", ground.collision_enabled,
                      " physics_traps=", traps.collision_enabled)
            if get_tree().has_meta("godot_ps5_m12c_boot_ms"):
                var origin: int = int(get_tree().get_meta("godot_ps5_m12c_boot_ms"))
                print("GODOT_PS5_M12C_PLAYABLE_SCENE_READY total_ms=",
                    Time.get_ticks_msec() - origin)
        else:
            # Valid during PS5Boot and during SceneTree quit/level swaps.
            # Only the actual Level_01 player-found marker is an acceptance gate.
            print("GODOT_PS5_M12_SCENE_NO_PLAYER_EXPECTED scene=", _previous_scene)
    if Input.is_action_just_pressed("Jump"):
        print("GODOT_PS5_M12_CROSS_JUMP")
    if _ticks % 180 == 0:
        var player := scene.get_node_or_null("Player")
        if player is CharacterBody2D:
            print("GODOT_PS5_M12_FRAME tick=", _ticks, " player=", player.global_position,
                " grounded=", player.is_on_floor(), " x=", Input.get_axis("Left","Right"))

# Frame hitch telemetry for native PS5 renderer/shader compilation diagnostics.
# Keep periodic logs bounded: no per-frame printf or logging on the GPU path.
var _last_report_ms: int = 0
var _hitch_count: int = 0
var _worst_frame_ms: float = 0.0
var _frame_samples: int = 0
var _frame_total_ms: float = 0.0

func _process(delta: float) -> void:
    var scene := get_tree().current_scene
    if scene == null or not scene.name.begins_with("Level_"):
        return
    var frame_ms: float = delta * 1000.0
    _frame_samples += 1
    _frame_total_ms += frame_ms
    _worst_frame_ms = maxf(_worst_frame_ms, frame_ms)
    if frame_ms >= 80.0:
        _hitch_count += 1
        if _hitch_count <= 12:
            print("GODOT_PS5_M12D_FRAME_HITCH frame_ms=", snappedf(frame_ms, 0.1),
                  " scene=", scene.name, " count=", _hitch_count)
    var now: int = Time.get_ticks_msec()
    if _last_report_ms == 0:
        _last_report_ms = now
    if now - _last_report_ms >= 5000:
        print("GODOT_PS5_M12D_FRAME_5S frames=", _frame_samples,
              " mean_ms=", snappedf(_frame_total_ms / maxf(float(_frame_samples), 1.0), 0.1),
              " worst_ms=", snappedf(_worst_frame_ms, 0.1),
              " hitches_80ms=", _hitch_count,
              " fps=", Engine.get_frames_per_second())
        _frame_samples = 0
        _frame_total_ms = 0
        _worst_frame_ms = 0
        _hitch_count = 0
        _last_report_ms = now
