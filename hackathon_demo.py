#!/usr/bin/env python3
"""
ARGUS Hackathon Demo Script
3-Minute Demonstration of the AI Research & Decision Intelligence Agent

This script simulates the flow of the ARGUS demo for the Nebius × NVIDIA hackathon.
"""

import time
import sys
import json

def print_slow(text, delay=0.03):
    """Print text slowly for dramatic effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_section(title, content=""):
    """Print a formatted section."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)
    if content:
        print(content)

def main():
    print_section("ARGUS", "Your idea. Under scrutiny.")
    
    # 0:00-0:20 - User pastes idea
    print_section("0:00 - 0:20", "")
    print("USER PASTES:")
    print_slow('  "I want to build an efficient multimodal model for detecting misinformation in social media."')
    time.sleep(1)
    
    # 0:20-0:45 - Initial analysis
    print_section("0:20 - 0:45", "")
    print("ARGUS BEGINS INVESTIGATING...")
    time.sleep(1)
    print_slow("  Extracting claims and assumptions...")
    time.sleep(0.5)
    print_slow("  Searching literature...")
    time.sleep(0.5)
    print_slow("  Searching recent research...")
    time.sleep(0.5)
    print_slow("  Searching counterevidence...")
    time.sleep(1)
    
    # 0:45-1:15 - Show results
    print_section("0:45 - 1:15", "")
    print("  38 sources found")
    print("  12 high-relevance sources")
    print("  5 contradictory findings")
    time.sleep(1)
    
    # Dashboard
    print_section("1:15 - 1:40", "")
    print("  ARGUS DASHBOARD APPEARS")
    time.sleep(0.5)
    print("  Idea Health Metrics:")
    print("    Novelty: ████████░░  78%")
    print("    Evidence:  ██████░░░░  64%")
    print("    Feasibility: █████████░  89%")
    print("    Impact:    ████████░░  81%")
    print("    Research Gap: ███████░░░  71%")
    time.sleep(1)
    
    # 1:40 - User clicks #BREAK_IT
    print_section("1:40", "")
    print("USER CLICKS: #BREAK_IT")
    time.sleep(1)
    print("  ")
    print_slow("  ARGUS attacks the proposal...")
    time.sleep(1)
    
    # Breakdown analysis
    print_section("1:40 - 2:10", "")
    print("  POTENTIAL FAILURE:")
    print_slow("    The claimed multimodal improvement may depend")
    print("    on strong text-image alignment.")
    time.sleep(1)
    print("  COUNTEREVIDENCE:")
    print_slow("    2 studies report reduced gains when")
    print("    modalities are weakly correlated.")
    time.sleep(1)
    
    # Breakpoint engine
    print_section("2:10 - 2:35", "")
    print("  BREAKPOINT FOUND")
    time.sleep(0.5)
    print_slow("    When modality correlation decreases,")
    print("    the expected performance advantage")
    time.sleep(0.5)
    print("    rapidly approaches zero.")
    time.sleep(1)
    
    # Recommendations
    print_section("2:35 - 2:55", "")
    print("  WHAT YOU SHOULD DO NEXT")
    time.sleep(0.3)
    print("    1. Measure modality correlation.")
    time.sleep(0.3)
    print("    2. Test weakly aligned samples.")
    time.sleep(0.3)
    print("    3. Compare against text-only baseline.")
    time.sleep(0.3)
    print("    4. Run cross-dataset evaluation.")
    time.sleep(1)
    
    # Final screen
    print_section("2:55 - 3:00", "")
    print_section("ARGUS", "Your idea. Under scrutiny.")
    time.sleep(1)
    
    print_section("", "")
    print("  " + " " * 20 + "╔══════════════════════════════════════════")
    print("  " + " " * 20 + "║                                       ║")
    print("  " + " " * 20 + "║   IDEA SUCCESSFULLY STRESS-TESTED     ║")
    print("  " + " " * 20 + "║                                       ║")
    print("  " + " " * 20 + "║  Breakpoint: Modality correlation       ║")
    print("  " + " " * 20 + "║  Recommendation: Measure alignment      ║")
    print("  " + " " * 20 + "║                                       ║")
    print("  " + " " * 20 + "╚══════════════════════════════════════════")
    
    print_section("", "")
    print_slow("""        

   ▂▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
   ▄▀░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄░▄ 
   █░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀░▀ 
   █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
   ▀▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▀

""")
    
    print_section("", "")
    print("         ARGUS - Making your ideas stronger before you build them.")
    print("         ")
    print("         The core identity:")
    print("           ARGUS")
    print("             AI Research & Decision Intelligence")
    print("               │")
    print("               ▼")
    print("          ┌──────────────────┐")
    print("          │  INVESTIGATE     │")
    print("          └────────┬─────────┘")
    print("               ▼")
    print("          ┌──────────────────┐")
    print("          │  FIND EVIDENCE   │")
    print("          └────────┬─────────┘")
    print("               ▼")
    print("          ┌──────────────────┐")
    print("          │  FIND CONTRA     │")
    print("          └────────┬─────────┘")
    print("               ▼")
    print("          ┌──────────────────┐")
    print("          │  REASON          │")
    print("          └────────┬─────────┘")
    print("               ▼")
    print("          ┌──────────────────┐")
    print("          │  BREAK IT        │")
    print("          └────────┬─────────┘")
    print("               ▼")
    print("          ┌──────────────────┐")
    print("          │  FIND BREAKPOINT │")
    print("          └────────┬─────────┘")
    print("               ▼")
    print("          ┌──────────────────┐")
    print("          │  TELL ME WHAT    │")
    print("          │  TO DO NEXT      │")
    print("          └──────────────────┘")
    
    print_section("", "")
    print("         Demo complete. Thank you for watching!")

if __name__ == "__main__":
    main()