extends SceneTree

func _initialize() -> void:
    var p := PCKPacker.new()
    var file_out := ProjectSettings.globalize_path("res://m10b-font-ui.pck")
    var result: Error = p.pck_start(file_out)
    if result != OK:
        push_error("GODOT_PS5_M10B_FONT_PACK_FAIL start=" + str(result))
        quit(98)
        return
    for filename in [
        "project.godot", "main.tscn", "main.gd",
        "PressStart2P-Regular.ttf", "OFL.txt", "FONTLOG.txt"
    ]:
        result = p.add_file("res://" + filename,
                ProjectSettings.globalize_path("res://" + filename))
        if result != OK:
            push_error("GODOT_PS5_M10B_FONT_PACK_FAIL file=" + filename)
            quit(99)
            return
    result = p.flush()
    if result != OK:
        push_error("GODOT_PS5_M10B_FONT_PACK_FAIL flush=" + str(result))
        quit(100)
        return
    print("GODOT_PS5_M10B_FONT_PCK_WRITTEN")
    quit(0)
