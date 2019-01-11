import numpy as np
from physics_sim import PhysicsSim


class HoverTaskVelocity():
    def __init__(self, init_pose=None, init_velocities=None, init_angle_velocities=None, runtime=5.):
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 

        self.state_size = 6
        self.action_low = 350
        self.action_high = 450
        self.action_size = 4

        self.target_pos = np.copy(init_pose[:3])

    def get_reward(self):
        pos_z = self.sim.pose[2]

        # Bad reward if the drone crashed
        if pos_z <= 0.:
            return 0.

        # Calculate distance and velocity
        distance = np.sqrt(sum(np.power(self.sim.pose[:3] - self.target_pos, 2)))
        velocity = np.sqrt(sum(np.power(self.sim.v, 2)))
        
        # Normalize distance and velocity
        distance = np.clip(distance / 10., 0, 1)
        velocity = np.clip(velocity / 10., 0, 1)
                        
        # Calculate reward
        dist_reward = 1. - distance ** .4
        vel_discount = (1. - max(velocity, .1)) ** (1. / max(distance, .1))
        reward = vel_discount * dist_reward

        return reward
        
    def step(self, rotor_speeds):
        done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
        reward = self.get_reward() 
        next_state = np.concatenate([self.sim.pose[:3], self.sim.v])
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose[:3], self.sim.v])
        return state


class HoverTaskLimit():
    def __init__(self, init_pose=None, init_velocities=None, init_angle_velocities=None, runtime=5., max_distance=5.):
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 

        self.state_size = 3
        self.action_low = 350
        self.action_high = 450
        self.action_size = 4

        self.target_pos = np.copy(init_pose[:3])
        self.max_distance = max_distance

    def get_reward(self):
        pos_z = self.sim.pose[2]
        distance = np.sqrt(sum(np.power(self.sim.pose[:3] - self.target_pos, 2)))
        
        # Bad reward if the drone crashed
        if pos_z <= 0.0:
            return -10.

        reward = 1 - (distance / self.max_distance) ** 0.4
        reward = np.clip(reward, 0, 1)
                        
        return reward

    def step(self, rotor_speeds):
        done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities

        #done = done or self.sim.pose[2] >= self.target_pos[2]
        
        reward = self.get_reward() 
        next_state = self.sim.pose[:3]
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = self.sim.pose[:3]
        return state


class HoverTask():
    def __init__(self, init_pose=None, init_velocities=None, init_angle_velocities=None, runtime=5., target_pos=None):
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 

        self.state_size = 3
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else self.sim.pose[:3]

    def get_reward3(self):
        pos_z = self.sim.pose[2]
        distance = np.sqrt(sum(np.power(self.sim.pose[:3] - self.target_pos, 2)))
        
        # Bad reward if the drone crashed
        if pos_z <= 0.0:
            return -1000.
                        
        # Normalize distance
        reward = 2. / (1 + np.exp(1. * distance - 6.)) - 1.
        return reward

    def get_reward(self):
        pos_z = self.sim.pose[2]
        distance = np.sqrt(sum(np.power(self.sim.pose[:3] - self.target_pos, 2)))
        
        # Bad reward if the drone crashed
        if pos_z <= 0.:
            return 0.
                        
        # Normalize distance
        reward = 1. / (1 + np.exp(1.0 * distance - 6.0))
        return reward

    def get_reward1(self):
        pos_z = self.sim.pose[2]
        distance = np.sqrt(sum(np.power(self.sim.pose[:3] - self.target_pos, 2)))
        
        # Bad reward if the drone crashed
        if pos_z <= 0.:
            return 0.
                        
        # Normalize distance
        reward = 1. - np.tanh(0.30 * distance)
        return reward

    def get_reward1(self):
        pos_z = self.sim.pose[2]
        distance = np.sqrt(sum(np.power(self.sim.pose[:3] - self.target_pos, 2)))
        
        # Bad reward if the drone crashed
        if pos_z <= 0.:
            return 0.
                        
        # Normalize distance
        reward = 1. - np.tanh(0.30 * distance)
        return reward
        
    def step(self, rotor_speeds):
        done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities

        #done = done or self.sim.pose[2] >= self.target_pos[2]
        
        reward = self.get_reward() 
        next_state = self.sim.pose[:3]
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = self.sim.pose[:3]
        return state


class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 3

        self.state_size = self.action_repeat * 6
        self.action_low = 0
        self.action_high = 900
        self.action_size = 4

        # Goal
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        reward = 1.-.3*(abs(self.sim.pose[:3] - self.target_pos)).sum()
        return reward

    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
            reward += self.get_reward() 
            pose_all.append(self.sim.pose)
        next_state = np.concatenate(pose_all)
        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode."""
        self.sim.reset()
        state = np.concatenate([self.sim.pose] * self.action_repeat) 
        return state