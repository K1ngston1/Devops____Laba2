"""
HMP Load Testing - Master Locustfile

This file combines user behaviors and load shapes for all test scenarios.

Usage Examples:
    # Average Load Test (default)
    locust --host=http://localhost:8000 --headless

    # Stress Test
    locust --host=http://localhost:8000 --class-picker --headless
    # Then select: StressLoadShape, StudentUser, InstructorUser

    # Spike Test
    locust --host=http://localhost:8000 --class-picker --headless
    # Then select: SpikeLoadShape, SpikeStudentUser, SpikeInstructorUser

    # Breakpoint Test
    locust --host=http://localhost:8000 --class-picker --headless
    # Then select: BreakpointLoadShape, StudentUser, InstructorUser

    # Soak Test
    locust --host=http://localhost:8000 --class-picker --headless
    # Then select: SoakLoadShape, StudentUser, InstructorUser

    # Smoke Test
    locust --host=http://localhost:8000 --class-picker --headless
    # Then select: SmokeLoadShape, StudentUser, InstructorUser
"""

# Import all user classes
from core.users import (
    StudentUser,
    InstructorUser,
    SpikeStudentUser,
    SpikeInstructorUser,
)

# Import all load shapes
from core.shapes import (
    AverageLoadShape,
    StressLoadShape,
    SpikeLoadShape,
    BreakpointLoadShape,
    SoakLoadShape,
    SmokeLoadShape,
)

# Default configuration: Average Load Test
__all__ = [
    "AverageLoadShape",
    "StudentUser",
    "InstructorUser",
    "StressLoadShape",
    "SpikeLoadShape",
    "SpikeStudentUser",
    "SpikeInstructorUser",
    "BreakpointLoadShape",
    "SoakLoadShape",
    "SmokeLoadShape",
]
