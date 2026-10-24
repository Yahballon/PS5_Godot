extends Control
# M12b progressive boot on real PS5. The original project splash is disabled
# so the last visible stage pinpoints the resource that blocks GLES3/FS.
# No substituted "toy" level; actual Level_01 remains the destination.
var _label: Label
var _step: int = 0
var _frames: int = 0
var _scene: PackedScene
var _failed: bool = false

func _ready() -> void:
    print("GODOT_PS5_M12B_BOOT_READY")
    _label = Label.new()
    _label.name = "VisibleLoaderStatus"
    _label.position = Vector2(80, 90)
    _label.size = Vector2(1600, 240)
    _label.add_theme_font_size_override("font_size", 36)
    _label.add_theme_color_override("font_color", Color(0.1, 0.97, 0.85))
    add_child(_label)
    _display("GODOT PS5  /  PLATFORMER\nSTARTING 0/6")
    queue_redraw()

func _display(msg: String) -> void:
    if _label != null:
        _label.text = msg
    print("GODOT_PS5_M12B_SCREEN ", msg.replace("\n", " | "))
    queue_redraw()

func _process(_delta: float) -> void:
    if _failed:
        return
    _frames += 1
    if _frames < 12 or _frames % 12 != 0:
        return
    match _step:
        0:
            _step += 1
            _probe("TILESET TEXTURE", "res://Assets/Spritesheet/platformPack_tilesheet.png", "Texture2D")
        1:
            _step += 1
            _probe("CHARACTER SPRITES", "res://Assets/Spritesheet/platformerPack_character.png", "Texture2D")
        2:
            _step += 1
            _probe("TRUE TYPE FONT", "res://Assets/Fonts/Star Choco.ttf", "Font")
        3:
            _step += 1
            _probe("PLAYER SCENE", "res://Scenes/Prefabs/player.tscn", "PackedScene")
        4:
            _step += 1
            _display("GODOT PS5 / PLATFORMER\nLOADING ORIGINAL LEVEL 1")
            print("GODOT_PS5_M12B_LEVEL_LOAD_BEGIN")
            var resource := ResourceLoader.load("res://Scenes/Levels/Level_01.tscn")
            if resource is PackedScene:
                _scene = resource
                print("GODOT_PS5_M12B_LEVEL_LOAD_OK")
                _display("GODOT PS5 / PLATFORMER\nLEVEL 1 READY")
            else:
                _fail("LEVEL_01.tscn failed to load")
        5:
            _step += 1
            print("GODOT_PS5_M12B_LEVEL_SWITCH_BEGIN")
            var error: Error = get_tree().change_scene_to_packed(_scene)
            if error != OK:
                _fail("level scene switch error " + str(error))
                return
            print("GODOT_PS5_M12B_LEVEL_SWITCH_OK")

func _probe(label: String, path: String, kind: String) -> void:
    _display("GODOT PS5 / PLATFORMER\nCHECKING " + label)
    print("GODOT_PS5_M12B_PROBE_BEGIN ", label, " ", path)
    var resource := ResourceLoader.load(path)
    if resource == null:
        _fail(label + " missing/unreadable")
        return
    if kind == "PackedScene" and not (resource is PackedScene):
        _fail(label + " not PackedScene")
        return
    if kind == "Texture2D" and not (resource is Texture2D):
        _fail(label + " not Texture2D")
        return
    if kind == "Font" and not (resource is Font):
        _fail(label + " not Font")
        return
    print("GODOT_PS5_M12B_PROBE_OK ", label)
    _display("GODOT PS5 / PLATFORMER\n" + label + " OK")

func _fail(message: String) -> void:
    _failed = true
    print("GODOT_PS5_M12B_LOAD_FAIL ", message)
    _display("GODOT PS5 / PLATFORMER\nRESOURCE ERROR: " + message + "\nCHECK /data/GodotPS5/gles3-stdout.log")

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, get_viewport_rect().size), Color(0.012, 0.022, 0.050), true)
    draw_rect(Rect2(Vector2(80, 53), Vector2(1480, 12)), Color(0.93, 0.20, 0.51), true)
    var filled: float = 1480.0 * minf(1.0, float(_step)/6.0)
    draw_rect(Rect2(Vector2(80, 390), Vector2(filled, 20)),
        Color(0.14, 0.95, 0.68) if not _failed else Color(1.0, 0.13, 0.2), true)
