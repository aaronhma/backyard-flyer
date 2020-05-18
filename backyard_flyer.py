import argparse
import time
from enum import Enum

import numpy as np

from udacidrone import Drone
from udacidrone.connection import MavlinkConnection, WebSocketConnection  # noqa: F401
from udacidrone.messaging import MsgID


class States(Enum):
    MANUAL = 0
    ARMING = 1
    TAKEOFF = 2
    WAYPOINT = 3
    LANDING = 4
    DISARMING = 5


class BackyardFlyer(Drone):

    def __init__(self, connection):
        super().__init__(connection)
        self.target_position = np.array([0.0, 0.0, 0.0])
        self.trajectory = list()
        self.in_mission = True
        self.check_state = {}

        # initial state
        self.flight_state = States.MANUAL

        # TODO: Register all your callbacks here
        self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(MsgID.STATE, self.state_callback)

    def local_position_callback(self):
        """
        TODO: Implement this method

        This triggers when `MsgID.LOCAL_POSITION` is received and self.local_position contains new data
        """
        pass

    def velocity_callback(self):
        """
        TODO: Implement this method

        This triggers when `MsgID.LOCAL_VELOCITY` is received and self.local_velocity contains new data
        """
        pass

    def state_callback(self):
        """
        TODO: Implement this method

        This triggers when `MsgID.STATE` is received and self.armed and self.guided contain new data
        """
        pass

    def calculate_trajectory(self):
        """
        This function returns the trajectory
        that allows the drone to fly in a
        square.
        """
        print("Calculating trajectory...")
        self.trajectory.append([10, 0, 3])
        self.trajectory.append([10, 10, 3])
        self.trajectory.append([0, 10, 3])
        self.trajectory.append([0, 0, 3])
        
        return self.trajectory

    def arming_transition(self):
        """
        This function takes control of
        the drone, arms it (gets it ready for takeoff),
        then sets the home position to the current
        takeoff position and automatically
        transitions to the arming state.
        """
        print("arming transition")
        self.take_control()
        self.arm()
        
        global_position_x = self.global_position[0]
        global_position_y = self.global_position[1]
        global_position_z = self.global_position[2]
        
        self.set_home_position(global_position_x, global_position_y, global_position_z)
        self.flight_state = States.ARMING # Set the flight state to ARMING
        
    def takeoff_transition(self):
        """
        TODO: Fill out this method
        
        1. Set target_position altitude to 3.0m
        2. Command a takeoff to 3.0m
        3. Transition to the TAKEOFF state
        """
        print("takeoff transition")

    def waypoint_transition(self):
        """
        TODO: Fill out this method
    
        1. Command the next waypoint position
        2. Transition to WAYPOINT state
        """
        print("waypoint transition")

    def landing_transition(self):
        """
        This function commands the drone
        to land and automatically transitions
        to the landing state.
        """
        print("landing transition")
        self.land() # Land the drone
        self.flight_state = States.LANDING # Set the flight state to LANDING

    def disarming_transition(self):
        """
        This function commands the drone
        to disarm and automatically
        transitions to the disarming state.
        """
        print("disarm transition")
        self.disarm() # Disarm the drone
        self.flight_state = States.DISARMING # Set the flight state to DISARMING

    def manual_transition(self):
        """
        This method is provided
        
        1. Release control of the drone
        2. Stop the connection (and telemetry log)
        3. End the mission
        4. Transition to the MANUAL state
        """
        print("manual transition")

        self.release_control()
        self.stop()
        self.in_mission = False
        self.flight_state = States.MANUAL

    def start(self):
        """
        This method is provided
        
        1. Open a log file
        2. Start the drone connection
        3. Close the log file
        """
        print("Creating log file")
        self.start_log("Logs", "NavLog.txt")
        print("starting connection")
        self.connection.start()
        print("Closing log file")
        self.stop_log()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5760, help='Port number')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="host address, i.e. '127.0.0.1'")
    args = parser.parse_args()

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), threaded=False, PX4=False)
    # conn = WebSocketConnection('ws://{0}:{1}'.format(args.host, args.port))
    drone = BackyardFlyer(conn)
    time.sleep(2)
    drone.start()
