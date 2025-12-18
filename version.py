"""
Version information for the Murder Mystery Dialogue Engine
"""

__version__ = "0.2.0"
__version_info__ = tuple(int(i) for i in __version__.split("."))

# Version history
VERSION_HISTORY = """
0.2.0 (2025-12-17)
-----------------
- Added explicit timeline/schedule system with TimeBlock and NPCScheduleEntry to eliminate time/location inconsistencies. NPCs now have precise schedules that AI must follow. Added /timeline command to view schedules.

0.1.1 (2025-12-17)
-----------------
- Added Victorian England setting context, Scotland Yard investigator role, and /setting command for investigation briefing

0.1.0 (2025-12-17)
------------------
- Initial release
- Core dialogue engine with AI-powered NPCs
- Fact-checking system against world state
- Memory system tracking lies and omissions
- The Harrow Estate Incident example scenario
- Standalone console interface for testing
- Support for OpenAI and Anthropic AI providers
"""
