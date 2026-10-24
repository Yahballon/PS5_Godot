extends Node2D

# M11b only accepts SAVE persistence when a SECOND SEPARATE PROCESS
# launches this PCK and reads exactly the previous process's payload.
# No "saved" signal is invented just because a FileAccess object was made.
# All FileAccess methods are the real Godot runtime's API.
const FILE: String = "user://m11-save-v1.txt"
const MAGIC: String = "GODOT_PS5_M11_SAVE_V1"
const MAX_TICKS: int = 270

var phase: int = 0
var output_count: int = -1
var ticks: int = 0
var failed: bool = false

func _ready() -> void:
    print("GODOT_PS5_M11_SAVE_BOOT")
    print("GODOT_PS5_M11_SAVE_USER_PATH=", ProjectSettings.globalize_path(FILE))
    var previous: int = 0
    if FileAccess.file_exists(FILE):
        var reader := FileAccess.open(FILE, FileAccess.READ)
        if reader == null:
            _fail("EXISTING_READ", 71)
            return
        var text: String = reader.get_as_text()
        reader.close()
        var lines := text.strip_edges().split("|")
        if lines.size() != 3 or lines[0] != MAGIC or not lines[1].is_valid_int():
            _fail("CORRUPT_SAVE", 72)
            return
        previous = lines[1].to_int()
        if previous < 1 or previous > 100000:
            _fail("INVALID_COUNT", 73)
            return
        if lines[2] != str(previous * 13 + 947):
            _fail("CHECKSUM", 74)
            return
        print("GODOT_PS5_M11_SAVE_PERSIST_OK previous=", previous)
        phase = 2

    output_count = previous + 1
    var writer := FileAccess.open(FILE, FileAccess.WRITE)
    if writer == null:
        print("GODOT_PS5_M11_SAVE_WRITE_UNAVAILABLE error=", FileAccess.get_open_error())
        _fail("WRITE_UNAVAILABLE", 75)
        return
    writer.store_string(MAGIC + "|" + str(output_count) + "|" + str(output_count * 13 + 947) + "\n")
    writer.flush()
    var write_error: Error = writer.get_error()
    writer.close()
    if write_error != OK:
        print("GODOT_PS5_M11_SAVE_WRITE_ERROR code=", write_error)
        _fail("WRITE_ERROR", 76)
        return
    var reread := FileAccess.open(FILE, FileAccess.READ)
    if reread == null:
        _fail("READ_AFTER_WRITE", 77)
        return
    var actual: String = reread.get_as_text()
    reread.close()
    var expected: String = MAGIC + "|" + str(output_count) + "|" + str(output_count * 13 + 947) + "\n"
    if actual != expected:
        _fail("ROUNDTRIP_MISMATCH", 78)
        return

    print("GODOT_PS5_M11_SAVE_WRITE_OK current=", output_count)
    print("GODOT_PS5_M11_SAVE_VERIFY_READBACK_OK")
    if phase == 2:
        print("GODOT_PS5_M11_SAVE_RESTART_PERSISTENCE_PASS old=", previous, " new=", output_count)
    else:
        print("GODOT_PS5_M11_SAVE_FIRST_LAUNCH_PASS new=", output_count)
        phase = 1
    queue_redraw()

func _fail(detail: String, code: int) -> void:
    failed = true
    print("GODOT_PS5_M11_SAVE_FAIL_", detail)
    get_tree().quit(code)

func _process(_delta: float) -> void:
    if failed:
        return
    ticks += 1
    if ticks >= MAX_TICKS:
        print("GODOT_PS5_M11_SAVE_TEST_FINISHED phase=", phase, " count=", output_count)
        get_tree().quit(0)

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, Vector2(1920, 1080)), Color(0.018, 0.027, 0.057), true)
    draw_rect(Rect2(260, 270, 1400, 18), Color(0.91, 0.18, 0.52), true)
    var color: Color = Color(0.15, 0.98, 0.48) if phase == 2 else Color(0.13, 0.87, 0.98)
    if failed:
        color = Color(1.0, 0.12, 0.20)
    draw_rect(Rect2(620, 420, 680, 340), color, true)
    for slot in range(5):
        draw_circle(Vector2(670 + slot * 145, 870), 25,
            Color(0.10, 1.0, 0.52) if slot < mini(output_count, 5) else Color(0.25, 0.28, 0.38))
