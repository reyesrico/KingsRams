# Simulator boundary

KingsRams targets **RCSSServerMJ**, the MuJoCo-based simulator selected for the
RoboCup 2026 3D Soccer Simulation League. The simulator is installed from PyPI
into the repository-local `.venv`; third-party simulator source and generated
assets are not copied into the team code.

- Runtime package: `rcsssmj==0.2.1`
- Physics engine: `mujoco==3.5.0` (pinned by RCSSServerMJ)
- Verified macOS runtime: `glfw==2.10.2`, `numpy==2.5.2`, and the exact
	transitive versions in `constraints.txt`
- Agent endpoint: TCP `127.0.0.1:60000`
- Monitor endpoint: TCP `127.0.0.1:60001`
- Rule book: `ssim26`
- Update mode: sequential, avoiding unstable concurrent model updates while
	several T1 agents join

This boundary keeps `src/kingsrams` independently packageable for qualification
while allowing the simulator to be upgraded and tested separately.

On macOS, `run-simulator.sh` uses a small wrapper that keeps GLFW and Cocoa on
the process main thread. The upstream `rcsssmj==0.2.1` entry point starts its
viewer in a worker thread, which exits with `trace trap` before creating a
window on current macOS versions.

## Legacy SimSpark

The linked 2017 macOS guide is for the retired SimSpark competition stack. Its
Xcode 2.4, Ruby 1.8, SDL 1.2, Boost, FreeType, JPEG, DevIL, and ODE recipe is not
compatible with a current Apple Silicon toolchain. Current SimSpark source has
also moved to C++17 and SDL2. RoboCup 2026 explicitly states that no SimSpark
competition will take place, so those libraries are intentionally not installed.