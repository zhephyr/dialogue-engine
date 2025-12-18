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
        print("\nWelcome to the interactive dialogue console!")
        print("You can talk to NPCs and investigate the murder mystery.\n")
        print("Commands:")
        print("  /talk <npc_name>  - Start talking to an NPC")
        print("  /npcs             - List all available NPCs")
        print("  /status <npc>     - Show NPC status and stats")
        print("  /lies <npc>       - Show lies told by an NPC")
        print("  /history <npc>    - Show conversation history")
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
