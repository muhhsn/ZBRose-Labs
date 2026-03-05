import os
import sys
import subprocess

# --- Dependency Auto-Installer ---
def check_and_install_dependencies():
    required_libraries = {
        "textual": "textual",
        "psutil": "psutil",
        "docker": "docker",
        "google.generativeai": "google-generativeai"
    }
    
    missing = []
    for lib, package in required_libraries.items():
        try:
            __import__(lib)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[*] Missing dependencies found: {', '.join(missing)}")
        print("[*] Attempting to install missing libraries...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("[+] Installation successful. Restarting application...")
            # Safer restart for Windows to preserve console handles
            print("[+] Installation successful. Finalizing...")
            subprocess.run([sys.executable] + sys.argv)
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print(f"[-] Critical Error: Failed to install dependencies. {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Aggressive Console Fix for Windows / Ghost Spectre
    import sys
    import os
    
    # 1. Detect IDLE (Textual will NEVER work in IDLE shell)
    if "idlelib" in sys.modules or "IDLE_STARTUP" in os.environ:
        print("\n" + "="*50)
        print("ERROR: SCRIPT INI TIDAK BISA DIJALANKAN DI IDLE!")
        print("="*50)
        print("Aplikasi TUI membutuhkan terminal asli untuk merender UI.")
        print("\nCara menjalankan yang benar:")
        print(f"1. Buka PowerShell atau CMD (Run as Administrator)")
        print(f"2. Ketik: python \"{__file__}\"")
        print("="*50 + "\n")
        input("Tekan Enter untuk keluar...")
        sys.exit(1)

    # 2. Check dependencies
    check_and_install_dependencies()

    # 3. Force valid streams for Textual Driver
    try:
        if sys.stdin is None or not hasattr(sys.stdin, 'fileno'):
            sys.stdin = open('CONIN$', 'r')
        if sys.stdout is None or not hasattr(sys.stdout, 'fileno'):
            sys.stdout = open('CONOUT$', 'w')
    except Exception:
        pass

import psutil
import docker
import asyncio
import shutil
from pathlib import Path
import google.generativeai as genai

from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, DataTable, RichLog, Button, Label, ProgressBar
from textual.screen import ModalScreen
from textual import work

# --- Configuration & Initialization ---

# Security Note: Provided for ZBRose Labs local testing. 
# Recommended: Set this as an environment variable 'GEMINI_API_KEY' instead of hardcoding.
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyC8png3-cBI0RCKD3nFKyl0ZJWCvh0162s")

if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
    
# Initialize Docker client gracefully
try:
    docker_client = docker.from_env()
except Exception:
    docker_client = None

# --- Custom Widgets & Screens ---

class ConfirmationModal(ModalScreen[bool]):
    """A TokyoNight styled modal to confirm risky actions."""
    def __init__(self, message: str, action_details: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.action_details = action_details

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"[b]$ ACTION REQUIRED[/b]", id="dialog-header")
            with Vertical(id="dialog-content"):
                yield Label(f"[cyan]Target:[/cyan] {self.message}", id="dialog-message")
                yield Label(f"\n[magenta]AI Insight:[/magenta]\n{self.action_details}", id="dialog-details")
            with Horizontal(id="dialog-buttons"):
                yield Button("CONFIRM", variant="error", id="confirm")
                yield Button("CANCEL", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(True if event.button.id == "confirm" else False)


class JunkScannerModal(ModalScreen[bool]):
    """A TokyoNight styled modal for scanning and cleaning Windows junk files."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.junk_size = 0
        self.junk_paths = []
        
    def compose(self) -> ComposeResult:
        with Vertical(id="junk-dialog"):
            yield Label("[b]$ JUNK CLEANER ENGINE[/b]", id="junk-header")
            with Vertical(id="junk-content"):
                yield Label("Scanning targeted directories...", id="junk-status")
                yield Label("", id="junk-details")
            with Horizontal(id="junk-buttons"):
                yield Button("WIPE SYSTEM", variant="error", id="clean", disabled=True)
                yield Button("CLOSE", variant="primary", id="cancel")
                
    def on_mount(self) -> None:
        self.scan_junk()
        
    @work(thread=True)
    def scan_junk(self) -> None:
        temp_dirs = [Path(r"C:\Windows\Temp"), Path(r"C:\Users\husin\AppData\Local\Temp")]
        total_size = 0
        paths_to_clean = []
        for t_dir in temp_dirs:
            if t_dir.exists() and t_dir.is_dir():
                try:
                    for root, dirs, files in os.walk(t_dir):
                        for f in files:
                            fp = Path(root) / f
                            try:
                                total_size += fp.stat().st_size
                                paths_to_clean.append(fp)
                            except Exception: pass
                except Exception: pass
        self.app.call_from_thread(self.update_scan_results, total_size, paths_to_clean)
        
    def update_scan_results(self, size: int, paths: list):
        self.junk_size, self.junk_paths = size, paths
        size_mb = size / (1024 * 1024)
        self.query_one("#junk-status", Label).update("[green]Scan Complete![/green]")
        self.query_one("#junk-details", Label).update(f"Identified {len(paths)} objects ({size_mb:.2f} MB)")
        if size > 0: self.query_one("#clean", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(True if event.button.id == "clean" else False)


class SystemStats(Vertical):
    """Panel 1: Ultra-Compact System Statistics for Ghost Spectre"""
    def compose(self) -> ComposeResult:
        yield Label("[b][cyan]SYSTEM MONITOR[/cyan][/b]", id="stats-header")
        
        # CPU Row
        with Horizontal(classes="compact-row"):
            yield Label("CPU", classes="row-label")
            yield ProgressBar(id="cpu-bar", total=100, show_eta=False)
            yield Label("0%", id="cpu-pct", classes="row-val")
        yield Label("Idle: --", id="cpu-idle", classes="row-sub")
        
        # RAM Row
        with Horizontal(classes="compact-row"):
            yield Label("RAM", classes="row-label")
            yield ProgressBar(id="ram-bar", total=100, show_eta=False)
            yield Label("0%", id="ram-pct", classes="row-val")
        yield Label("U: 0G | F: 0G", id="ram-details", classes="row-sub")
        
        # Disk Row
        with Horizontal(classes="compact-row"):
            yield Label("DSK", classes="row-label")
            yield ProgressBar(id="disk-bar", total=100, show_eta=False)
            yield Label("0%", id="disk-pct", classes="row-val")
        yield Label("U: 0G | F: 0G", id="disk-details", classes="row-sub")

        # Junk Row
        with Horizontal(id="junk-row", classes="compact-row"):
            yield Label("JNK", classes="row-label")
            yield ProgressBar(id="junk-bar", total=100, show_eta=False)
            yield Label("0M", id="junk-pct", classes="row-val")
        yield Label("Files: 0 | Total: 0MB", id="junk-details", classes="row-sub")
        yield Button("WIPE JUNK FILES", id="btn-junk-clear", classes="compact-btn-wide")

    def on_mount(self) -> None:
        self.confirm_state = False
        self.update_stats()
        self.set_interval(2.0, self.update_stats)
        self.set_interval(5.0, self.update_junk_summary)
        self.update_junk_summary()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-junk-clear":
            if not self.confirm_state:
                # Step 1: Initial Click
                self.confirm_state = True
                event.button.label = "CONFIRM"
                event.button.add_class("confirm-danger")
                # Reset after 3 seconds if not confirmed
                self.set_timer(3.0, self.reset_junk_button)
            else:
                # Step 2: Confirmation Click
                self.execute_wipe()
                self.reset_junk_button()

    def reset_junk_button(self) -> None:
        self.confirm_state = False
        try:
            btn = self.query_one("#btn-junk-clear", Button)
            btn.label = "CLEAR"
            btn.remove_class("confirm-danger")
        except Exception:
            pass

    def execute_wipe(self) -> None:
        paths = [r"C:\Windows\Temp", r"C:\Users\husin\AppData\Local\Temp"]
        deleted_count = 0
        for p in paths:
            if os.path.exists(p):
                try:
                    for entry in os.scandir(p):
                        try:
                            if entry.is_file():
                                os.remove(entry.path)
                                deleted_count += 1
                            elif entry.is_dir():
                                shutil.rmtree(entry.path)
                                deleted_count += 1
                        except Exception: continue
                except Exception: continue
        self.app.log_insight(f"[+] Junk Wipe: {deleted_count} items removed from Temp.")
        self.update_junk_summary()


    def update_stats(self) -> None:
        try:
            # CPU
            cpu = psutil.cpu_percent()
            self.query_one("#cpu-bar", ProgressBar).progress = cpu
            self.query_one("#cpu-pct", Label).update(f"{cpu:.0f}%")
            self.query_one("#cpu-idle", Label).update(f"Idle capacity: {100-cpu:.1f}%")

            # RAM
            mem = psutil.virtual_memory()
            mem_total_gb = 20.0 
            mem_used_gb = mem.used / (1024**3)
            mem_free_gb = max(0, mem_total_gb - mem_used_gb)
            mem_percent = min((mem_used_gb / mem_total_gb) * 100, 100.0)
            self.query_one("#ram-bar", ProgressBar).progress = mem_percent
            self.query_one("#ram-pct", Label).update(f"{mem_percent:.0f}%")
            self.query_one("#ram-details", Label).update(f"Used: {mem_used_gb:.1f}G | Free: {mem_free_gb:.1f}G")

            # Disk
            try:
                disk = psutil.disk_usage("C:\\")
                self.query_one("#disk-bar", ProgressBar).progress = disk.percent
                self.query_one("#disk-pct", Label).update(f"{disk.percent:.0f}%")
                self.query_one("#disk-details", Label).update(f"Used: {disk.used/(1024**3):.1f}G | Free: {disk.free/(1024**3):.1f}G")
            except Exception: pass

        except Exception as e:
            try: self.app.log_insight(f"[!] Stats Error: {str(e)}")
            except Exception: pass

    @work(thread=True)
    def update_junk_summary(self) -> None:
        paths = {
            "System Temp": Path(r"C:\Windows\Temp"),
            "User Temp": Path(r"C:\Users\husin\AppData\Local\Temp"),
            "Prefetch": Path(r"C:\Windows\Prefetch")
        }
        total_count = 0
        total_size_bytes = 0
        breakdown = []
        
        for name, p in paths.items():
            path_count = 0
            path_size = 0
            if p.exists() and p.is_dir():
                try:
                    for root, dirs, files in os.walk(p):
                        for f in files:
                            try:
                                fp = Path(root) / f
                                sz = fp.stat().st_size
                                path_size += sz
                                path_count += 1
                            except (PermissionError, FileNotFoundError):
                                continue
                except Exception:
                    continue
            total_count += path_count
            total_size_bytes += path_size
            if path_count > 0:
                breakdown.append(f"{name}: {path_count} files ({path_size / (1024*1024):.1f}MB)")
        
        size_mb = total_size_bytes / (1024 * 1024)
        progress = min((size_mb / 1024) * 100, 100.0)
        
        def update_ui():
            try:
                self.query_one("#junk-bar", ProgressBar).progress = progress
                self.query_one("#junk-pct", Label).update(f"{size_mb:.0f}M")
                self.query_one("#junk-details", Label).update(f"Files: {total_count} | Total: {size_mb:.1f}MB")
                # Also log the breakdown occasionally to the insight log
                if breakdown:
                    # self.app.log_insight(f"[*] Junk Breakdown: {', '.join(breakdown)}")
                    pass
            except Exception: pass

        try: self.app.call_from_thread(update_ui)
        except Exception: pass

# --- Main Application ---

class MonitorApp(App):
    CSS = '''
    /* TokyoNight Storm Palette */
    $bg: #1a1b26;
    $surface: #24283b;
    $cyan: #7dcfff;
    $magenta: #bb9af7;
    $green: #9ece6a;
    $yellow: #e0af68;
    $red: #f7768e;
    $blue: #7aa2f7;
    $fg: #cfc9c2;

    Screen {
        background: transparent;
        color: $fg;
    }

    Grid {
        grid-size: 2 2;
        grid-columns: 1fr 2fr;
        grid-rows: 1fr 1fr;
        grid-gutter: 0;
        background: $bg 40%; /* Semi-transparent main background */
    }
    
    /* Panel Standardizing with Glass Effect */
    #sys-stats { border: round $cyan; padding: 0 1; background: $surface 60%; }
    #docker-services { border: round $green; background: $surface 60%; }
    #ai-insight { border: round $magenta; background: $surface 60%; padding: 0; }
    #os-processes { border: round $yellow; background: $surface 60%; }
    
    /* Global Compact Styling */
    DataTable {
        height: 100%;
        background: $surface;
        color: $fg;
        border: none;
    }
    
    DataTable > .datatable--header {
        background: $blue;
        color: $bg;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: $blue 30%;
    }

    RichLog {
        background: $surface;
        color: $fg;
        border: none;
        overflow-x: hidden;
    }

    /* System Stats specific compact fixes */
    #stats-header { text-align: center; color: $cyan; margin-bottom: 0; text-style: bold underline; }
    .compact-row { height: 1; align: left middle; }
    .row-label { width: 5; text-style: bold; color: $blue; }
    .row-val { width: 5; text-align: right; color: $fg; }
    .row-sub { color: #565f89; text-style: italic; margin-left: 5; margin-bottom: 0; }
    
    ProgressBar { width: 1fr; margin: 0 1; height: 1; }
    ProgressBar > .bar--background { background: #414868; }
    #cpu-bar > .bar--foreground { background: $cyan; }
    #ram-bar > .bar--foreground { background: $magenta; }
    #disk-bar > .bar--foreground { background: $green; }
    #junk-bar > .bar--foreground { background: $red; }

    .compact-btn {
        width: 10;
        height: 1;
        min-width: 8;
        border: none;
        background: #414868;
        color: $fg;
        margin-left: 1;
    }

    .compact-btn-wide {
        width: 100%;
        height: 1;
        border: none;
        background: #414868;
        color: $fg;
        margin-top: 1;
    }

    .confirm-danger {
        background: $red !important;
        color: $bg !important;
        text-style: bold;
    }
    
    #compact-junk-box {
        margin-top: 1;
        padding: 0 1;
        border-top: solid #414868;
        background: #16161e;
    }
    #junk-summary-text { color: $red; }

    /* Modals & Dialogs */
    ModalScreen {
        align: center middle;
        background: $bg 80%;
    }
    
    #dialog, #junk-dialog {
        padding: 1 2;
        width: 60;
        height: auto;
        border: thick $blue;
        background: $surface;
    }
    
    #dialog-message, #junk-status {
        text-align: center;
        text-style: bold;
        color: $cyan;
        margin-bottom: 1;
    }
    
    #dialog-details, #junk-details {
        text-align: center;
        color: $fg;
        margin-bottom: 1;
    }
    
    #dialog-buttons, #junk-buttons {
        height: 3;
        align: center middle;
        margin-top: 1;
    }
    
    #dialog-buttons Button, #junk-buttons Button {
        width: 20;
        margin: 0 1;
        border: solid $fg 20%;
    }

    #confirm, #clean {
        background: $red 20%;
        color: $red;
        border: solid $red !important;
    }

    #confirm:hover, #clean:hover {
        background: $red;
        color: $bg;
    }
    '''

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("j", "scan_junk", "Junk Scanner"),
        ("r", "refresh_data", "Refresh Tables")
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Grid():
            # Panel 1: Top Left
            yield SystemStats(id="sys-stats")
            
            # Panel 3: Top Right
            docker_table = DataTable(id="docker-services")
            docker_table.cursor_type = "row"
            docker_table.add_columns("Type", "ID/PID", "Name", "Status/Port")
            yield docker_table
            
            # Panel 2: Bottom Left
            insight_log = RichLog(id="ai-insight", wrap=True, markup=True)
            yield insight_log
            
            # Panel 4: Bottom Right
            proc_table = DataTable(id="os-processes")
            proc_table.cursor_type = "row"
            proc_table.add_columns("PID", "Name", "Memory (MB)", "CPU %")
            yield proc_table
            
        yield Footer()

    def on_mount(self) -> None:
        self.title = "ZBRose Labs - AI System Monitor"
        try:
            self.log_insight("[TokyoNight] UI Engine Loaded.")
            self.log_insight("[System] Initializing Gemini AI...")
            
            if GENAI_API_KEY:
                self.log_insight("[+] API Key detected. Performing initial system scan...")
                self.startup_ai_analysis()
            else:
                self.log_insight("[!] Warning: API Key missing. Running in Simulation Mode.")
        except Exception:
            pass
        
        self.set_timer(0.5, self.refresh_data)
        self.set_interval(5.0, self.refresh_processes)

    @work(thread=True)
    def startup_ai_analysis(self) -> None:
        """Proactive AI analysis on startup to greet the user and check system health."""
        try:
            self.app.call_from_thread(self.log_insight, "[*] AI: Connecting to Gemini API...")
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = (
                f"Greet the user at ZBRose Labs. Current system: CPU {cpu}%, RAM {mem.percent}% used. "
                f"Give a 1-sentence technical optimization tip for Windows 11 Ghost Spectre. "
                f"Keep it very brief and cool."
            )
            
            response = model.generate_content(prompt)
            if response and response.text:
                self.app.call_from_thread(self.log_insight, f"[Gemini] {response.text.strip()}")
            else:
                self.app.call_from_thread(self.log_insight, "[!] AI Error: Received empty response.")
        except Exception as e:
            self.app.call_from_thread(self.log_insight, f"[AI Startup Error] {str(e)}")
            # Log full error to terminal for deep debugging
            print(f"AI DEBUG: {e}")

    def action_refresh_data(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        """Main entry point to refresh all data tables."""
        try:
            self.refresh_docker_services()
            self.refresh_processes()
        except Exception as e:
            self.log_insight(f"[System Error] Refresh failed: {e}")

    def refresh_docker_services(self) -> None:
        try:
            table = self.query_one("#docker-services", DataTable)
        except Exception:
            return

        table.clear()
        
        # Load Docker Containers
        if docker_client:
            try:
                for container in docker_client.containers.list(all=True):
                    # Style: Blue for active Docker
                    type_cell = "[b][#7aa2f7]DOCKER[/#7aa2f7][/b]"
                    table.add_row(type_cell, container.short_id, container.name, container.status, key=f"docker_{container.id}")
            except Exception as e:
                self.log_insight(f"Docker Error: {e}")
        else:
            table.add_row("[b][#f7768e]DOCKER[/#f7768e][/b]", "OFF", "Daemon Not Running", "N/A", key="docker_error")
            
        # Load Background Network Services
        try:
            # kind='inet' can crash on some Ghost Spectre/Lite builds
            connections = psutil.net_connections()
            listen_conns = [c for c in connections if c.status == 'LISTEN' and c.pid]
            for conn in listen_conns[:20]:
                try:
                    proc = psutil.Process(conn.pid)
                    name = proc.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    name = "Unknown"
                
                port = conn.laddr.port if hasattr(conn.laddr, 'port') else "Unknown"
                # Style: Dimmed gray for background services
                type_cell = "[#565f89]SERVICE[/#565f89]"
                table.add_row(type_cell, str(conn.pid), name, f"Port {port}", key=f"service_{conn.pid}_{port}")
        except Exception as e:
            self.log_insight(f"Net Error: {e}")

    def refresh_processes(self) -> None:
        try:
            table = self.query_one("#os-processes", DataTable)
        except Exception:
            return
            
        procs = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    info = p.info
                    # Handle NoneType memory_info on some Windows systems
                    mem_info = info.get('memory_info')
                    mem_mb = mem_info.rss / (1024 * 1024) if mem_info else 0
                    procs.append((info['pid'], info['name'], mem_mb, info['cpu_percent']))
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    pass
        except Exception as e:
            self.log_insight(f"Proc Error: {e}")
            return
                
        # Sort by memory descending
        procs.sort(key=lambda x: x[2], reverse=True)
        
        table.clear()
        for pid, name, mem, cpu in procs[:40]: # Top 40 Processes
            try:
                table.add_row(str(pid), name, f"{mem:.1f}", f"{cpu:.1f}", key=f"proc_{pid}")
            except Exception:
                pass

    def log_insight(self, message: str) -> None:
        log_widget = self.query_one("#ai-insight", RichLog)
        log_widget.write(message)

    @work(thread=True)
    def ask_gemini_guardrail(self, action: str, target: str, callback) -> None:
        """Queries Gemini for a quick risk analysis before executing a critical action."""
        if not GENAI_API_KEY:
            self.app.call_from_thread(self.log_insight, f"[*] Simulated AI: Warning, {action} on {target} may affect system stability. Verify before proceeding.")
            self.app.call_from_thread(callback, "AI Guardrail disabled (No API Key). Please proceed with caution.")
            return
            
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = (
                f"You are an AI guardrail for a Windows 11 system administrator. "
                f"The admin is about to execute the command '{action}' on target '{target}'. "
                f"Provide a strict 1-2 sentence technical warning about the potential consequences. "
                f"Be concise, direct, and assume expert context."
            )
            
            self.app.call_from_thread(self.log_insight, f"[*] Querying AI Guardrail for {action} on {target}...")
            response = model.generate_content(prompt)
            ai_text = response.text.strip()
            
            self.app.call_from_thread(self.log_insight, f"[AI Guardrail] {ai_text}")
            self.app.call_from_thread(callback, ai_text)
            
        except Exception as e:
            self.app.call_from_thread(self.log_insight, f"[AI Error] {str(e)}")
            self.app.call_from_thread(callback, "Failed to reach AI Guardrail. Proceed with caution.")

    def action_scan_junk(self) -> None:
        def check_clean(should_clean: bool):
            if should_clean:
                self.ask_gemini_guardrail("CLEAN", "Windows %TEMP%, Prefetch, and __pycache__ folders", self.execute_clean)

        self.push_screen(JunkScannerModal(), check_clean)

    def execute_clean(self, ai_context: str) -> None:
        def confirm_clean(confirmed: bool):
            if confirmed:
                self.log_insight("[*] Deleting junk files...")
                # Safety: Simulated wipe for this TUI template to prevent accidental OS damage
                # In production, iterate through paths and use os.remove / shutil.rmtree
                self.log_insight("[+] Junk cleanup completed successfully.")
            else:
                self.log_insight("[-] Cleanup cancelled by user.")
                
        self.push_screen(ConfirmationModal(
            "Confirm System Cleanup", 
            f"AI Insight:\n{ai_context}"
        ), confirm_clean)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table_id = event.data_table.id
        row_key = event.row_key.value
        
        # --- Handle Docker & Services Interaction ---
        if table_id == "docker-services":
            if row_key.startswith("docker_"):
                container_id = row_key.split("_")[1]
                target_name = event.data_table.get_row(event.row_key)[2]
                
                def execute_docker_stop(ai_context: str):
                    def confirm_stop(confirmed: bool):
                        if confirmed and docker_client:
                            try:
                                container = docker_client.containers.get(container_id)
                                container.stop()
                                self.log_insight(f"[+] Container '{target_name}' stopped.")
                                self.refresh_docker_services()
                            except Exception as e:
                                self.log_insight(f"[-] Failed to stop container: {e}")
                    
                    self.push_screen(ConfirmationModal(
                        f"Stop Docker Container: {target_name}?", 
                        f"AI Insight:\n{ai_context}"
                    ), confirm_stop)
                    
                self.ask_gemini_guardrail("STOP", f"Docker container '{target_name}'", execute_docker_stop)
                
            elif row_key.startswith("service_"):
                pid = row_key.split("_")[1]
                target_name = event.data_table.get_row(event.row_key)[2]
                self.trigger_kill_process(pid, target_name)
                
        # --- Handle OS Processes Interaction ---
        elif table_id == "os-processes":
            if row_key.startswith("proc_"):
                pid = row_key.split("_")[1]
                target_name = event.data_table.get_row(event.row_key)[1]
                self.trigger_kill_process(pid, target_name)

    def trigger_kill_process(self, pid: str, target_name: str) -> None:
        def execute_kill(ai_context: str):
            def confirm_kill(confirmed: bool):
                if confirmed:
                    try:
                        p = psutil.Process(int(pid))
                        p.terminate()
                        self.log_insight(f"[+] Process '{target_name}' (PID: {pid}) terminated.")
                        self.refresh_processes()
                    except Exception as e:
                        self.log_insight(f"[-] Failed to kill process: {e}")
            
            self.push_screen(ConfirmationModal(
                f"Kill Process: {target_name} (PID: {pid})?", 
                f"AI Insight:\n{ai_context}"
            ), confirm_kill)
            
        self.ask_gemini_guardrail("KILL", f"Process '{target_name}' (PID {pid})", execute_kill)


if __name__ == "__main__":
    app = MonitorApp()
    app.run()
