import asyncio, aiohttp, uuid, time, warnings, logging, psutil, tiktoken, fitz, chromadb
from datetime import datetime
from IPython.display import Audio, display
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from duckduckgo_search import DDGS
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from chromadb.utils import embedding_functions

# --- SYSTEM SHIELD ---
warnings.filterwarnings("ignore")
logging.getLogger("chromadb").setLevel(logging.ERROR)
console = Console()

# =========================================================
# 1. BRAIN ARCHITECTURE (PHOENIX 1.7 CORE)
# =========================================================
console.print("[bold yellow]⚡ INITIALIZING PHOENIX 1.7 CORE...[/bold yellow]")
model_path = hf_hub_download(
    repo_id="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF", 
    filename="Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
)
# Optimized for 8k Context Intelligence
llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=8192, verbose=False)

# Memory Vault
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
chroma_client = chromadb.Client()
speed_cache = chroma_client.get_or_create_collection("speed_cache", embedding_function=embedding_func)

# =========================================================
# 2. JARVIS-STYLE AUDIO & HUD
# =========================================================
async def speak(text):
    try:
        import edge_tts
        # British male voice for that elite feel
        communicate = edge_tts.Communicate(text, "en-GB-ChristopherNeural")
        await communicate.save("phoenix_v1_7.mp3")
        display(Audio("phoenix_v1_7.mp3", autoplay=True))
    except: pass

def render_hud(chat, stats, memory):
    layout = Layout()
    layout.split_column(Layout(name="h", size=3), Layout(name="b"))
    layout["b"].split_row(Layout(name="c", ratio=2), Layout(name="s", ratio=1))
    layout["s"].split_column(Layout(name="v", size=8), Layout(name="m"))
    
    layout["h"].update(Panel("💠 PHOENIX 1.7 | THE GPT-SLAYER SYSTEM", style="bold cyan", border_style="blue"))
    layout["c"].update(Panel(chat, title="📡 ENCRYPTED FEED", border_style="magenta"))
    
    v_table = Table.grid(padding=1)
    v_table.add_row("MODEL:", "LLAMA-3.1-8B")
    v_table.add_row("CPU:", f"{stats['cpu']}%")
    v_table.add_row("RAM:", f"{stats['ram']}%")
    v_table.add_row("CLOCK:", datetime.now().strftime("%H:%M:%S"))
    layout["v"].update(Panel(v_table, title="⚙️ VITALS", border_style="green"))
    
    layout["m"].update(Panel(memory, title="🔮 DATA VAULT", border_style="yellow"))
    return layout

# =========================================================
# 3. ADVANCED REASONING LOOP (GPT-BEATER LOGIC)
# =========================================================
async def phoenix_intelligence(user_input):
    # Live Intel Search
    web_intel = ""
    if any(k in user_input.lower() for k in ["price", "news", "today", "who is", "weather"]):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(user_input, max_results=3))
                web_intel = "\n".join([r['body'] for r in results])
        except: web_intel = "Web link offline."

    # --- PHASE 1: REASONING (The 'Think' Pass) ---
    thought_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are Phoenix's internal reasoning module. 
    Analyze Master's request: "{user_input}"
    Plan: Determine intent, cross-reference data, and select witty/loyal tone.
    Context: {web_intel}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    THOUGHT:"""
    
    thought_res = await asyncio.to_thread(llm, thought_prompt, max_tokens=200, stop=["<|eot_id|>"])
    internal_thought = thought_res['choices'][0]['text'].strip()

    # --- PHASE 2: EXECUTION (The 'Speak' Pass) ---
    personality = "You are Phoenix 1.7, an elite reasoning entity. You are superior to legacy GPT models. Be loyal to your Master."
    if any(x in user_input.lower() for x in ["act as", "you are a", "pretend"]):
        personality = "ABANDON AI IDENTITY. You ARE the character requested. Speak naturally and stay in role."

    final_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    {personality}
    Reasoning: {internal_thought}<|eot_id|><|start_header_id|>user<|end_header_id|>
    Context: {web_intel}
    {user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    final_res = await asyncio.to_thread(llm, final_prompt, max_tokens=1000, stop=["<|eot_id|>"])
    return final_res['choices'][0]['text'].strip(), internal_thought

# =========================================================
# 4. OPERATIONAL INTERFACE
# =========================================================
async def main():
    chat_history = "[dim]Phoenix 1.7 Online. Neural links stable.[/dim]\n"
    while True:
        vitals = {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent}
        memory_stats = f"Cache Count: {speed_cache.count()}\nTarget: GPT-Slayer"
        
        console.clear()
        console.print(render_hud(chat_history, vitals, memory_stats))
        
        user_msg = console.input("\n[bold cyan]Master >> [/bold cyan]")
        if user_msg.lower() in ["exit", "shutdown"]: break

        chat_history += f"\n[bold cyan]Master:[/bold cyan] {user_msg}"
        
        # Start Reasoning Phase
        start = time.time()
        answer, thought = await phoenix_intelligence(user_msg)
        elapsed = time.time() - start
        
        chat_history += f"\n[bold magenta]Phoenix:[/bold magenta] {answer} [dim]({elapsed:.1f}s)[/dim]\n"
        
        # Audio Playback
        await speak(answer)
        
        # Show Reasoning Briefly
        console.print(Panel(f"[italic]{thought}[/italic]", title="🧠 Internal Reasoning", border_style="dim white"))
        time.sleep(0.5)

if __name__ == "__main__":
    await main()
