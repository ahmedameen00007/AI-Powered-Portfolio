"""
chatbot.py

A professional interactive terminal chatbot for OVI (Ahmed Ameen's portfolio RAG system).
Supports interactive conversational mode with memory, streaming responses, and one-shot queries.
Uses the Groq API for prompt synthesis.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure terminal output encoding to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from builders.answer_generator import AnswerGenerator
from builders.embeddings_builder import EmbeddingBackendUnavailable
from builders.query_expander import QueryExpander
from builders.retriever import Retriever

# Try importing dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
except ImportError:
    pass

# Try importing colorama for colorized terminal output
try:
    import colorama
    from colorama import Fore, Style
    colorama.init()
except ImportError:
    class DummyColor:
        def __getattr__(self, name: str) -> str:
            return ""
    Fore = DummyColor()
    Style = DummyColor()


SMOKE_TEST_QUERIES = [
    "Who is Ahmed Ameen?",
    "What certifications does Ahmed have?",
    "Which certifications did he complete on Coursera?",
    "What projects has he worked on?",
    "What did he study at university?",
]


def print_banner() -> None:
    """Prints a professional, clean startup banner for the chatbot."""
    banner = f"""{Fore.CYAN}{Style.BRIGHT}============================================================
🤖  OVI Chatbot — Portfolio Assistant for Ahmed Ameen
============================================================{Fore.RESET}
Welcome! Ask me anything about Ahmed's background, certifications, 
projects, or education.

