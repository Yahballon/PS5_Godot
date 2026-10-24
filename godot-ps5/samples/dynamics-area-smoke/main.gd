extends Node2D

# M10a: Authentic Godot 4.7.2 PhysicsServer2D body movement, contacts, and
# Area2D monitoring. No manually scripted motion, bounce, overlap or gravity.
# Screen geometry is only for display; shapes drive all collision logic.

const BALL_X: float = 800.0
const BALL_START_Y: float = 180.0
const BALL_R: float = 36.0
const SENSOR_Y: float = 510.0
const SENSOR_H: float = 170.0
const FLOOR_Y: float = 845.0
const FLOOR_H: float = 64.0
const FLOOR_TOP: float = FLOOR_Y - FLOOR_H * 0.5
const EXPECTED_REST_Y: float = FLOOR_TOP - BALL_R
const TOLERANCE: float = 8.0
const MAX_TICKS: int = 780
const REST_TICKS_REQUIRED: int = 75

var ball: RigidBody2D
var floor: StaticBody2D
var sensor: Area2D
var frame_count: int = 0
var stable_frames: int = 0
var entered_area: bool = false
var exited_area: bool = false
var hit_floor: bool = false
var finished: bool = false
var x_previous: bool = false

func _ready() -> void:
    print("GODOT_PS5_M10A_BOOT")
    floor = StaticBody2D.new()
    floor.name = "CollisionFloor"
    floor.position = Vector2(BALL_X, FLOOR_Y)
    floor.collision_layer = 1
    floor.collision_mask = 2
    var floor_shape := CollisionShape2D.new()
    var floor_rect := RectangleShape2D.new()
    floor_rect.size = Vector2(920, FLOOR_H)
    floor_shape.shape = floor_rect
    floor.add_child(floor_shape)
    add_child(floor)

    sensor = Area2D.new()
    sensor.name = "RealAreaTrigger"
    sensor.position = Vector2(BALL_X, SENSOR_Y)
    sensor.collision_layer = 0
    sensor.collision_mask = 2
    sensor.monitoring = true
    sensor.monitorable = true
    var trigger_collision := CollisionShape2D.new()
    var trigger_rect := RectangleShape2D.new()
    trigger_rect.size = Vector2(540, SENSOR_H)
    trigger_collision.shape = trigger_rect
    sensor.add_child(trigger_collision)
    sensor.body_entered.connect(_area_entered)
    sensor.body_exited.connect(_area_exited)
    add_child(sensor)

    ball = RigidBody2D.new()
    ball.name = "GravityBody"
    ball.position = Vector2(BALL_X, BALL_START_Y)
    ball.gravity_scale = 1.0
    ball.mass = 1.0
    ball.collision_layer = 2
    ball.collision_mask = 1
    ball.contact_monitor = true
    ball.max_contacts_reported = 8
    ball.can_sleep = true
    var ball_collision := CollisionShape2D.new()
    var sphere := CircleShape2D.new()
    sphere.radius = BALL_R
    ball_collision.shape = sphere
    ball.add_child(ball_collision)
    ball.body_entered.connect(_rigid_contact)
    add_child(ball)
    print("GODOT_PS5_M10A_BODIES_READY")
    queue_redraw()

func _area_entered(body: Node2D) -> void:
    if body != ball or entered_area:
        return
    entered_area = true
    print("GODOT_PS5_M10A_AREA_ENTER_OK y=", ball.global_position.y)

func _area_exited(body: Node2D) -> void:
    if body != ball or exited_area:
        return
    exited_area = true
    print("GODOT_PS5_M10A_AREA_EXIT_OK y=", ball.global_position.y)

func _rigid_contact(body: Node) -> void:
    if body != floor or hit_floor:
        return
    hit_floor = true
    print("GODOT_PS5_M10A_RIGID_CONTACT_OK y=", ball.global_position.y)

func _physics_process(_delta: float) -> void:
    frame_count += 1
    if finished:
        return
    if frame_count == 25 and ball.global_position.y <= BALL_START_Y + 4.0:
        _fail("GRAVITY_UNAVAILABLE", 51)
        return
    if ball.global_position.y > FLOOR_TOP + 130.0:
        _fail("FLOOR_PASSTHROUGH", 52)
        return
    if frame_count >= MAX_TICKS:
        _fail("TIMEOUT", 53)
        return

    # This is NOT a collision solver. We merely observe the engine's body
    # position and velocity once all three genuine signals have fired.
    var position_ok: bool = absf(ball.global_position.y - EXPECTED_REST_Y) < TOLERANCE
    var speed_ok: bool = ball.linear_velocity.length() < 5.0
    if entered_area and exited_area and hit_floor and position_ok and speed_ok:
        stable_frames += 1
        if stable_frames >= REST_TICKS_REQUIRED:
            finished = true
            print("GODOT_PS5_M10A_TEST_PASS ticks=", frame_count,
                  " rest_y=", ball.global_position.y,
                  " velocity=", ball.linear_velocity)
            get_tree().quit(0)
    else:
        stable_frames = 0
    queue_redraw()

func _fail(reason: String, code: int) -> void:
    finished = true
    print("GODOT_PS5_M10A_FAIL_", reason,
          " frame=", frame_count, " y=", ball.global_position.y,
          " entered=", entered_area, " exited=", exited_area,
          " floor_hit=", hit_floor)
    get_tree().quit(code)

func _process(_delta: float) -> void:
    var x_now: bool = Input.is_joy_button_pressed(0, JOY_BUTTON_A)
    if x_now and not x_previous:
        print("GODOT_PS5_M10A_DUALSENSE_X")
    x_previous = x_now

func _draw() -> void:
    draw_rect(Rect2(0, 0, 1920, 1080), Color(0.014, 0.026, 0.056), true)
    draw_rect(Rect2(BALL_X - 270, SENSOR_Y - SENSOR_H * 0.5, 540, SENSOR_H),
              Color(0.28, 0.85, 0.98, 0.3), true)
    draw_rect(Rect2(BALL_X - 270, SENSOR_Y - SENSOR_H * 0.5, 540, SENSOR_H),
              Color(0.19, 0.86, 1.0), false, 8.0)
    draw_rect(Rect2(BALL_X - 460, FLOOR_TOP, 920, FLOOR_H),
              Color(0.95, 0.25, 0.54), true)
    if ball != null:
        var ball_color: Color = Color(0.16, 0.98, 0.45) if finished or (entered_area and exited_area and hit_floor) else Color(0.96, 0.84, 0.23)
        draw_circle(ball.position, BALL_R, ball_color)
    # Three check lights, each one only switches after a true physics signal.
    draw_circle(Vector2(640, 115), 25, Color(0.25, 1.0, 0.48) if entered_area else Color(0.3, 0.35, 0.40))
    draw_circle(Vector2(800, 115), 25, Color(0.25, 1.0, 0.48) if exited_area else Color(0.3, 0.35, 0.40))
    draw_circle(Vector2(960, 115), 25, Color(0.25, 1.0, 0.48) if hit_floor else Color(0.3, 0.35, 0.40))
