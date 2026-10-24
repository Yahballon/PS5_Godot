extends Node2D

# M9a: *real* upstream Godot 4.7.2 collision acceptance.
# Draw functions are visual only. All motion and contact use CharacterBody2D,
# StaticBody2D, CollisionShape2D, and CharacterBody2D.move_and_collide().
# NEVER substitute hand-coded x-axis bounce for successful physics evidence.

const LIMIT_FRAMES: int = 720
const WALL_X: float = 1170.0
const WALL_W: float = 80.0
const BODY_W: float = 72.0
const SPEED: float = 600.0
const START_X: float = 410.0
const CONTACT_EXIT_DELAY: int = 300

var mover: CharacterBody2D
var wall: StaticBody2D
var physics_frames: int = 0
var contact_frames: int = 0
var contact_verified: bool = false
var failed: bool = false
var previous_x: bool = false

func _ready() -> void:
    print("GODOT_PS5_M9_BOOT")
    print("GODOT_PS5_M9_USING_CHARACTERBODY2D_STATICBODY2D_COLLISIONSHAPE2D")
    wall = StaticBody2D.new()
    wall.name = "TestWall"
    wall.position = Vector2(WALL_X, 540.0)
    var wall_collision := CollisionShape2D.new()
    var wall_rect := RectangleShape2D.new()
    wall_rect.size = Vector2(WALL_W, 520.0)
    wall_collision.shape = wall_rect
    wall.add_child(wall_collision)
    add_child(wall)

    mover = CharacterBody2D.new()
    mover.name = "TestCharacter"
    mover.position = Vector2(START_X, 540.0)
    mover.collision_layer = 1
    mover.collision_mask = 1
    var mover_collision := CollisionShape2D.new()
    var mover_rect := RectangleShape2D.new()
    mover_rect.size = Vector2(BODY_W, BODY_W)
    mover_collision.shape = mover_rect
    mover.add_child(mover_collision)
    add_child(mover)
    print("GODOT_PS5_M9_BODIES_READY")
    queue_redraw()

func _physics_process(delta: float) -> void:
    physics_frames += 1
    if not contact_verified and not failed:
        var movement: Vector2 = Vector2(SPEED * minf(delta, 0.05), 0.0)
        var collision: KinematicCollision2D = mover.move_and_collide(movement)
        if collision != null:
            var hit_wall: bool = collision.get_collider() == wall
            var normal: Vector2 = collision.get_normal()
            var stop_x: float = mover.global_position.x
            var max_x: float = WALL_X - WALL_W * 0.5 - BODY_W * 0.5
            if hit_wall and normal.x < -0.8 and stop_x <= max_x + 2.0 and stop_x >= max_x - 5.0:
                contact_verified = true
                contact_frames = 0
                print("GODOT_PS5_M9_REAL_COLLISION_OK x=", stop_x, " normal=", normal)
            else:
                failed = true
                print("GODOT_PS5_M9_COLLISION_INVALID hit_wall=", hit_wall,
                      " x=", stop_x, " normal=", normal)
                get_tree().quit(41)
                return
        if mover.position.x > WALL_X + WALL_W:
            failed = true
            print("GODOT_PS5_M9_NO_COLLISION_PHYSICS_UNAVAILABLE x=", mover.position.x)
            get_tree().quit(42)
            return
    elif contact_verified:
        contact_frames += 1
        if contact_frames == CONTACT_EXIT_DELAY:
            print("GODOT_PS5_M9_TEST_PASS physics_frames=", physics_frames)
            get_tree().quit(0)
    if physics_frames >= LIMIT_FRAMES:
        print("GODOT_PS5_M9_TIMEOUT physics_frames=", physics_frames)
        get_tree().quit(43)

func _process(_delta: float) -> void:
    var x_now: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if x_now and not previous_x:
        print("GODOT_PS5_M9_DUALSENSE_X")
    previous_x = x_now
    queue_redraw()

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, Vector2(1920, 1080)), Color(0.015, 0.028, 0.065), true)
    for n in range(16):
        draw_rect(Rect2(100.0 + float(n) * 108.0, 925, 54, 9),
                  Color(0.18, 0.24, 0.35), true)
    # The wall rectangle is only a visualization of StaticBody2D's actual shape.
    draw_rect(Rect2(WALL_X - WALL_W * 0.5, 280, WALL_W, 520),
              Color(0.96, 0.28, 0.55), true)
    # Mover position is controlled EXCLUSIVELY by move_and_collide().
    if mover != null:
        var tint: Color = Color(0.15, 1.0, 0.49) if contact_verified \
            else Color(0.15, 0.90, 0.99)
        draw_rect(Rect2(mover.position.x - BODY_W * 0.5, 540 - BODY_W * 0.5,
                  BODY_W, BODY_W), tint, true)
    if contact_verified:
        # Green marker is displayed ONLY when the real engine reports contact.
        draw_circle(Vector2(960, 160), 52, Color(0.15, 0.98, 0.38))
    elif failed:
        draw_circle(Vector2(960, 160), 52, Color(1.0, 0.10, 0.13))
    else:
        draw_circle(Vector2(960, 160), 52, Color(0.12, 0.6, 0.94))
