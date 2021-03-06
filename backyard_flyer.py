import argparse
import time
import enum

import numpy as np

import udacidrone
# temporary workaround to udacidrone connection module error:
from udacidrone.connection import MavlinkConnection # WebSocketConnection

class States(enum.Enum):
    MANUAL = 0
    ARMING = 1
    TAKEOFF = 2 
    WAYPOINT = 3
    LANDING = 4
    DISARMING = 5


class BackyardFlyer(udacidrone.Drone):

    def __init__(self, connection):
        super().__init__(connection)
        self.target_position = np.array([0.0, 0.0, 0.0])
        self.trajectory = list()
        self.in_mission = True
        self.check_state = {}
        
        # Waypoint counter
        self.waypoint = 0
        self.prev_waypoint = 1
        self.next_waypoint = 2
        
        # Get the flight trajectory
        self.calculate_trajectory()

        # initial state
        self.flight_state = States.MANUAL

        # Register all the callbacks for the drone
        self.register_callback(udacidrone.messaging.MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(udacidrone.messaging.MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(udacidrone.messaging.MsgID.STATE, self.state_callback)

    def local_position_callback(self):
        """
        This triggers when `udacidrone.messaging.MsgID.LOCAL_POSITION` is received and self.local_position contains new data
        """
        if self.flight_state == States.TAKEOFF:
            altitude = -1.0 * self.local_position[2]
            
            if altitude > 0.95 * self.target_position[2]:
                self.landing_transition()

    def velocity_callback(self):
        """
        This triggers when `udacidrone.messaging.MsgID.LOCAL_VELOCITY` is received and self.local_velocity contains new data
        """
        if self.flight_state == States.LANDING:
            if (self.global_position[2] - self.global_home[2] < 0.1) and abs(self.local_position[2] < 0.01):
                self.disarming_transition()

    def state_callback(self):
        """
        This triggers when `udacidrone.messaging.MsgID.STATE` is received and self.armed and self.guided contain new data
        """
        if not self.in_mission:
            return
        if self.flight_state == States.MANUAL:
            self.arming_transition()
        elif self.flight_state == States.ARMING:
            if self.armed:
                self.takeoff_transition()
        elif self.flight_state == States.DISARMING:
            if not self.armed:
                self.manual_transition()
        # TODO: create waypoint callback

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
        This function changes the target
        z-axis (height) to 3 meters,
        then takesoff to the target altitude,
        and automatically transitions to
        the takeoff state.
        """
        print("takeoff transition")
        target_altitude = 3.0 # 3.0 meters
        self.target_position[2] = target_altitude # change the z-axis (height) to 3 meters
        self.takeoff(target_altitude) # Takeoff 3 meters
        self.flight_state = States.TAKEOFF # Set the flight state to TAKEOFF

    def waypoint_transition(self):
        """
        TODO: Fill out this method
    
        1. Command the next waypoint position
        2. Transition to WAYPOINT state
        """
        print("waypoint transition")
        print("current waypoint: {}, next waypoint: {}".format(self.prev_waypoint, self.next_waypoint))
        self.prev_waypoint += 1
        self.next_waypoint += 1
        waypoint = self.trajectory[self.waypoint]
        # self.command(waypoint)
        self.waypoint += 1
        self.flight_state = States.WAYPOINT # Set the flight state to WAYPOINT

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
    parser.add_argument('--port', type = int, default = 5760, help = "The simulator port number")
    parser.add_argument('--host', type = str, default = '127.0.0.1', help = "The simulator host address, i.e. '127.0.0.1'")
    args = parser.parse_args()

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), threaded = False, PX4 = False)
    # conn = WebSocketConnection('ws://{0}:{1}'.format(args.host, args.port))
    drone = BackyardFlyer(conn)
    time.sleep(2)
    drone.start()
