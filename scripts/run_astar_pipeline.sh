#!/bin/bash
set -e

echo "[1/7] Kill previous ROS nodes" 
rosnode kill -a 2>/dev/null || true
sleep 1

echo "[2/7] Source ROS and workspace"
source /opt/ros/noetic/setup.bash
source /home/ubuntu/workspace/devel/setup.bash
export TURTLEBOT3_MODEL=burger

echo "[3/7] Launch Gazebo world with TurtleBot3"
roslaunch turtlebot3_gazebo turtlebot3_world.launch &
GAZEBO_PID=$!
sleep 10

echo "[4/7] Launch A* navigation stack"
roslaunch turtlebot3_navigation turtlebot3_astar_navigation.launch map_file:=/home/ubuntu/workspace/maps/my_map.yaml rviz:=false &
NAV_PID=$!
sleep 12

echo "[5/7] TF chain check (map->odom->base_footprint)"
python3 /home/ubuntu/workspace/scripts/check_tf_chain.py &
TF_PID=$!
sleep 4

echo "[6/7] Check /scan if Laser is streaming"
rosrun tf tf_monitor /map /base_footprint 1 &
TFM_PID=$!

# Wait a bit for scan to appear
sleep 6

SCAN_RATE=$(rostopic hz /scan -n 1 2>&1 | grep -o -E "[0-9]+\.?[0-9]*" | head -1 || true)
if [ -z "$SCAN_RATE" ]; then
  echo "[WARN] No scan topic, check your Gazebo world and robot laser."
else
  echo "[INFO] Scan rate: $SCAN_RATE Hz"
fi

echo "[7/7] Launch A* test script"
rosrun turtlebot3_example test_astar.py || true

# cleanup
kill $TFM_PID 2>/dev/null || true
kill $TF_PID 2>/dev/null || true
kill $NAV_PID 2>/dev/null || true
kill $GAZEBO_PID 2>/dev/null || true

echo "Done"
