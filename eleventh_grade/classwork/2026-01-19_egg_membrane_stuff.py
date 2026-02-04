from vpython import color, vector
import vpython
import random
import numpy as np

# --- UTILITY FUNCTIONS ---
def abs_vector(a: vector) -> vector:
    return vector(abs(a.x), abs(a.y), abs(a.z))

# --- CLASSES ---
class Molecule:
    def __init__(self, start_position, start_velocity, collision_layer, sphere_radius, sphere_color):
        self.sphere = vpython.sphere(pos=start_position, radius=sphere_radius, color=sphere_color)
        self.velocity = start_velocity
        self.collision_layer = collision_layer
    
    def update(self, dt: float):
        self.sphere.pos += self.velocity * dt

    def get_velocity(self):
        return self.velocity
    
    def set_velocity(self, new_velocity: vector):
        self.velocity = new_velocity
    
    def is_can_collide(self, another_collision_layer) -> bool:
        return another_collision_layer in self.collision_layer

class Plane:
    current_tick_collisions_velocity_sums = {}

    def __init__(self, collision_direction, distance, collision_layer, size):
        collision_directions = {
            "-x": vector(-1, 0, 0), "+x": vector(1, 0, 0),
            "-y": vector(0, -1, 0), "+y": vector(0, 1, 0),
            "-z": vector(0, 0, -1), "+z": vector(0, 0, 1),
        }
        self.collision_vector = collision_directions[collision_direction]
        self.distance = distance
        self.collision_layer = collision_layer
        
        # We create a box for static walls; for the membrane, the Membrane class will manage visuals
        self.box = vpython.box(pos=self.collision_vector * distance, 
                               size=(((vector(1,1,1) - abs_vector(self.collision_vector)) * size * 2) + 
                                     (abs_vector(self.collision_vector) * 0.5)), 
                               opacity=0.2)
        
        if collision_layer not in Plane.current_tick_collisions_velocity_sums:
            Plane.current_tick_collisions_velocity_sums[collision_layer] = {"velocity": vector(0, 0, 0)}

    def check_collision_and_change_molecule(self, molecule: Molecule, wall_velocity=vector(0,0,0)):
        if molecule.is_can_collide(self.collision_layer):
            pos_on_axis = molecule.sphere.pos.dot(self.collision_vector)
            sphere_edge = pos_on_axis + molecule.sphere.radius
            
            if sphere_edge >= self.distance:
                relative_v = (molecule.get_velocity() - wall_velocity).dot(self.collision_vector)
                
                if relative_v > 0:
                    # Momentum transfer to the layer
                    Plane.current_tick_collisions_velocity_sums[self.collision_layer]["velocity"] += self.collision_vector * relative_v
                    
                    # Reflection
                    new_v = molecule.get_velocity() - 2 * relative_v * self.collision_vector
                    molecule.set_velocity(new_v)

                    # Positional correction
                    penetration = sphere_edge - self.distance
                    molecule.sphere.pos -= self.collision_vector * (penetration + 0.1)

class Membrane:
    def __init__(self, x_center, thickness, size, collision_layer):
        self.thickness = thickness
        self.visual = vpython.box(pos=vector(x_center, 0, 0), 
                                  size=vector(thickness, size*2, size*2), 
                                  color=color.red, opacity=0.4)
        
        # Inward-facing normal vectors
        self.right_face_normal = vector(1, 0, 0)  # Handles molecules at x > center
        self.left_face_normal = vector(-1, 0, 0)  # Handles molecules at x < center
        self.collision_layer = collision_layer

        if collision_layer not in Plane.current_tick_collisions_velocity_sums:
            Plane.current_tick_collisions_velocity_sums[collision_layer] = {"velocity": vector(0, 0, 0)}

    def update_membrane(self, displacement):
        self.visual.pos += displacement

    def check_collision(self, molecule, wall_velocity):
        is_on_right = molecule.sphere.pos.x > self.visual.pos.x
        normal = self.right_face_normal if is_on_right else self.left_face_normal
        boundary_x = self.visual.pos.x + (self.thickness/2 if is_on_right else -self.thickness/2)
        
        # Distance from membrane center along the x-axis
        dist_x = (molecule.sphere.pos.x - self.visual.pos.x) * normal.x
        
        # Check if molecule edge is inside the membrane face
        if dist_x < (self.thickness / 2 + molecule.sphere.radius):
            v_rel = (molecule.get_velocity() - wall_velocity).dot(normal)
            
            if v_rel < 0: # Moving toward the membrane
                # Calculate velocity change
                old_v = molecule.get_velocity()
                new_v = old_v - 2 * v_rel * normal
                molecule.set_velocity(new_v)
                
                # MOMENTUM TRANSFER: Delta_V of the molecule is (new_v - old_v)
                # The impulse on the wall is the negative of the molecule's change
                impulse = -(new_v - old_v)
                Plane.current_tick_collisions_velocity_sums[self.collision_layer]["velocity"] += impulse

                # EJECTION: Push molecule out so it doesn't "tunnel" or get crushed
                overlap = (self.thickness / 2 + molecule.sphere.radius) - dist_x
                molecule.sphere.pos += normal * (overlap + 0.01)

