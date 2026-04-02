cmake_minimum_required(VERSION 3.0.2)
project(custom_worlds)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY worlds/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/worlds
)

install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)