# Project Context

1. Core concept & Story:
The application is a hands-on educational platform designed to teach Python programming to K-12 students through interactive robotics. This tool serves as an engaging bridge for students, STEAM teachers, and technical beginners to learn coding by providing immediate, physical feedback.
- The Mission: The physical setup consists of a 3-joint robotic arm placed on a chess-like grid platform. Students are tasked with specific missions, such as controlling the arm to pick up an object and precisely moving it to a designated coordinate on the board.
- The Gameplay: Drawing inspiration from educational games like KTurtle, students must write sequential logic to solve the physical puzzle, bridging the gap between digital code and real-world mechanics.
2. User Experience (UI):
The application runs directly on a Raspberry Pi or IoT gateway, projecting a split-screen Textual User Interface (TUI) to the user's monitor.
- Left Screen (The Editor): A dedicated coding environment where students write simple, beginner-friendly Python commands (e.g., arm.turn_left(90), arm.grab(), arm.release()).
- Right Screen (The Console): A real-time feedback log that displays the execution status, debugging information, and printed outputs from the student's code, helping them troubleshoot their logic.
3. Tech stack
- Language: Python 3.11.
- Hardware: Raspberry Pi (or similar gateway) connected to a 3-joint robotic arm.
- UI Framework: textual (a Python framework for building sophisticated terminal user interfaces).
- Hardware Communication: The thingbot-telemetrix library, which handles the telemetrix protocol to translate Python commands into physical servo movements on the hardware. (https://github.com/MEO-3/thingbot-telemetrix, https://github.com/MEO-3/thingbot-telemetrix-arduino)
- Hardware Specs: NEO One Gateway:
    - CPU: Quad-core ARM Cortex-A53
    - RAM: 2GB
    - Storage: 16GB eMMC
    - Connectivity: Wi-Fi, Bluetooth, Ethernet
    - OS: Linux Armbian (CLI only, no desktop environment)