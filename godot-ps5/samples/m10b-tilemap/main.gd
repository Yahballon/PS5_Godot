extends Node2D

# A real TileMapLayer built with TileSetAtlasSource and TileData physics polygons.
# Engine-drawn atlas tiles; NO manually drawn platform or fake collision result.
# Godot PhysicsServer2D KinematicCollision2D must identify this TileMapLayer.

const TILE_PX: int = 64
const FLOOR_ROW: int = 12
const START_X: float = 960.0
const START_Y: float = 210.0
const BODY_PX: float = 50.0
const SPEED: float = 660.0
const MAX_TICKS: int = 650

var layer: TileMapLayer
var mover: CharacterBody2D
var tick: int = 0
var hit: bool = false
var completed: bool = false
var waited: int = 0
var previous_x: bool = false

func _ready() -> void:
    print("GODOT_PS5_M10B_TILE_BOOT")
    var image := Image.create(TILE_PX, TILE_PX, false, Image.FORMAT_RGBA8)
    image.fill(Color(0.94, 0.20, 0.53))
    var image_texture := ImageTexture.create_from_image(image)
    var set := TileSet.new()
    set.tile_size = Vector2i(TILE_PX, TILE_PX)
    set.add_physics_layer()
    set.set_physics_layer_collision_layer(0, 1)
    set.set_physics_layer_collision_mask(0, 2)
    var atlas := TileSetAtlasSource.new()
    atlas.texture = image_texture
    atlas.texture_region_size = Vector2i(TILE_PX, TILE_PX)
    atlas.create_tile(Vector2i.ZERO)
    var source_id: int = set.add_source(atlas)
    var data: TileData = atlas.get_tile_data(Vector2i.ZERO, 0)
    if data == null:
        print("GODOT_PS5_M10B_TILE_FAIL_DATA")
        get_tree().quit(70)
        return
    data.set_collision_polygons_count(0, 1)
    data.set_collision_polygon_points(0, 0, PackedVector2Array([
        Vector2(-32, -32), Vector2(32, -32), Vector2(32, 32), Vector2(-32, 32)
    ]))
    layer = TileMapLayer.new()
    layer.name = "RealTileMapPlatform"
    layer.tile_set = set
    add_child(layer)
    # One real Godot tile per grid cell, no Sprite2D or StaticBody2D floor.
    for x in range(11, 20):
        layer.set_cell(Vector2i(x, FLOOR_ROW), source_id, Vector2i.ZERO)
    layer.update_internals()
    if layer.get_cell_source_id(Vector2i(15, FLOOR_ROW)) != source_id:
        print("GODOT_PS5_M10B_TILE_FAIL_CELL")
        get_tree().quit(71)
        return
    print("GODOT_PS5_M10B_TILEMAP_READY cells=9 source=", source_id)

    mover = CharacterBody2D.new()
    mover.name = "TileColliderCharacter"
    mover.position = Vector2(START_X, START_Y)
    mover.collision_layer = 2
    mover.collision_mask = 1
    var shape_node := CollisionShape2D.new()
    var rect := RectangleShape2D.new()
    rect.size = Vector2(BODY_PX, BODY_PX)
    shape_node.shape = rect
    mover.add_child(shape_node)
    add_child(mover)
    print("GODOT_PS5_M10B_TILE_BODY_READY")
    queue_redraw()

func _physics_process(delta: float) -> void:
    tick += 1
    if completed:
        return
    if hit:
        waited += 1
        if waited == 90:
            completed = true
            print("GODOT_PS5_M10B_TILE_TEST_PASS tick=", tick, " y=", mover.global_position.y)
            get_tree().quit(0)
        return
    var contact: KinematicCollision2D = mover.move_and_collide(Vector2(0, SPEED * minf(delta, 0.05)))
    if contact != null:
        var target: Object = contact.get_collider()
        var normal: Vector2 = contact.get_normal()
        var y: float = mover.global_position.y
        var expected_y: float = float(FLOOR_ROW * TILE_PX) - BODY_PX * 0.5
        if target == layer and normal.y < -0.8 and absf(y - expected_y) < 6.0:
            hit = true
            print("GODOT_PS5_M10B_TILE_CONTACT_OK tilemap=", target.get_name(),
                " normal=", normal, " y=", y)
        else:
            print("GODOT_PS5_M10B_TILE_FAIL_CONTACT target=", target, " normal=", normal, " y=", y)
            get_tree().quit(72)
            completed = true
            return
    if mover.global_position.y > 900.0:
        print("GODOT_PS5_M10B_TILE_FAIL_PASSTHROUGH y=", mover.global_position.y)
        get_tree().quit(73)
        completed = true
        return
    if tick >= MAX_TICKS:
        print("GODOT_PS5_M10B_TILE_FAIL_TIMEOUT tick=", tick)
        get_tree().quit(74)
        completed = true
    queue_redraw()

func _process(_delta: float) -> void:
    var now: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if now and not previous_x:
        print("GODOT_PS5_M10B_TILE_PAD_X")
    previous_x = now

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, Vector2(1920, 1080)), Color(0.016, 0.027, 0.062), true)
    if mover != null:
        draw_rect(Rect2(mover.position - Vector2(BODY_PX/2.0, BODY_PX/2.0),
                       Vector2(BODY_PX, BODY_PX)),
            Color(0.14, 1.0, 0.48) if hit else Color(0.11, 0.88, 1.0), true)
    draw_circle(Vector2(970, 130), 39,
        Color(0.14, 1.0, 0.48) if hit else Color(0.28, 0.33, 0.45))
