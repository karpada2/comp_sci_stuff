from vpython import *
import math

# +x - rightwards when camera at default
# +y - upwards when camera at default
# +z - towards camera at default

run = 9

if run == 1 or run < 0:
    ball = sphere(pos=vector(5, 0, 0), radius=1, color=color.orange)
    velocity = vector(4,0,0)
    arrow(pos=ball.pos, axis=velocity, color=color.green)
if run == 2 or run < 0:
    spheres = []
    for x in [-3, 3]:
        for y in [-3, 3]:
            for z in [-3, 3]:
                if x == -3:
                    spheres.append(sphere(pos=vector(x, y, z), radius=0.5, color=color.green))
                else:
                    spheres.append(sphere(pos=vector(x, y, z), radius=0.5, color=color.blue))
    arrow(pos=spheres[4].pos, axis=vector(0,0,0) - spheres[4].pos, color=color.red)
if run == 3 or run < 0:
    cylinder(pos=vector(-3, 0, 0), axis=vector(6, 0, 0), radius=0.25, color=color.cyan)
    cylinder(pos=vector(0, -3, 0), axis=vector(0, 6, 0), radius=0.25, color=color.green)
    cylinder(pos=vector(0, 0, -3), axis=vector(0, 0, 6), radius=0.25, color=color.magenta)
if run == 4 or run < 0:
    box(pos=vector(0, 0, 0), length=10, width=1, height=1, color=color.cyan)
    box(pos=vector(0, 0, 0), length=1, width=10, height=1, color=color.green)
    box(pos=vector(0, 0, 0), length=1, width=1, height=10, color=color.magenta)
if run == 5 or run < 0:
    ball_positions = [
            vector(2, 2, 0),
            vector(2, -2, 0),
            vector(-2, -2, 0),
            # vector(-2, 2, 0)
        ]
    
    for i in range(len(ball_positions)):
        sphere(pos=ball_positions[i], radius=0.5, color=color.green)
        arrow(pos=ball_positions[i], axis=ball_positions[i-1] - ball_positions[i], color=color.red)
if run == 6 or run < 0:
    for i in range(-10, 11):
        if i != 0:
            box(pos=vector(i, 0, 0), length=0.5, width=0.5, height=0.5, color=color.cyan)
            box(pos=vector(0, i, 0), length=0.5, width=0.5, height=0.5, color=color.green)
            box(pos=vector(0, 0, i), length=0.5, width=0.5, height=0.5, color=color.magenta)
        if i == 0:
            box(pos=vector(0, 0, 0), length=0.5, width=0.5, height=0.5)
if run == 7 or run < 0:
    amount_of_circles = 20
    distance = 8
    radius = 1
    for i in range(amount_of_circles):
        x = distance
        y = 0
        theta = (i/amount_of_circles)*(2*math.pi)
        a = (x*math.cos(theta)) - (y*math.sin(theta))
        b = (x*math.sin(theta)) + (y*math.cos(theta))
        sphere(pos=vector(a, b, 0), radius=radius, color=color.cyan)
        sphere(pos=vector(a, 0, b), radius=radius, color=color.green)
        sphere(pos=vector(0, a, b), radius=radius, color=color.magenta)
if run == 8 or run < 0:
    ### parameters ###
    dt = 0.01

    ### initialization ###
    start_position = vector(0, 0, 0)
    start_velocity = vector(-0.5, 0, 0)
    cart_size = vector(0.2, 0.1, 0.1)
    track_size = vector(4.0+cart_size.x, 0.2, 0.2)

    ### system creation ###
    track = box(pos=vector(0, 0, 0), size=track_size, color=color.orange)

    cart = box(pos=vector(start_position.x - (cart_size.x/2) + (track_size.x/2), start_position.y + (cart_size.y/2) + (track_size.y/2), start_position.z), size=vector(0.2,0.1,0.1), color=color.gray(0.7))

    x_t = gcurve(color=color.blue)

    ### Time Evolution ###
    t = 0
    while t < 8:
        rate(1/dt)
        t += dt
        cart.pos = cart.pos + start_velocity*dt
        
        x_t.plot(pos=(t, cart.pos.x))
if run == 9 or run < 0:
    ### parameters ###
    dt = 0.01

    ### initialization ###
    start_position = vector(2.5, 0, 0)
    start_velocity = vector(0.5, 0, 0)
    cart_size = vector(0.2, 0.1, 0.1)
    cart_mass = 1

    track_size = vector(4.0+cart_size.x, 0.2, 0.2)

    wall_x_value = 1.5
    wall_size = vector(track_size.x-(wall_x_value*2), track_size.y, track_size.z)
    wall_k = 20000

    ### system creation ###

    track = box(pos=vector(0, 0, 0), size=track_size, color=color.orange, opacity=0.5)

    cart = box(pos=vector(start_position.x + (cart_size.x/2) - (track_size.x/2), start_position.y + (cart_size.y/2) + (track_size.y/2), start_position.z), size=vector(0.2,0.1,0.1), color=color.gray(0.7))
    wall = box(pos=vector(wall_x_value+(wall_size.x/2), wall_size.y, 0), size=wall_size, color=color.cyan, opcaity=0)
    # spring = helix()

    x_t = gcurve(color=color.blue)

    ### Time Evolution ###
    t = 0
    cart_velocity = vector(start_velocity.x, start_velocity.y, start_velocity.z)
    while t < 10:
        rate(0.2/dt)
        t += dt
        if cart.pos.x + (cart_size.x/2) > wall_x_value:
            wall_force = -((cart.pos.x+(cart_size.x/2)) - wall_x_value)*wall_k
            wall_acceleration = wall_force/cart_mass
            cart_velocity.x += wall_acceleration*dt

        cart.pos = cart.pos + cart_velocity*dt

        if cart.pos.x > 1.4:
            print(cart.pos.x)
        
        x_t.plot(pos=(t, cart.pos.x))
if run == 10 or run < 0:
    def rotate_2d_vector(x, y, theta):
        a = (x*math.cos(theta)) - (y*math.sin(theta))
        b = (x*math.sin(theta)) + (y*math.cos(theta))
        return (a, b)
    
    ### parameters ###
    dt = 0.01

    ### initialization ###
    mass = 2

    length = 2

    arm_1_current_angle = 0.2*math.pi
    arm_2_current_angle = -0.3*math.pi

    x1 = 0.5*length*math.sin(arm_1_current_angle)
    y1 = -0.5*length*math.cos(arm_1_current_angle)

    x2 = length*(math.sin(arm_1_current_angle) + (0.5*math.sin(arm_2_current_angle)))
    y2 = -length*(math.cos(arm_1_current_angle) + (0.5*math.cos(arm_2_current_angle)))

    ### system creation ###

    x, y = rotate_2d_vector(0, length, arm_1_current_angle)
    arm_1 = cylinder(pos=vector(0, 0, 0), axis=vector(x, y, 0), radius=0.5)

    x, y = rotate_2d_vector(0, length, arm_2_current_angle)
    arm_2 = cylinder(pos=arm_1.axis, axis=vector(x, y, 0), radius=0.5)


    ### Time Evolution ###
    t = 0
    while t < 10:
        rate(0.2/dt)
        t += dt
        