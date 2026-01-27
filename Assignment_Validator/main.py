import sys
import os
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
import rich.box
from dotenv import load_dotenv

from consoles import ClaudeConsole
from consoles import DeepConsole
from consoles import Helper

# Find .env in multiple locations
if getattr(sys, 'frozen', False):
    bundle_dir = os.path.dirname(sys.executable)
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(bundle_dir, '.env'))
load_dotenv()

DEEP_API_KEY = os.getenv("DEEP_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

helper = Helper.Helper()
console = Console()



def get_input_file():
    """Gets file from drag-onto-exe OR prompts user."""
    
    console.print("\n[cyan]Enter file path (or drag file here):[/cyan]")
    file_path = input("> ").strip().strip('"').strip("'")
    
    # Remove escape characters from drag-and-drop
    file_path = file_path.replace("\\ ", " ")
    file_path = file_path.replace("\\(", "(")
    file_path = file_path.replace("\\)", ")")
    
    if os.path.exists(file_path):
        return file_path
    
    console.print(f"[red]✗ File not found: {file_path}[/red]")
    return None


def get_output_path(input_path):
    directory = os.path.dirname(input_path)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    
    if not directory:
        directory = "."
    
    output_path = os.path.join(directory, f"{filename}_answers.txt")
    return output_path


def load_file(file_path):
    """Loads PDF or TXT file."""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".pdf":
        return helper.load_pdf(file_path)
    elif file_extension == ".txt":
        return helper.load_txt(file_path)
    else:
        console.print(f"[red]✗ Unsupported file type: {file_extension}[/red]")
        console.print("[dim]Supported: .pdf, .txt[/dim]")
        return None


# ============ CONSOLE DISPLAY FUNCTIONS ============

def display_header():
    """Displays the application header."""
    header = """
╔═══════════════════════════════════════════════════════════════╗
║              ASSIGNMENT VALIDATOR v1.0                        ║
║           Multi-LLM Homework Verification System              ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(Text(header, style="bold cyan"))


def display_pricing_table():
    """Displays LLM pricing information."""
    console.print("\n[bold]═══ LLM PRICING (Per Million Tokens) ═══[/bold]", justify="center")
    
    table = Table(show_header=True, header_style="bold", box=rich.box.DOUBLE_EDGE)
    
    table.add_column("Model", style="cyan")
    table.add_column("Input", justify="right")
    table.add_column("Cached Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Status", justify="center")

    table.add_row("ChatGPT", "$0.25", "$0.025", "$2.00", "[green]● ONLINE[/green]")
    table.add_row("DeepSeek", "$0.28", "$0.028", "$0.42", "[green]● ONLINE[/green]")
    table.add_row("Claude", "$0.10-$5.00", "—", "$1.25-$2.00", "[green]● ONLINE[/green]")

    console.print(table)


# ============ PROMPT BUILDERS ============

def build_question_prompt(question_text):
    """Builds prompt to send to LLMs for answering questions."""
    prompt = f"""Answer the following questions. Provide clear, concise answers.

{question_text}

Format your response as:
Q1: [answer]
Q2: [answer]
... and so on.
"""
    return prompt


def build_validation_prompt(answer_1, answer_2):
    """Builds prompt to compare two sets of answers."""
    prompt = f"""Compare these two answer sets. Do they match in meaning (not necessarily word-for-word)?

Answer Set 1:
{answer_1}

Answer Set 2:
{answer_2}

Respond with ONLY "true" if they match, or "false" if they don't match.
"""
    return prompt


# ============ RESPONSE EXTRACTORS ============

def extract_claude_response(result):
    """Extracts text from Claude API response."""
    if result and "content" in result:
        return result["content"][0]["text"]
    return None


def extract_deepseek_response(result):
    """Extracts text from DeepSeek API response."""
    if result and "choices" in result:
        return result["choices"][0]["message"]["content"]
    return None


# ============ VALIDATION LOGIC ============

def validate_answers(question_text, max_retries=3):
    """Main validation logic with retry."""
    
    claude_answer = None
    deep_answer = None
    
    for attempt in range(1, max_retries + 1):
        console.print(f"\n[yellow]Attempt {attempt}/{max_retries}[/yellow]")
        
        question_prompt = build_question_prompt(question_text)
        
        with console.status("[bold blue]  Processing with Claude...[/bold blue]", spinner="dots"):
            claude_result = ClaudeConsole.Claude_Connect(CLAUDE_API_KEY, prompt=question_prompt)
            claude_answer = extract_claude_response(claude_result)
        
        if claude_answer:
            console.print("[green]✓[/green] Claude response received")
        else:
            console.print("[red]✗[/red] Claude response failed")
        
        with console.status("[bold blue]  Processing with DeepSeek...[/bold blue]", spinner="dots"):
            deep_result = DeepConsole.DeepSeek_Connect(DEEP_API_KEY, prompt=question_prompt)
            deep_answer = extract_deepseek_response(deep_result)
        
        if deep_answer:
            console.print("[green]✓[/green] DeepSeek response received")
        else:
            console.print("[red]✗[/red] DeepSeek response failed")
        
        # Check if we got valid responses
        if not claude_answer or not deep_answer:
            console.print("[red]✗[/red] Failed to get responses, retrying...")
            continue
        
        # Compare answers using DeepSeek as validator
        validation_prompt = build_validation_prompt(claude_answer, deep_answer)
        
        with console.status("[bold blue]  Validating answers...[/bold blue]", spinner="dots"):
            validation_result = DeepConsole.DeepSeek_Connect(DEEP_API_KEY, prompt=validation_prompt)
            validation_answer = extract_deepseek_response(validation_result)
        console.print("[green]✓[/green] Validation complete")
        
        # Check if answers match
        if validation_answer and validation_answer.strip().lower() == "true":
            console.print("[bold green]✓ Answers match![/bold green]")
            return {
                "success": True,
                "claude_answer": claude_answer,
                "deep_answer": deep_answer,
                "attempts": attempt
            }
        else:
            console.print("[red]✗ Answers don't match[/red]")
    
    # All retries exhausted
    console.print("[bold red]Max retries reached. Returning best effort.[/bold red]")
    return {
        "success": False,
        "claude_answer": claude_answer,
        "deep_answer": deep_answer,
        "attempts": max_retries
    }


# ============ OUTPUT ============

def save_answer_key(output_path, results, question_text):
    """Saves the answer key to a file."""
    with open(output_path, "w") as f:
        f.write("=" * 50 + "\n")
        f.write("ANSWER KEY\n")
        f.write("=" * 50 + "\n\n")
        
        if results["success"]:
            f.write("Status: VERIFIED (Both LLMs agreed)\n\n")
        else:
            f.write("Status: UNVERIFIED (LLMs disagreed)\n\n")
        
        f.write(f"Attempts: {results['attempts']}\n\n")
        f.write("-" * 50 + "\n")
        f.write("Claude's Answers:\n")
        f.write("-" * 50 + "\n")
        f.write((results["claude_answer"] or "No response received") + "\n\n")
        f.write("-" * 50 + "\n")
        f.write("DeepSeek's Answers:\n")
        f.write("-" * 50 + "\n")
        f.write((results["deep_answer"] or "No response received") + "\n")


# ============ MAIN ============

def main():
    try:
        display_header()
        display_pricing_table()
        
        # Check API keys
        if not CLAUDE_API_KEY or not DEEP_API_KEY:
            console.print("[red]✗ API keys not found in .env file[/red]")
            input("\nPress Enter to exit...")
            return
        
        # ========== MAIN LOOP ==========
        while True:
            # Get input file
            input_path = get_input_file()
            if not input_path:
                if not Confirm.ask("\nTry another file?", default=True):
                    break
                continue
            
            console.print(f"[green]✓[/green] Selected: {input_path}")
            
            # Auto-generate output path
            output_path = get_output_path(input_path)
            console.print(f"[dim]Output will be saved to: {output_path}[/dim]")
            
            # Confirm before proceeding
            if not Confirm.ask("\nProceed with validation?", default=True):
                if not Confirm.ask("Try a different file?", default=True):
                    break
                continue
            
            # Load file
            console.print("\n[bold yellow]Initiating validation sequence...[/bold yellow]")
            
            with console.status("[bold blue]  Loading file...[/bold blue]", spinner="dots"):
                question_text = load_file(input_path)
            
            if not question_text:
                console.print("[red]✗ Error: Could not load file[/red]")
                if not Confirm.ask("\nTry another file?", default=True):
                    break
                continue
            
            console.print("[green]✓[/green] File loaded successfully")
            
            # Run validation
            results = validate_answers(question_text, max_retries=3)
            
            # Save output
            with console.status("[bold blue]  Saving answer key...[/bold blue]", spinner="dots"):
                save_answer_key(output_path, results, question_text)
            
            console.print(f"[green]✓[/green] Answer key saved to: {output_path}")
            console.print("\n[bold green]Done![/bold green]")
            
            # Ask to continue or quit
            console.print("\n" + "=" * 50)
            if not Confirm.ask("\nValidate another file?", default=True):
                break
        
        console.print("\n[cyan]Goodbye![/cyan]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()