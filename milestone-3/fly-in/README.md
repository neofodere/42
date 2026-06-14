# Fly-In: Coordinated Drone Routing System

*This project has been created as part of the 42 curriculum by nfodere-.*

## Description
This project implements an autonomous multi-drone routing system over a spatiotemporal network of zones. The objective is to navigate an arbitrary number of drones concurrently from a starting hub to an destination endpoint in the minimum number of steps. The system explicitly prevents routing deadlocks, collision states, and resource over-allocation by honoring distinct node capacities (`max_drones`), link constraints (`max_link_capacity`), and terrain weights (such as multi-turn transit costs for restricted zones or route prioritize weights for preferred zones).

## Instructions

### Installation
Install project developer dependencies and checking infrastructure using your system environment's default package manager:

```bash
make install