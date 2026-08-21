# RoboCup 3D Soccer Simulation notes

RoboCup is an international research initiative whose long-term soccer goal is
for humanoid robots to defeat the human world champion team by 2050. The 3D
Simulation League removes the cost of physical hardware while retaining research
problems in humanoid control, perception, learning, optimization, multi-agent
coordination, and team strategy.

The 2026 league changes the platform from SimSpark to the MuJoCo-based
RCSSServerMJ and uses simulated Booster T1 humanoids. The simulator permits 11
players under its generic rules, but the `ssim26` competition rule book sets a
seven-player maximum on a FIFA 7v7 field. KingsRams therefore begins with one
goalkeeper, two defenders, two midfielders, and two strikers. Each robot is a separate client process that
receives perceptions and sends actuator commands over length-prefixed TCP.

## Teams and qualification

Current teams include FC Portugal, magmaOffenburg, Bahia RT, UT Austin Villa,
ITAndroids, Apollo3D, and others from universities worldwide. Teams commonly
publish Team Description Papers and some release source or base code; source-code
release is a community practice, not the 2026 binary submission format.

For 2026, qualification required a 4-12 page Springer LNCS Team Description
Paper, a publications/achievements PDF, and a 64-bit Linux team binary bundle.
The bundle requires `start.sh` and `kill.sh`, must include external libraries,
must run headlessly without output, and must acknowledge work derived from other
teams. Competition binaries must target MuJoCo and run on a modern GNU/Linux
system such as Ubuntu 24.04. Qualification deadlines for RoboCup 2026 have
already passed; KingsRams should target the next published call for participation.

## Primary references

- <https://ssim.robocup.org/3d-simulation/>
- <https://ssim.robocup.org/2025/12/16/robocup-2026-soccer-simulation-3d-call-for-participation/>
- <https://gitlab.com/robocup-sim/rcssservermj>
- <https://robocup-sim.gitlab.io/rcssservermj/>
- <https://ssim.robocup.org/3d-simulation/3d-tools/>
- <https://archive.robocup.info/Soccer/Simulation/3D/>