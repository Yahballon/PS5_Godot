extends Node2D

# M11b2: PS5 FileAccessUnix.file_exists() uses libc stat/access, which
# returned FALSE on hardware even while the save was physically present.
# For the true restart gate, open READ directly with Godot FileAccess.
# Never overwrite any existing save if an unexpected READ error occurs.

const FILE: String = "user://m11-save-v1.txt"
const MAGIC: String = "GODOT_PS5_M11_SAVE_V1"
const FONT_PATH: String = "res://PressStart2P-Regular.ttf"
const MAX_FRAMES: int = 300

var phase: int = 0
var output_count: int = 0
var old_count: int = 0
var frame_count: int = 0
var exit_code: int = 0
var ui_status: String = "INITIALIZING"
var ui_detail: String = ""
var font: FontFile
var status_label: Label
var count_label: Label

func _ready() -> void:
    print("GODOT_PS5_M11B2_BOOT")
    print("GODOT_PS5_M11B2_PATH=", ProjectSettings.globalize_path(FILE))
    var exists_hint: bool = FileAccess.file_exists(FILE)
    print("GODOT_PS5_M11B2_STAT_HINT=", exists_hint)
    var reader := FileAccess.open(FILE, FileAccess.READ)
    if reader != null:
        var text: String = reader.get_as_text()
        reader.close()
        var pieces := text.strip_edges().split("|")
        if pieces.size() != 3 or pieces[0] != MAGIC or not pieces[1].is_valid_int():
            _fail("SAVE_FORMAT", 81)
            _create_ui()
            return
        old_count = pieces[1].to_int()
        if old_count < 1 or old_count > 100000 or pieces[2] != str(old_count * 13 + 947):
            _fail("SAVE_CHECKSUM", 82)
            _create_ui()
            return
        phase = 2
        print("GODOT_PS5_M11B2_DIRECT_READ_OK previous=", old_count)
    else:
        var err: Error = FileAccess.get_open_error()
        print("GODOT_PS5_M11B2_DIRECT_READ_MISSING err=", err)
        if err != ERR_FILE_NOT_FOUND:
            _fail("READ_ERROR", 83)
            _create_ui()
            return

    output_count = old_count + 1
    var writer := FileAccess.open(FILE, FileAccess.WRITE)
    if writer == null:
        _fail("WRITE_OPEN", 84)
        _create_ui()
        return
    var content: String = MAGIC + "|" + str(output_count) + "|" + str(output_count * 13 + 947) + "\n"
    writer.store_string(content)
    writer.flush()
    var write_error: Error = writer.get_error()
    writer.close()
    if write_error != OK:
        _fail("WRITE_FLUSH", 85)
        _create_ui()
        return
    print("GODOT_PS5_M11B2_WRITE_OK new=", output_count)

    var verify := FileAccess.open(FILE, FileAccess.READ)
    if verify == null:
        _fail("VERIFY_OPEN", 86)
        _create_ui()
        return
    var readback := verify.get_as_text()
    verify.close()
    if readback != content:
        _fail("VERIFY_MISMATCH", 87)
        _create_ui()
        return
    print("GODOT_PS5_M11B2_READBACK_OK")

    if phase == 2:
        ui_status = "SAVE RESTORED"
        ui_detail = "PREVIOUS " + str(old_count) + "  NEW " + str(output_count)
        print("GODOT_PS5_M11B2_RESTART_PERSISTENCE_PASS old=", old_count, " new=", output_count)
    else:
        phase = 1
        ui_status = "FIRST SAVE CREATED"
        ui_detail = "NEW SAVE " + str(output_count) + "  RESTART APP"
        print("GODOT_PS5_M11B2_FIRST_LAUNCH_PASS new=", output_count)
    _create_ui()
    queue_redraw()

func _fail(reason: String, code: int) -> void:
    exit_code = code
    phase = 3
    ui_status = "SAVE TEST ERROR"
    ui_detail = reason + "  CODE " + str(code)
    print("GODOT_PS5_M11B2_FAIL_", reason, " code=", code)

func _create_ui() -> void:
    font = FontFile.new()
    var err: Error = font.load_dynamic_font(FONT_PATH)
    if err != OK or not font.has_char(65):
        print("GODOT_PS5_M11B2_FONT_UNAVAILABLE err=", err)
        if exit_code == 0:
            _fail("FONT", 88)
        return
    _label("GODOT PS5 / SAVEGAME M11B2", Vector2(110, 190), 21,
        Color(0.15, 0.91, 1.0))
    status_label = _label(ui_status, Vector2(110, 400), 26,
        Color(0.99, 0.26, 0.39) if phase == 3 else Color(0.16, 0.99, 0.49))
    count_label = _label(ui_detail, Vector2(110, 580), 15,
        Color(0.98, 0.86, 0.31))
    _label("APP EXITS AFTER TEST  /  START AGAIN", Vector2(110, 820), 13,
        Color(0.78, 0.81, 0.95))
    print("GODOT_PS5_M11B2_VISIBLE_STATUS_READY phase=", phase)

func _label(msg: String, at: Vector2, size: int, color: Color) -> Label:
    var obj := Label.new()
    obj.text = msg
    obj.position = at
    obj.size = Vector2(1740, 110)
    obj.add_theme_font_override("font", font)
    obj.add_theme_font_size_override("font_size", size)
    obj.add_theme_color_override("font_color", color)
    add_child(obj)
    return obj

func _process(_delta: float) -> void:
    frame_count += 1
    if frame_count >= MAX_FRAMES:
        print("GODOT_PS5_M11B2_TEST_FINISHED phase=", phase, " count=", output_count,
              " code=", exit_code)
        get_tree().quit(exit_code)

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, Vector2(1920, 1080)), Color(0.016, 0.026, 0.052), true)
    draw_rect(Rect2(110, 310, 1650, 13), Color(0.94, 0.2, 0.51), true)
    var tint: Color = Color(0.96, 0.19, 0.25) if phase == 3 else (Color(0.1, 1.0, 0.44) if phase == 2 else Color(0.14, 0.81, 0.98))
    draw_rect(Rect2(1350, 380, 260, 270), tint, true)
