#!/usr/bin/env python3
import rospy
import numpy as np
import tf2_ros
import tf2_geometry_msgs
import time
from nav_msgs.msg import OccupancyGrid, Path
from geometry_msgs.msg import PoseStamped
from astar import AStarPlanner
from dijkstra import DijkstraPlanner
from greedy import GreedyPlanner

class PlannerNode:
    def __init__(self):
        rospy.init_node("custom_planner")

        self.map = None
        self.resolution = None
        self.origin = None

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)

        rospy.Subscriber("/map", OccupancyGrid, self.map_callback)
        rospy.Subscriber("/goal", PoseStamped, self.goal_callback)

        self.path_pub = rospy.Publisher("/planned_path", Path, queue_size=1)

        self.algorithm = rospy.get_param("~algorithm", "astar")
        rospy.loginfo(f"[Planner] Algorithme utilisé : {self.algorithm}")

    def map_callback(self, msg):
        self.resolution = msg.info.resolution
        self.origin = (msg.info.origin.position.x, msg.info.origin.position.y)
        grid = np.array(msg.data, dtype=np.int8).reshape((msg.info.height, msg.info.width))
        # 0 = libre, 100 = obstacle, -1 = inconnue
        # On interdit explicitement les cellules inconnues pour la planification
        self.map = np.where(grid == 0, 0, 1)

    def get_robot_pose_in_map(self):
        try:
            tf = self.tf_buffer.lookup_transform(
                "map", "base_link", rospy.Time(0), rospy.Duration(1.0)
            )
            pose = PoseStamped()
            pose.header.frame_id = "base_link"
            pose.pose.orientation.w = 1.0
            pose_in_map = tf2_geometry_msgs.do_transform_pose(pose, tf)
            x = pose_in_map.pose.position.x
            y = pose_in_map.pose.position.y
            return x, y
        except Exception as e:
            rospy.logwarn(f"[Planner] Impossible de récupérer la pose du robot : {e}")
            return None

    def goal_callback(self, msg):
        if self.map is None:
            rospy.logwarn("[Planner] Carte non reçue.")
            return

        robot_pose = self.get_robot_pose_in_map()
        if robot_pose is None:
            rospy.logwarn("[Planner] Pose robot indisponible.")
            return

        start = self.world_to_grid(robot_pose[0], robot_pose[1])
        goal = self.world_to_grid(msg.pose.position.x, msg.pose.position.y)

        if not self.is_cell_free(start):
            rospy.logwarn(f"[Planner] Start invalide ou occupé: {start}")
            return
        if not self.is_cell_free(goal):
            rospy.logwarn(f"[Planner] Goal invalide ou occupé: {goal}")
            return

        if self.algorithm == "astar":
            planner = AStarPlanner(self.map)
        elif self.algorithm == "dijkstra":
            planner = DijkstraPlanner(self.map)
        elif self.algorithm == "greedy":
            planner = GreedyPlanner(self.map)
        else:
            rospy.logwarn(f"[Planner] Algorithme inconnu '{self.algorithm}', utilisation de A* par défaut.")
            planner = AStarPlanner(self.map)

        t0 = time.time()
        path = planner.plan(start, goal)
        t1 = time.time()

        if path is None:
            rospy.logwarn("[Planner] Aucun chemin trouvé.")
            return

        dist = self.compute_path_distance(path)
        rospy.loginfo(f"[Planner] {self.algorithm.upper()} : Temps planification={t1-t0:.3f}s, distance={dist:.3f}m, étapes={len(path)}")

        self.publish_path(path)

    def world_to_grid(self, x, y):
        if self.origin is None or self.resolution is None:
            raise ValueError("Map non initialisée")

        gx = int(round((x - self.origin[0]) / self.resolution))
        gy = int(round((y - self.origin[1]) / self.resolution))

        gx = max(0, min(gx, self.map.shape[1] - 1))
        gy = max(0, min(gy, self.map.shape[0] - 1))

        return (gy, gx)

    def grid_to_world(self, gy, gx):
        x = gx * self.resolution + self.origin[0]
        y = gy * self.resolution + self.origin[1]
        return (x, y)

    def is_cell_free(self, cell):
        gy, gx = cell
        if gy < 0 or gy >= self.map.shape[0] or gx < 0 or gx >= self.map.shape[1]:
            return False
        return self.map[gy][gx] == 0

    def compute_path_distance(self, path):
        if len(path) < 2:
            return 0.0

        total = 0.0
        for i in range(1, len(path)):
            gy0, gx0 = path[i-1]
            gy1, gx1 = path[i]
            x0, y0 = self.grid_to_world(gy0, gx0)
            x1, y1 = self.grid_to_world(gy1, gx1)
            d = ((x1-x0)**2 + (y1-y0)**2)**0.5
            total += d
        return total

    def publish_path(self, path):
        ros_path = Path()
        ros_path.header.stamp = rospy.Time.now()
        ros_path.header.frame_id = "map"

        for gy, gx in path:
            x, y = self.grid_to_world(gy, gx)
            pose = PoseStamped()
            pose.header.stamp = ros_path.header.stamp
            pose.header.frame_id = "map"
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0
            ros_path.poses.append(pose)

        self.path_pub.publish(ros_path)
        rospy.loginfo("[Planner] Chemin publié sur /planned_path")

if __name__ == "__main__":
    PlannerNode()
    rospy.spin()
