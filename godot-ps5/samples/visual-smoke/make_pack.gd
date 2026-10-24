extends SceneTree

func _initialize() -> void:
    var packer: PCKPacker = PCKPacker.new()
    var output: String = ProjectSettings.globalize_path("res://visual-smoke.pck")
    var status: Error = packer.pck_start(output)
    if status != OK:
        push_error("PCK start error: " + str(status))
        quit(1)
        return
    for name in ["project.godot", "main.tscn", "main.gd"]:
        var resource: String = "res://" + name
        status = packer.add_file(resource, ProjectSettings.globalize_path(resource))
        if status != OK:
            push_error("PCK add error: " + resource + " " + str(status))
            quit(2)
            return
    status = packer.flush()
    if status != OK:
        push_error("PCK flush error " + str(status))
        quit(3)
        return
    print("GODOT_PS5_VISUAL_PCK_WRITTEN")
    quit(0)
