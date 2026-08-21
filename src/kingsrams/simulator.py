"""macOS-safe entry point for the RCSSServerMJ graphical simulator."""

import logging
from typing import Any

from rcsssmj.__main__ import soccer_sim
from rcsssmj.monitor.mujoco_monitor import MujocoMonitor
from rcsssmj.server.server import SimServer


logger = logging.getLogger(__name__)
_remove_monitors = SimServer._remove_monitors


def _remove_monitors_and_stop(server: Any, monitors: Any) -> None:
    """Stop the local server when its graphical monitor is closed."""
    viewer_closed = any(isinstance(monitor, MujocoMonitor) for monitor in monitors)
    _remove_monitors(server, monitors)
    if viewer_closed:
        logger.info("Simulator window closed; stopping server.")
        server.shutdown()


def _close_connection_listeners(listeners: Any) -> None:
    """Close listening sockets before joining their blocked accept loops."""
    for listener in listeners:
        listener.shutdown()
        sock = getattr(listener, "_sock", None)
        if sock is not None:
            sock.close()
    for listener in listeners:
        listener.join()


def _run_on_main_thread(server: Any) -> None:
    """Run GLFW on the main thread as required by macOS Cocoa."""
    logger.info("Starting server...")
    server._shutdown = False

    try:
        for listener in server._connection_listeners:
            listener.bind()
    except ConnectionError:
        for listener in server._connection_listeners:
            listener.shutdown()
        raise

    for listener in server._connection_listeners:
        listener.listen_for_connections()

    logger.info("Starting server... DONE!")
    try:
        server._run_simulation()
    finally:
        logger.info("Shutting down server...")
        server._shutdown = True
        _close_connection_listeners(server._connection_listeners)
        server._connection_listeners.clear()
        server._graceful_shutdown(server._agents)
        server._agents.clear()
        server._graceful_shutdown(server._monitors)
        server._monitors.clear()
        server.sim.shutdown()
        logger.info("Shutting down server... DONE!")


def main() -> None:
    SimServer.run = _run_on_main_thread
    SimServer._remove_monitors = _remove_monitors_and_stop
    soccer_sim()


if __name__ == "__main__":
    main()