{Fore.YELLOW}Commands:{Fore.RESET}
  {Fore.GREEN}/exit{Fore.RESET} or {Fore.GREEN}/quit{Fore.RESET} - Exit the chatbot
  {Fore.GREEN}/clear{Fore.RESET}        - Clear conversation history
  {Fore.GREEN}/history{Fore.RESET}      - View current conversation history
  {Fore.GREEN}/help{Fore.RESET}         - Show this help message
{Fore.CYAN}============================================================{Style.RESET_ALL}"""
    print(banner)


def handle_command(cmd: str, history: list[dict[str, str]]) -> bool:
    """
    Handles slash commands. Returns True if execution should continue,
    False if it should exit.
    """
    clean_cmd = cmd.strip().lower()
    if clean_cmd in ("/exit", "/quit"):
        print(f"\n{Fore.CYAN}Goodbye! 👋{Style.RESET_ALL}\n")
        return False
    elif clean_cmd == "/clear":
        history.clear()
        print(f"\n{Fore.GREEN}✓ Conversation history cleared.{Style.RESET_ALL}\n")
    elif clean_cmd == "/history":
        if not history:
            print(f"\n{Fore.YELLOW}Conversation history is empty.{Style.RESET_ALL}\n")
        else:
            print(f"\n{Fore.CYAN}--- Current History ---{Style.RESET_ALL}")
            for msg in history:
                role_label = "You" if msg["role"] == "user" else "Assistant"
                color = Fore.GREEN if msg["role"] == "user" else Fore.BLUE
                print(f"{color}{Style.BRIGHT}{role_label}:{Style.RESET_ALL} {msg['content']}")
            print(f"{Fore.CYAN}-----------------------{Style.RESET_ALL}\n")
    elif clean_cmd == "/help":
        print(f"\n{Fore.YELLOW}Available commands:{Style.RESET_ALL}")
        print("  /exit, /quit - Exit the chatbot")
        print("  /clear       - Clear conversation history")
        print("  /history     - View conversation history in memory")
        print("  /help        - Show this menu\n")
    else:
        print(f"\n{Fore.RED}Unknown command: {cmd}. Type /help for available commands.{Style.RESET_ALL}\n")
    return True


def run_interactive(
    retriever: Retriever,
    generator: AnswerGenerator,
    query_expander: QueryExpander,
    top_k: int,
    stream: bool,
    entity_counts: dict,
) -> None:
    """Starts the interactive multi-turn chat loop."""
    print_banner()
    history: list[dict[str, str]] = []

    while True:
        try:
            # Prompt the user
            user_input = input(f"{Fore.GREEN}{Style.BRIGHT}You:{Style.RESET_ALL} ").strip()
            if not user_input:
                continue

            # Check for command
            if user_input.startswith("/"):
                should_continue = handle_command(user_input, history)
                if not should_continue:
                    break
                continue

            # --- Query Expansion ---
            print(f"{Fore.YELLOW}[🔍 Expanding query...]{Style.RESET_ALL}", end="\r")
            expansion = query_expander.expand(user_input)
            language = expansion["language"]
            search_queries = expansion["search_queries"]
            # Clear the indicator line
            print(" " * 40, end="\r")

            # Retrieve context chunks using expanded queries
            results = retriever.search_multi(search_queries, top_k=top_k)

            # Generate and print answer
            print(f"{Fore.BLUE}{Style.BRIGHT}Assistant:{Style.RESET_ALL} ", end="")
            sys.stdout.flush()

            if stream:
                answer_chunks = []
                # AnswerGenerator returns an iterator in streaming mode
                for token in generator.generate(
                    user_input, results, history=history, stream=True,
                    language=language, entity_counts=entity_counts
                ):
                    print(token, end="")
                    sys.stdout.flush()
                    answer_chunks.append(token)
                print()  # Add trailing newline
                full_answer = "".join(answer_chunks)
            else:
                # AnswerGenerator returns a full string in non-streaming mode
                full_answer = generator.generate(
                    user_input, results, history=history, stream=False,
                    language=language, entity_counts=entity_counts
                )
                print(full_answer)

            # Update history with user query and assistant response
            if not full_answer.startswith("✗"):
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": full_answer})

            print()  # Spacer line

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print(f"\n\n{Fore.CYAN}Goodbye! 👋{Style.RESET_ALL}\n")
            break
        except Exception as exc:
            print(f"\n{Fore.RED}✗ Error: {exc}{Style.RESET_ALL}\n")


def run_one_shot(
    query: str,
    retriever: Retriever,
    generator: AnswerGenerator,
    query_expander: QueryExpander,
    top_k: int,
    entity_counts: dict,
) -> None:
    """Executes a single RAG query and prints the synthesized response."""
    try:
        expansion = query_expander.expand(query)
        language = expansion["language"]
        search_queries = expansion["search_queries"]
        results = retriever.search_multi(search_queries, top_k=top_k)
        print(f"{Fore.GREEN}{Style.BRIGHT}Query:{Style.RESET_ALL} {query}\n")
        print(f"{Fore.BLUE}{Style.BRIGHT}Assistant:{Style.RESET_ALL} ")

        # Stream the output directly
        for token in generator.generate(
            query, results, history=None, stream=True,
            language=language, entity_counts=entity_counts
        ):
            print(token, end="")
            sys.stdout.flush()
        print("\n")
    except Exception as exc:
        print(f"{Fore.RED}✗ Error: {exc}{Style.RESET_ALL}\n")


def run_smoke_test(
    retriever: Retriever,
    generator: AnswerGenerator,
    query_expander: QueryExpander,
    entity_counts: dict,
) -> None:
    """Runs a quick series of predefined queries to test chatbot health."""
    print(f"{Fore.CYAN}{Style.BRIGHT}Running Chatbot Smoke Tests...{Style.RESET_ALL}\n")
    for query in SMOKE_TEST_QUERIES:
        print("-" * 60)
        run_one_shot(query, retriever, generator, query_expander, top_k=3, entity_counts=entity_counts)
    print("=" * 60)
    print(f"{Fore.GREEN}{Style.BRIGHT}Smoke tests complete.{Style.RESET_ALL}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OVI Chatbot — Portfolio RAG assistant for Ahmed Ameen."
    )
    parser.add_argument(
        "--query",
        type=str,
        help="A one-shot query to ask the chatbot. Runs in non-interactive mode.",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run a suite of smoke test queries to verify system health.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=15,
        help="Number of retrieved chunks to feed into the generator prompt context.",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming mode (return full responses at once).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="openai/gpt-oss-120b",
        help="Groq LLM model name to use.",
    )
    args = parser.parse_args()

    # Pre-flight check: Load retriever index
    try:
        retriever = Retriever()
    except FileNotFoundError as exc:
        print(f"{Fore.RED}✗ {exc}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please build the embeddings index first by running:{Style.RESET_ALL}")
        print("  python scripts/build_embeddings.py")
        sys.exit(1)
    except EmbeddingBackendUnavailable as exc:
        print(f"{Fore.RED}✗ Embedding backend unavailable: {exc}{Style.RESET_ALL}")
        sys.exit(2)

    # Fetch total entity counts from the knowledge base (used for completeness hints)
    try:
        entity_counts = retriever.get_entity_counts()
    except Exception:
        entity_counts = {}

    # Initialize answer generator
    try:
        generator = AnswerGenerator(model_name=args.model)
    except Exception as exc:
        print(f"{Fore.RED}✗ Error initializing generator: {exc}{Style.RESET_ALL}")
        sys.exit(1)

    # Initialize query expander
    try:
        query_expander = QueryExpander()
    except Exception as exc:
        print(f"{Fore.YELLOW}⚠ Query expansion unavailable: {exc}. Using raw queries.{Style.RESET_ALL}")
        # Create a no-op fallback expander inline
        class _FallbackExpander:
            def expand(self, q: str) -> dict:
                return {"original": q, "language": "en", "search_queries": [q]}
        query_expander = _FallbackExpander()  # type: ignore[assignment]

    # Run correct mode
    if args.query:
        run_one_shot(args.query, retriever, generator, query_expander, top_k=args.top_k, entity_counts=entity_counts)
    elif args.smoke_test:
        run_smoke_test(retriever, generator, query_expander, entity_counts=entity_counts)
    else:
        run_interactive(retriever, generator, query_expander, top_k=args.top_k, stream=not args.no_stream, entity_counts=entity_counts)


if __name__ == "__main__":
    main()
