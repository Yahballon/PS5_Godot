extends Control

# The labels are drawn by Godot Control/TextServer, NOT fake drawn bitmap text.
# A real OFL licensed Press Start 2P TTF is bundled in this PCK.
const TEST_FONT_PATH: String = "res://PressStart2P-Regular.ttf"
const MAX_FRAMES: int = 480
var test_font: FontFile
var current_frame: int = 0
var loaded: bool = false
var x_previous: bool = false
var title_label: Label
var status_label: Label

func _ready() -> void:
    print("GODOT_PS5_M10B_FONT_BOOT")
    var file := FileAccess.open(TEST_FONT_PATH, FileAccess.READ)
    if file == null:
        print("GODOT_PS5_M10B_FONT_FAIL_OPEN error=", FileAccess.get_open_error())
        get_tree().quit(90)
        return
    var bytes: PackedByteArray = file.get_buffer(file.get_length())
    file.close()
    if bytes.size() < 10000:
        print("GODOT_PS5_M10B_FONT_FAIL_BYTES size=", bytes.size())
        get_tree().quit(91)
        return
    print("GODOT_PS5_M10B_FONT_RESOURCE_OK size=", bytes.size())

    test_font = FontFile.new()
    var result: Error = test_font.load_dynamic_font(TEST_FONT_PATH)
    if result != OK or test_font.data.is_empty():
        print("GODOT_PS5_M10B_FONT_FAIL_LOAD status=", result)
        get_tree().quit(92)
        return
    print("GODOT_PS5_M10B_FONT_TTF_LOADED")
    if not test_font.has_char(65):
        print("GODOT_PS5_M10B_FONT_FAIL_GLYPH_A")
        get_tree().quit(93)
        return
    var measured: Vector2 = test_font.get_string_size("GODOT PS5 M10B", HORIZONTAL_ALIGNMENT_LEFT, -1, 28)
    if measured.x < 25.0 or measured.y < 10.0:
        print("GODOT_PS5_M10B_FONT_FAIL_METRICS measured=", measured)
        get_tree().quit(94)
        return
    print("GODOT_PS5_M10B_FONT_METRICS_OK size=", measured)

    var background := ColorRect.new()
    background.color = Color(0.012, 0.023, 0.052)
    background.size = Vector2(1920, 1080)
    add_child(background)
    var stripe := ColorRect.new()
    stripe.color = Color(0.9, 0.18, 0.53)
    stripe.position = Vector2(130, 160)
    stripe.size = Vector2(1660, 8)
    add_child(stripe)

    title_label = _make_label("GODOT PS5 / M10B", Vector2(130, 220), 28,
        Color(0.18, 0.95, 1.0))
    status_label = _make_label("LABEL + TRUE TYPE FONT", Vector2(130, 410), 20,
        Color(0.98, 0.98, 0.98))
    _make_label("0123456789  ABCDEFGHIJKLM", Vector2(130, 550), 16,
        Color(1.0, 0.83, 0.27))
    _make_label("UMLAUT: Ä Ö Ü ß", Vector2(130, 690), 18,
        Color(0.55, 0.96, 0.62))
    _make_label("PRESS X / CHANGE COLOR", Vector2(130, 835), 16,
        Color(0.77, 0.78, 0.88))
    loaded = true
    print("GODOT_PS5_M10B_LABEL_TREE_READY count=5")
    print("GODOT_PS5_M10B_FONT_VISUAL_TEST_STARTED")
    
func _make_label(value: String, at: Vector2, pts: int, tint: Color) -> Label:
    var label := Label.new()
    label.name = "FontTestLabel" + str(get_child_count())
    label.text = value
    label.position = at
    label.size = Vector2(1740, 105)
    label.add_theme_font_override("font", test_font)
    label.add_theme_font_size_override("font_size", pts)
    label.add_theme_color_override("font_color", tint)
    add_child(label)
    return label

func _process(_delta: float) -> void:
    if not loaded:
        return
    current_frame += 1
    var x_now: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if x_now and not x_previous:
        title_label.add_theme_color_override("font_color", Color(0.95, 0.28, 0.54))
        status_label.text = "DUALSENSE X / GODOT UI"
        print("GODOT_PS5_M10B_FONT_PAD_X")
    x_previous = x_now
    if current_frame == 180:
        print("GODOT_PS5_M10B_FONT_VISUAL_WINDOW_OK")
    if current_frame >= MAX_FRAMES:
        print("GODOT_PS5_M10B_FONT_TEST_FINISHED frames=", current_frame)
        get_tree().quit(0)