# --- SETUP ---
t, dt = 0, 0.005
default_distance = 50

# Static Walls
planes = []
for axis in ["x", "y", "z"]:
    for sign in ["-", "+"]:
        planes.append(Plane(sign + axis, default_distance, 1, default_distance))

membrane_thickness = 6.0
# Membrane Partition
membrane = Membrane(x_center=0, thickness=membrane_thickness, size=default_distance, collision_layer=2)

proportion = 1/20
molecule_amount = 300
molecule_velocity = 30

molecules = []
for i in range(molecule_amount):
    side = 1 if i >= molecule_amount*proportion else -1
    # Start molecules well away from the 6-unit thick membrane
    x_start = side * (random.uniform(10, 45))
    molecules.append(Molecule(vector(x_start, random.uniform(-40, 40), random.uniform(-40, 40)), 
                              vector((random.random()-0.5), (random.random()-0.5), (random.random()-0.5)).norm()*molecule_velocity, 
                              [1, 2], 1.5, color.green))

presure_scene = vpython.graph(title="Pressure graph", xtitle="Time", ytitle="Pressure")

# Create two distinct curves with different colors
curve_left = vpython.gcurve(color=color.red, label="Left Side")
curve_right = vpython.gcurve(color=color.blue, label="Right Side")

pos_scene = vpython.graph(title="Membrane position", xtitle="Time", ytitle="X position")

curve_position = vpython.gcurve(color=color.black, label="Position")

current_v = vector(0,0,0)
area = (default_distance * 2)**2
momentum_L = 0
momentum_R = 0
graphing_frequency = 500
velocity_scaling_frequency = 100
# --- PHYSICAL CONSTANTS ---
mass = 200.0   # High mass prevents "jitter" and teleporting
damping = 0.998 # High damping helps it settle into equilibrium
sub_steps = 4   # Higher sub-stepping prevents molecules from passing through
dt_sub = dt / sub_steps

while t < 1000:
    vpython.rate(1000)
    
    for _ in range(sub_steps):
        t += dt_sub
        
        # 1. Update Membrane Position (Direct addition of velocity)
        membrane.update_membrane(current_v * dt_sub)
        
        # 2. Hard Stop container boundaries
        limit = default_distance - (membrane.thickness / 2 + 1)
        if abs(membrane.visual.pos.x) > limit:
            membrane.visual.pos.x = (limit if membrane.visual.pos.x > 0 else -limit)
            current_v.x = 0
        
        # 3. Physics
        for m in molecules:
            # Determine side for pressure tracking
            on_right = m.sphere.pos.x > membrane.visual.pos.x
            
            for p in planes: 
                p.check_collision_and_change_molecule(m)
            
            # Tracking momentum transfer
            pre_impulse = Plane.current_tick_collisions_velocity_sums[2]["velocity"].x
            membrane.check_collision(m, current_v)
            post_impulse = Plane.current_tick_collisions_velocity_sums[2]["velocity"].x
            
            # Sum the magnitude of impulse for pressure calculation
            mag = abs(post_impulse - pre_impulse)
            if on_right: momentum_R += mag
            else: momentum_L += mag
            
            m.update(dt_sub)

        # 4. Membrane Velocity Update (F = ma integration)
        impulse_vec = Plane.current_tick_collisions_velocity_sums[2]["velocity"]
        current_v += (impulse_vec / mass)
        current_v *= damping 
        
        # Reset impulses per sub-step
        Plane.current_tick_collisions_velocity_sums[1]["velocity"] = vector(0,0,0)
        Plane.current_tick_collisions_velocity_sums[2]["velocity"] = vector(0,0,0)

    # 5. Velocity Scaling
    if int(t/dt) % velocity_scaling_frequency == 0:
        for m in molecules:
            current_speed = m.velocity.mag
            if current_speed != 0:
                # Scale the velocity vector to match the target speed
                m.velocity = m.velocity * (molecule_velocity / current_speed)

    # 6. Graphing
    curve_position.plot(pos=(t, membrane.visual.pos.x / (default_distance - (membrane_thickness/2))))

    if int(t/dt) % graphing_frequency == 0:
        # Average pressure over the graphing_frequency steps
        p_L = momentum_L / (area * dt * graphing_frequency)
        p_R = momentum_R / (area * dt * graphing_frequency)
        curve_left.plot(pos=(t, p_L))
        curve_right.plot(pos=(t, p_R))
        momentum_L, momentum_R = 0, 0
    