extends SceneTree

func _initialize() -> void:
    # Build a real upstream-Godot PCK for PC validation and future PS5 bring-up.
    # No export templates needed; PCKPacker serializes source assets directly.
    var packer: PCKPacker = PCKPacker.new()
    var output: String = ProjectSettings.globalize_path("res://smoke.pck")
    var status: Error = packer.pck_start(output)
    if status != OK:
        push_error("PCK startup error: " + str(status))
        quit(1)
        return

    for name in ["project.godot", "main.tscn", "main.gd"]:
        var resource: String = "res://" + name
        status = packer.add_file(resource, ProjectSettings.globalize_path(resource))
        if status != OK:
            push_error("PCK add file error: " + resource + " " + str(status))
            quit(2)
            return

    status = packer.flush()
    if status != OK:
        push_error("PCK flush error: " + str(status))
        quit(3)
        return
    print("GODOT_PS5_PCK_WRITTEN")
    quit(0)
