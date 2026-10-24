extends CanvasLayer
# Keep original SceneTransition.load_scene(PackedScene) API while moving
# heavy AnimationPlayer creation out of the initial autoload boot path.
var _overlay: ColorRect
var _switching: bool = false

func _ready() -> void:
    print("GODOT_PS5_M12B_SCENE_TRANSITION_LIGHT_READY")

func load_scene(target_scene: PackedScene) -> void:
    if _switching or target_scene == null:
        return
    _switching = true
    print("GODOT_PS5_M12B_TRANSITION_BEGIN")
    if _overlay == null:
        _overlay = ColorRect.new()
        _overlay.name = "TransitionOverlay"
        _overlay.color = Color(0, 0, 0, 0)
        _overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
        add_child(_overlay)
    var tween := create_tween()
    tween.tween_property(_overlay, "color:a", 1.0, 0.25)
    await tween.finished
    var err: Error = get_tree().change_scene_to_packed(target_scene)
    print("GODOT_PS5_M12B_TRANSITION_SCENE_RC ", err)
    var out := create_tween()
    out.tween_property(_overlay, "color:a", 0.0, 0.25)
    await out.finished
    _switching = false
