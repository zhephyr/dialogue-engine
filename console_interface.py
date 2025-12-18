"""
Console Interface

Standalone console interface for testing the dialogue engine.
Allows interaction with NPCs without game integration.
"""

import sys
from typing import Optional
from dialogue_engine import DialogueEngine
from world_state import WorldState
from npc_agent import NPCAgent, CharacterTrait
from colorama import init, Fore, Style
import os
from version import __version__

# Initialize colorama for colored output
try:
    init(autoreset=True)
    COLORS_ENABLED = True
except:
    COLORS_ENABLED = False


class ConsoleInterface:
    """Interactive console interface for the dialogue engine"""
    
    def __init__(self, engine: DialogueEngine):
        self.engine = engine
        self.current_npc: Optional[str] = None
        self.player_name = "Detective"
        self.running = True
    
    def print_colored(self, text: str, color: str = "") -> None:
        """Print colored text if colors are enabled"""
        if COLORS_ENABLED and color:
            print(f"{color}{text}{Style.RESET_ALL}")
        else:
            print(text)
    
    def print_header(self, text: str) -> None:
        """Print a header"""
        self.print_colored(f"\n{'='*60}", Fore.CYAN)
        self.print_colored(f"  {text}", Fore.CYAN)
        self.print_colored(f"{'='*60}", Fore.CYAN)
    
    def print_npc(self, npc_name: str, text: str) -> None:
        """Print NPC dialogue"""
        self.print_colored(f"\n{npc_name}: ", Fore.GREEN)
        self.print_colored(f'  "{text}"', Fore.WHITE)
    
    def print_player(self, text: str) -> None:
        """Print player dialogue"""
        self.print_colored(f"\n{self.player_name}: ", Fore.YELLOW)
        self.print_colored(f'  "{text}"', Fore.WHITE)
    
    def print_system(self, text: str) -> None:
        """Print system message"""
        self.print_colored(f"\n[{text}]", Fore.CYAN)
    
    def print_debug(self, text: str) -> None:
        """Print debug information"""
        self.print_colored(f"  DEBUG: {text}", Fore.MAGENTA)
    
    def show_welcome(self) -> None:
        """Show welcome message"""
        self.print_header("MURDER MYSTERY DIALOGUE ENGINE")
        self.print_colored(f"Version {__version__}", Fore.CYAN)
        print("\nWelcome to the interactive dialogue console!")
        print("You can talk to NPCs and investigate the murder mystery.\n")
        print("Commands:")
        print("  /talk <npc_name>  - Start talking to an NPC")
        print("  /npcs             - List all available NPCs")
        print("  /status <npc>     - Show NPC status and stats")
        print("  /lies <npc>       - Show lies told by an NPC")
        print("  /history <npc>    - Show conversation history")
        print("  /timeline [npc]   - Show timeline/schedule (all or specific NPC)")
        print("  /setting          - Show setting and initial investigation report")
        print("  /scene <text>     - Set the current scene")
        print("  /world            - Show world state summary")
        print("  /stats            - Show engine statistics")
        print("  /help             - Show this help message")
        print("  /quit or /exit    - Exit the program")
        print("\nType your message to talk to the current NPC, or use a command.\n")
    
    def show_npcs(self) -> None:
        """List all available NPCs"""
        npcs = self.engine.get_all_npcs()
        if not npcs:
            self.print_system("No NPCs available")
            return
        
        self.print_header("AVAILABLE NPCs")
        for npc_name in npcs:
            npc = self.engine.get_npc(npc_name)
            if npc:
                print(f"\n  {npc.name}")
                print(f"    Location: {npc.current_location}")
                print(f"    Personality: {npc.personality}")
                print(f"    Emotional State: {npc.emotional_state}")
    
    def show_npc_status(self, npc_name: str) -> None:
        """Show detailed NPC status"""
        status = self.engine.get_npc_status(npc_name)
        if not status:
            self.print_system(f"NPC '{npc_name}' not found")
            return
        
        self.print_header(f"STATUS: {status['name']}")
        print(f"\n  Location: {status['location']}")
        print(f"  Emotional State: {status['emotional_state']}")
        print(f"  Conversation Turns: {status['conversation_turns']}")
        print(f"  Total Memories: {status['memories']}")
        print(f"  Lies Told: {status['lies_told']}")
        print(f"  Omissions Made: {status['omissions_made']}")
        
        if status['goals']:
            print(f"\n  Goals:")
            for goal in status['goals']:
                print(f"    - {goal}")
        
        if status['secrets']:
            print(f"\n  Secrets:")
            for secret in status['secrets']:
                print(f"    - {secret}")
    
    def show_lies(self, npc_name: str) -> None:
        """Show lies told by an NPC"""
        lies = self.engine.get_npc_lies(npc_name)
        if not lies:
            self.print_system(f"No recorded lies from {npc_name}")
            return
        
        self.print_header(f"LIES TOLD BY {npc_name}")
        for i, lie in enumerate(lies, 1):
            print(f"\n  {i}. {lie['content']}")
            if 'player_message' in lie.get('context', {}):
                print(f"     In response to: {lie['context']['player_message']}")
    
    def show_history(self, npc_name: str) -> None:
        """Show conversation history"""
        history = self.engine.get_conversation_history(npc_name, num_turns=20)
        if not history:
            self.print_system(f"No conversation history with {npc_name}")
            return
        
        self.print_header(f"CONVERSATION HISTORY: {npc_name}")
        for turn in history:
            speaker = turn['speaker']
            message = turn['message']
            
            if speaker == self.player_name:
                self.print_colored(f"\n  {speaker}: \"{message}\"", Fore.YELLOW)
            else:
                self.print_colored(f"\n  {speaker}: \"{message}\"", Fore.GREEN)
    
    def show_world_state(self) -> None:
        """Show world state summary"""
        summary = self.engine.world_state.get_world_summary()
        
        self.print_header("WORLD STATE")
        print(f"\n  Total Facts: {summary['total_facts']} ({summary['public_facts']} public, {summary['private_facts']} private)")
        print(f"  Total Events: {summary['total_events']}")
        print(f"  Total Relationships: {summary['total_relationships']}")
        
        if summary['locations']:
            print(f"\n  Locations: {', '.join(summary['locations'])}")
        
        if summary['characters']:
            print(f"\n  Characters: {', '.join(summary['characters'])}")
    
    def show_stats(self) -> None:
        """Show engine statistics"""
        stats = self.engine.get_engine_stats()
        
        self.print_header("ENGINE STATISTICS")
        print(f"\n  Total NPCs: {stats['total_npcs']}")
        print(f"  AI Provider: {stats['ai_provider']}")
        
        if 'fact_checking' in stats:
            fc = stats['fact_checking']
            print(f"\n  Fact Checking:")
            print(f"    Total Validations: {fc['total_validations']}")
            print(f"    Valid Claims: {fc['valid_claims']}")
            print(f"    Invalid Claims: {fc['invalid_claims']}")
            print(f"    Intentional Lies: {fc['intentional_lies']}")
            print(f"    Omissions: {fc['omissions']}")
            print(f"    Accuracy Rate: {fc['accuracy_rate']:.1f}%")
    
    def show_setting(self) -> None:
        """Show setting information and initial investigation report"""
        world = self.engine.world_state
        
        # Get setting facts
        time_period = world.get_fact("time_period") or "Unknown"
        setting = world.get_fact("setting") or "Unknown location"
        estate_name = world.get_fact("estate_name") or "Unknown estate"
        estate_type = world.get_fact("estate_type") or "Unknown"
        player_role = world.get_fact("player_role") or "Investigator"
        
        self.print_header("SETTING & INVESTIGATION BRIEFING")
        
        # Setting description
        print(f"\n  TIME PERIOD: {time_period}")
        print(f"  LOCATION: {estate_name}, {setting}")
        print(f"  ESTATE TYPE: {estate_type}")
        print(f"\n  YOUR ROLE: {player_role}")
        
        # Initial investigation report from on-site officer
        self.print_colored("\n  === INITIAL INVESTIGATION REPORT ===", Fore.YELLOW)
        self.print_colored("  From: On-site Officer", Fore.WHITE)
        self.print_colored("  To: Investigating Detective\n", Fore.WHITE)
        
        # Get public murder facts
        victim = world.get_fact("victim")
        cause = world.get_fact("cause_of_death")
        location = world.get_fact("murder_location")
        time_of_death = world.get_fact("time_of_death")
        discovered_by = world.get_fact("body_discovered_by")
        discovery_time = world.get_fact("discovery_time")
        door_locked = world.get_fact("door_locked")
        
        print(f"  VICTIM: {victim if victim else 'Unknown'}")
        print(f"  CAUSE OF DEATH: {cause if cause else 'Under investigation'}")
        print(f"  LOCATION: {location if location else 'Unknown'}")
        print(f"  TIME OF DEATH: {time_of_death if time_of_death else 'Unknown'}")
        print(f"\n  DISCOVERY:")
        print(f"    - Body discovered by {discovered_by if discovered_by else 'unknown'} at {discovery_time if discovery_time else 'unknown time'}")
        if door_locked:
            print(f"    - {location} door found locked")
        
        # List occupants present
        occupants = [char for char in world.characters if char != "Investigator"]
        if occupants:
            print(f"\n  OCCUPANTS PRESENT:")
            for occupant in sorted(occupants):
                print(f"    - {occupant}")
        
        # Public events
        public_events = world.query_facts(category="murder", is_public=True)
        if len(public_events) > 3:  # More than just basic facts
            print(f"\n  ADDITIONAL NOTES:")
            print(f"    - Multiple witnesses present at estate")
            print(f"    - All occupants have been secured on premises")
            print(f"    - Await your arrival to conduct interviews")
        
        print(f"\n  OBJECTIVE: Question all occupants and determine the perpetrator.")
        print(f"\n  Use /npcs to see who you can interview.")
        
    def show_timeline(self, npc_name: Optional[str] = None) -> None:
        """Show timeline/schedule for all NPCs or a specific NPC"""
        world = self.engine.world_state
        
        if npc_name:
            # Show specific NPC's schedule
            npc = self.engine.get_npc(npc_name)
            if not npc:
                self.print_system(f"NPC '{npc_name}' not found")
                return
            
            schedule = world.get_character_schedule(npc.name)
            if not schedule:
                self.print_system(f"No schedule information for {npc.name}")
                return
            
            self.print_header(f"TIMELINE: {npc.name}")
            current_day = None
            
            for entry in schedule:
                if entry.time_block.day != current_day:
                    current_day = entry.time_block.day
                    self.print_colored(f"\\n  === Day {current_day} ===", Fore.YELLOW)
                
                time_str = entry.time_block.period.replace('_', ' ').title()
                print(f"\\n  {time_str}:")
                print(f"    Location: {entry.location}")
                print(f"    Activity: {entry.activity}")
                
                if entry.with_characters:
                    print(f"    With: {', '.join(entry.with_characters)}")
                
                if entry.notes and not entry.is_public:
                    # Only show notes if they're private (for testing/debugging)
                    self.print_colored(f"    [Private Note: {entry.notes}]", Fore.MAGENTA)
        else:
            # Show timeline for all NPCs side-by-side
            self.print_header("COMPLETE TIMELINE - ALL OCCUPANTS")
            
            # Get all characters except Investigator
            characters = [c for c in world.characters if c != "Investigator"]
            
            if not characters:
                self.print_system("No character schedules available")
                return
            
            # Get all schedule entries
            all_schedules = {}
            for char in characters:
                all_schedules[char] = world.get_character_schedule(char)
            
            # Group by day and time period
            days = set()
            for schedules in all_schedules.values():
                for entry in schedules:
                    days.add(entry.time_block.day)
            
            for day in sorted(days):
                self.print_colored(f"\\n  === DAY {day} ===", Fore.YELLOW)
                
                for period in world.time_periods:
                    # Check if any character has an entry for this period
                    has_entries = any(
                        any(e.time_block.day == day and e.time_block.period == period 
                            for e in schedules)
                        for schedules in all_schedules.values()
                    )
                    
                    if not has_entries:
                        continue
                    
                    period_name = period.replace('_', ' ').title()
                    print(f"\\n  {period_name}:")
                    
                    for char in sorted(characters):
                        schedules = all_schedules[char]
                        entry = next(
                            (e for e in schedules 
                             if e.time_block.day == day and e.time_block.period == period),
                            None
                        )
                        
                        if entry:
                            companions = f" (with {', '.join(entry.with_characters)})" if entry.with_characters else ""
                            print(f"    {char:20s} -> {entry.location:15s} - {entry.activity}{companions}")
                        else:
                            print(f"    {char:20s} -> {'Unknown':15s}")
            
            print(f"\\n  Use /timeline <npc_name> to see detailed schedule for specific NPC.")
            
    def handle_command(self, command: str) -> bool:
        """
        Handle a command. Returns True if command was processed.
        """
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""
        
        if cmd in ['/quit', '/exit']:
            self.print_system("Goodbye!")
            self.running = False
            return True
        
        elif cmd == '/help':
            self.show_welcome()
            return True
        
        elif cmd == '/npcs':
            self.show_npcs()
            return True
        
        elif cmd == '/talk':
            if not arg:
                self.print_system("Usage: /talk <npc_name>")
            else:
                npc = self.engine.get_npc(arg)
                if npc:
                    self.current_npc = npc.name
                    self.print_system(f"Now talking to {npc.name}")
                    self.print_colored(f"\nYou approach {npc.name}...\n", Fore.CYAN)
                else:
                    self.print_system(f"NPC '{arg}' not found. Use /npcs to see available NPCs.")
            return True
        
        elif cmd == '/status':
            if not arg:
                self.print_system("Usage: /status <npc_name>")
            else:
                self.show_npc_status(arg)
            return True
        
        elif cmd == '/lies':
            if not arg:
                self.print_system("Usage: /lies <npc_name>")
            else:
                self.show_lies(arg)
            return True
        
        elif cmd == '/history':
            if not arg:
                self.print_system("Usage: /history <npc_name>")
            else:
                self.show_history(arg)
            return True
        
        elif cmd == '/timeline':
            # arg is optional - can show all or specific NPC
            self.show_timeline(arg if arg else None)
            return True
        
        elif cmd == '/scene':
            if not arg:
                self.print_system("Usage: /scene <description>")
            else:
                self.engine.set_scene(arg)
                self.print_system(f"Scene set: {arg}")
            return True
        
        elif cmd == '/world':
            self.show_world_state()
            return True
        
        elif cmd == '/stats':
            self.show_stats()
            return True
        
        elif cmd == '/setting':
            self.show_setting()
            return True
        
        return False
    
    def run(self) -> None:
        """Main console loop"""
        self.show_welcome()
        
        while self.running:
            try:
                # Show prompt
                if self.current_npc:
                    prompt = f"{Fore.YELLOW}[Talking to {self.current_npc}]{Style.RESET_ALL} > " if COLORS_ENABLED else f"[{self.current_npc}] > "
                else:
                    prompt = f"{Fore.CYAN}[No NPC selected]{Style.RESET_ALL} > " if COLORS_ENABLED else "> "
                
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                    continue
                
                # Must have an NPC selected to talk
                if not self.current_npc:
                    self.print_system("Please select an NPC first using /talk <npc_name>")
                    continue
                
                # Show player message
                self.print_player(user_input)
                
                # Get NPC response
                response, metadata = self.engine.converse(
                    self.current_npc,
                    user_input,
                    self.player_name
                )
                
                # Show NPC response
                self.print_npc(self.current_npc, response)
                
                # Show validation info if in verbose mode
                if self.engine.verbose and metadata.get('validation_results'):
                    self.print_debug("Validation Results:")
                    for result in metadata['validation_results']:
                        status = "✓" if result['is_valid'] else "✗"
                        flag = " [LIE]" if result['is_lie'] else (" [OMISSION]" if result['is_omission'] else "")
                        self.print_debug(f"{status} {result['claim']}{flag}")
            
            except KeyboardInterrupt:
                print("\n")
                self.print_system("Use /quit to exit")
            except Exception as e:
                self.print_system(f"Error: {str(e)}")
                if self.engine.verbose:
                    import traceback
                    traceback.print_exc()


def main():
    """Main entry point for console interface"""
    # Check for command line arguments
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    print("Loading dialogue engine...")
    
    # Import the example scenario
    try:
        from example_scenario import create_example_scenario
        engine = create_example_scenario(verbose=verbose)
    except ImportError:
        # If example doesn't exist, create a minimal setup
        print("Warning: example_scenario.py not found. Creating minimal setup.")
        world = WorldState()
        engine = DialogueEngine(world, verbose=verbose)
        print("No NPCs loaded. You can add them programmatically or create example_scenario.py")
    
    # Create and run console interface
    console = ConsoleInterface(engine)
    console.run()


if __name__ == "__main__":
    main()
