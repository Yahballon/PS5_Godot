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
