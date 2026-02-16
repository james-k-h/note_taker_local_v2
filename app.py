import tkinter as tk
from tkinter import messagebox, scrolledtext, font as tkfont
import subprocess
import os
from dotenv import load_dotenv
import json
import sys
from pathlib import Path
import threading
from datetime import datetime, timedelta


BASE_DIR = Path(__file__).resolve().parent
NOTES_DIR = BASE_DIR / "notes"

# Create notes directory if it doesn't exist
try:
    NOTES_DIR.mkdir(exist_ok=True)
    print(f"Notes directory: {NOTES_DIR}")
except Exception as e:
    print(f"Error creating notes directory: {e}")

NOTES_INDEX_FILE = NOTES_DIR / "notes_index.json"


class Theme:
    """Design system for consistent styling"""

    # Colors
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F8F9FA"
    BG_HOVER = "#E9ECEF"

    ACCENT_PRIMARY = "#4A90E2"
    ACCENT_HOVER = "#357ABD"
    ACCENT_DARK = "#2E5C8A"

    TEXT_PRIMARY = "#1A1A1A"
    TEXT_SECONDARY = "#6C757D"
    TEXT_LIGHT = "#ADB5BD"

    BORDER = "#DEE2E6"
    SUCCESS = "#28A745"
    ERROR = "#DC3545"
    WARNING = "#FFC107"

    # Fonts
    FONT_TITLE = ("Segoe UI", 20, "bold")
    FONT_SUBTITLE = ("Segoe UI", 10)
    FONT_CATEGORY = ("Segoe UI", 14, "bold")
    FONT_BUTTON = ("Segoe UI", 10)
    FONT_BUTTON_LARGE = ("Segoe UI", 11)
    FONT_STATUS = ("Segoe UI", 9)
    FONT_NOTE = ("Segoe UI", 10)
    FONT_NOTE_TITLE = ("Segoe UI", 12, "bold")

    # Spacing
    PADDING_XL = 24
    PADDING_L = 14
    PADDING_M = 10
    PADDING_S = 5

    # Dimensions
    BUTTON_HEIGHT = 32
    BUTTON_HEIGHT_SMALL = 22
    BORDER_RADIUS = 6


class ModernButton(tk.Button):
    """Custom button with hover effects and modern styling"""

    def __init__(self, parent, style="primary", **kwargs):
        # Set default styling based on style type
        if style == "primary":
            defaults = {
                "bg": Theme.ACCENT_PRIMARY,
                "fg": "white",
                "activebackground": Theme.ACCENT_HOVER,
                "activeforeground": "white",
            }
            self.hover_color = Theme.ACCENT_HOVER
            self.normal_color = Theme.ACCENT_PRIMARY
        elif style == "secondary":
            defaults = {
                "bg": Theme.BG_SECONDARY,
                "fg": Theme.TEXT_PRIMARY,
                "activebackground": Theme.BG_HOVER,
                "activeforeground": Theme.TEXT_PRIMARY,
            }
            self.hover_color = Theme.BG_HOVER
            self.normal_color = Theme.BG_SECONDARY
        else:  # ghost/back button
            defaults = {
                "bg": Theme.BG_PRIMARY,
                "fg": Theme.TEXT_SECONDARY,
                "activebackground": Theme.BG_SECONDARY,
                "activeforeground": Theme.TEXT_PRIMARY,
            }
            self.hover_color = Theme.BG_SECONDARY
            self.normal_color = Theme.BG_PRIMARY

        defaults.update(
            {
                "font": kwargs.get("font", Theme.FONT_BUTTON),
                "relief": "flat",
                "cursor": "hand2",
                "bd": 0,
                "padx": 16,
                "pady": 10,
            }
        )

        # Merge with provided kwargs
        defaults.update(kwargs)

        super().__init__(parent, **defaults)

        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.config(bg=self.hover_color)

    def _on_leave(self, e):
        self.config(bg=self.normal_color)


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes")
        self.root.geometry("520x650")
        self.root.configure(bg=Theme.BG_PRIMARY)

        # Make window non-resizable for consistent layout
        self.root.resizable(False, False)

        self.notes = self.load_notes()
        self.current_note_id = None

        # Main container with padding
        container = tk.Frame(root, bg=Theme.BG_PRIMARY)
        container.pack(fill="both", expand=True)

        # Content area
        self.main_frame = tk.Frame(container, bg=Theme.BG_PRIMARY)
        self.main_frame.pack(
            fill="both", expand=True, padx=Theme.PADDING_L, pady=Theme.PADDING_L
        )

        # Status bar at bottom
        self._create_status_bar(root)

        self.show_main_menu()

    def _create_status_bar(self, root):
        """Create modern status bar"""
        status_frame = tk.Frame(root, bg=Theme.BG_SECONDARY, height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            anchor="w",
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY,
            font=Theme.FONT_STATUS,
            padx=Theme.PADDING_M,
        )
        self.status_label.pack(side="left", fill="both", expand=True)

        # Status indicator dot
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            bg=Theme.BG_SECONDARY,
            fg=Theme.SUCCESS,
            font=("Segoe UI", 12),
            padx=Theme.PADDING_M,
        )
        self.status_indicator.pack(side="right")

    def set_status(self, message: str, status_type: str = "ready"):
        """Update status bar with message and color indicator"""
        color_map = {
            "ready": Theme.SUCCESS,
            "saving": Theme.WARNING,
            "error": Theme.ERROR,
            "success": Theme.SUCCESS,
        }

        self.status_var.set(message)
        self.status_indicator.config(fg=color_map.get(status_type, Theme.SUCCESS))

    def load_notes(self):
        """Load notes index from JSON file"""
        try:
            if NOTES_INDEX_FILE.exists():
                with open(NOTES_INDEX_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {e}")
            return []

    def save_notes_index(self):
        """Save notes index to JSON file"""
        try:
            with open(NOTES_INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(self.notes, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save notes index: {e}")
            self.set_status("Save failed", "error")
            return False

    def save_note_file(self, note_data):
        """Save individual note as a file on disk"""
        try:
            note_filename = f"{note_data['id']}.json"
            note_filepath = NOTES_DIR / note_filename

            print(f"Saving note to: {note_filepath}")

            with open(note_filepath, "w", encoding="utf-8") as f:
                json.dump(note_data, f, indent=2, ensure_ascii=False)

            print(f"Note saved successfully: {note_filename}")
            return True
        except Exception as e:
            print(f"Error saving note file: {e}")
            messagebox.showerror("Error", f"Failed to save note file: {e}")
            return False

    def load_note_file(self, note_id):
        """Load individual note from file"""
        try:
            note_filepath = NOTES_DIR / f"{note_id}.json"
            if note_filepath.exists():
                with open(note_filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load note: {e}")
            return None

    def show_main_menu(self):
        """Display main menu with options"""
        self.set_status("Ready", "ready")

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Header section
        header_frame = tk.Frame(self.main_frame, bg=Theme.BG_PRIMARY)
        header_frame.pack(fill="x", pady=(0, Theme.PADDING_L))

        title = tk.Label(
            header_frame,
            text="Notes",
            font=Theme.FONT_TITLE,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
        )
        title.pack()

        subtitle = tk.Label(
            header_frame,
            text="Capture your thoughts and ideas",
            font=Theme.FONT_SUBTITLE,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_SECONDARY,
        )
        subtitle.pack(pady=(Theme.PADDING_S, 0))

        # Divider
        divider = tk.Frame(self.main_frame, bg=Theme.BORDER, height=1)
        divider.pack(fill="x", pady=Theme.PADDING_L)

        # Button container
        button_container = tk.Frame(self.main_frame, bg=Theme.BG_PRIMARY)
        button_container.pack(fill="both", expand=True, pady=Theme.PADDING_M)

        # New Note button
        new_note_btn = ModernButton(
            button_container,
            text="✏️ Create New Note",
            style="primary",
            command=self.create_new_note,
            font=Theme.FONT_BUTTON_LARGE,
            width=24,
            height=2,
        )
        new_note_btn.pack(pady=Theme.PADDING_S, ipady=2)

        # Recent Notes (7 days)
        recent_btn = ModernButton(
            button_container,
            text="📅 Recent Notes (Last 7 Days)",
            style="secondary",
            command=lambda: self.show_notes_list(7),
            font=Theme.FONT_BUTTON_LARGE,
            width=24,
            height=2,
        )
        recent_btn.pack(pady=Theme.PADDING_S, ipady=2)

        # 30 Days Notes
        month_btn = ModernButton(
            button_container,
            text="📆 Notes (Last 30 Days)",
            style="secondary",
            command=lambda: self.show_notes_list(30),
            font=Theme.FONT_BUTTON_LARGE,
            width=24,
            height=2,
        )
        month_btn.pack(pady=Theme.PADDING_S, ipady=2)

        # All Notes
        all_btn = ModernButton(
            button_container,
            text="📚 All Notes",
            style="secondary",
            command=lambda: self.show_notes_list(None),
            font=Theme.FONT_BUTTON_LARGE,
            width=24,
            height=2,
        )
        all_btn.pack(pady=Theme.PADDING_S, ipady=2)

    def create_new_note(self):
        """Create a new note"""
        note_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_note_id = note_id
        self.show_note_editor(note_id, is_new=True)

    def show_notes_list(self, days_filter=None):
        """Display list of notes filtered by days"""
        self.set_status(f"Viewing notes", "ready")

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Header with back button
        header_frame = tk.Frame(self.main_frame, bg=Theme.BG_PRIMARY)
        header_frame.pack(fill="x", pady=(0, Theme.PADDING_L))

        back_btn = ModernButton(
            header_frame,
            text="← Back",
            style="ghost",
            command=self.show_main_menu,
            font=Theme.FONT_BUTTON,
        )
        back_btn.pack(side="left")

        # Title based on filter
        if days_filter == 7:
            title_text = "Recent Notes (Last 7 Days)"
        elif days_filter == 30:
            title_text = "Notes (Last 30 Days)"
        else:
            title_text = "All Notes"

        title = tk.Label(
            header_frame,
            text=title_text,
            font=Theme.FONT_CATEGORY,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
        )
        title.pack(side="left", padx=Theme.PADDING_M)

        # Divider
        divider = tk.Frame(self.main_frame, bg=Theme.BORDER, height=1)
        divider.pack(fill="x", pady=Theme.PADDING_M)

        # Filter notes
        filtered_notes = self.filter_notes_by_days(days_filter)

        # Notes container with scrollbar
        canvas_frame = tk.Frame(self.main_frame, bg=Theme.BG_PRIMARY)
        canvas_frame.pack(fill="both", expand=True, pady=Theme.PADDING_M)

        canvas = tk.Canvas(canvas_frame, bg=Theme.BG_PRIMARY, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.BG_PRIMARY)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not filtered_notes:
            empty_state = tk.Label(
                scrollable_frame,
                text="No notes found",
                font=Theme.FONT_SUBTITLE,
                bg=Theme.BG_PRIMARY,
                fg=Theme.TEXT_LIGHT,
            )
            empty_state.pack(pady=Theme.PADDING_XL)
            return

        # Display notes
        for note in filtered_notes:
            self.create_note_card(scrollable_frame, note)

    def filter_notes_by_days(self, days):
        """Filter notes by number of days"""
        if days is None:
            return sorted(self.notes, key=lambda x: x["created"], reverse=True)

        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = [
            note
            for note in self.notes
            if datetime.fromisoformat(note["created"]) >= cutoff_date
        ]
        return sorted(filtered, key=lambda x: x["created"], reverse=True)

    def create_note_card(self, parent, note):
        """Create a card widget for a note"""
        card_frame = tk.Frame(parent, bg=Theme.BG_SECONDARY)
        card_frame.pack(fill="x", pady=Theme.PADDING_S)

        # Note title and preview
        note_title = note.get("title", "Untitled Note")
        created_date = datetime.fromisoformat(note["created"]).strftime(
            "%b %d, %Y at %I:%M %p"
        )

        # Title label
        title_label = tk.Label(
            card_frame,
            text=note_title,
            font=Theme.FONT_NOTE_TITLE,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            anchor="w",
        )
        title_label.pack(fill="x", padx=Theme.PADDING_M, pady=(Theme.PADDING_M, 4))

        # Date label
        date_label = tk.Label(
            card_frame,
            text=created_date,
            font=Theme.FONT_STATUS,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_SECONDARY,
            anchor="w",
        )
        date_label.pack(fill="x", padx=Theme.PADDING_M, pady=(0, Theme.PADDING_S))

        # Preview of content
        content_preview = note.get("content", "")[:100]
        if len(note.get("content", "")) > 100:
            content_preview += "..."

        if content_preview:
            preview_label = tk.Label(
                card_frame,
                text=content_preview,
                font=Theme.FONT_NOTE,
                bg=Theme.BG_SECONDARY,
                fg=Theme.TEXT_SECONDARY,
                anchor="w",
                justify="left",
                wraplength=440,
            )
            preview_label.pack(
                fill="x", padx=Theme.PADDING_M, pady=(0, Theme.PADDING_S)
            )

        # Button frame
        btn_frame = tk.Frame(card_frame, bg=Theme.BG_SECONDARY)
        btn_frame.pack(fill="x", padx=Theme.PADDING_M, pady=(0, Theme.PADDING_M))

        # Open button
        open_btn = ModernButton(
            btn_frame,
            text="Open",
            style="primary",
            command=lambda n=note: self.show_note_editor(n["id"], is_new=False),
            font=Theme.FONT_BUTTON,
            padx=16,
            pady=6,
        )
        open_btn.pack(side="left", padx=(0, Theme.PADDING_S))

        # Delete button
        delete_btn = ModernButton(
            btn_frame,
            text="Delete",
            style="ghost",
            command=lambda n=note: self.delete_note(n["id"]),
            font=Theme.FONT_BUTTON,
            padx=16,
            pady=6,
        )
        delete_btn.pack(side="left")

    def show_note_editor(self, note_id, is_new=False):
        """Show note editor interface"""
        self.current_note_id = note_id

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Header with back button
        header_frame = tk.Frame(self.main_frame, bg=Theme.BG_PRIMARY)
        header_frame.pack(fill="x", pady=(0, Theme.PADDING_L))

        back_btn = ModernButton(
            header_frame,
            text="← Back",
            style="ghost",
            command=self.show_main_menu,
            font=Theme.FONT_BUTTON,
        )
        back_btn.pack(side="left")

        title_text = "New Note" if is_new else "Edit Note"
        title = tk.Label(
            header_frame,
            text=title_text,
            font=Theme.FONT_CATEGORY,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
        )
        title.pack(side="left", padx=Theme.PADDING_M)

        # Divider
        divider = tk.Frame(self.main_frame, bg=Theme.BORDER, height=1)
        divider.pack(fill="x", pady=Theme.PADDING_M)

        # Title input
        title_frame = tk.Frame(self.main_frame, bg=Theme.BG_PRIMARY)
        title_frame.pack(fill="x", pady=(0, Theme.PADDING_M))

        title_label = tk.Label(
            title_frame,
            text="Title:",
            font=Theme.FONT_BUTTON,
            bg=Theme.BG_PRIMARY,
            fg=Theme.TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        self.title_entry = tk.Entry(
            title_frame,
            font=Theme.FONT_NOTE,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            relief="flat",
            bd=0,
        )
        self.title_entry.pack(fill="x", ipady=8, pady=(4, 0))

        # Formatting toolbar
        toolbar_frame = tk.Frame(self.main_frame, bg=Theme.BG_SECONDARY)
        toolbar_frame.pack(fill="x", pady=(Theme.PADDING_M, Theme.PADDING_S))

        toolbar_label = tk.Label(
            toolbar_frame,
            text="Format:",
            font=Theme.FONT_BUTTON,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
        )
        toolbar_label.pack(side="left", padx=(Theme.PADDING_M, Theme.PADDING_S))

        # Format buttons
        bold_btn = ModernButton(
            toolbar_frame,
            text="B",
            style="ghost",
            command=lambda: self.apply_format("bold"),
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=4,
        )
        bold_btn.pack(side="left", padx=2)

        italic_btn = ModernButton(
            toolbar_frame,
            text="I",
            style="ghost",
            command=lambda: self.apply_format("italic"),
            font=("Segoe UI", 10, "italic"),
            padx=8,
            pady=4,
        )
        italic_btn.pack(side="left", padx=2)

        underline_btn = ModernButton(
            toolbar_frame,
            text="U",
            style="ghost",
            command=lambda: self.apply_format("underline"),
            font=("Segoe UI", 10, "underline"),
            padx=8,
            pady=4,
        )
        underline_btn.pack(side="left", padx=2)

        # Text editor
        editor_frame = tk.Frame(self.main_frame, bg=Theme.BG_PRIMARY)
        editor_frame.pack(fill="x", pady=(0, Theme.PADDING_M))

        self.text_editor = scrolledtext.ScrolledText(
            editor_frame,
            font=Theme.FONT_NOTE,
            bg=Theme.BG_SECONDARY,
            fg=Theme.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            wrap="word",
            padx=Theme.PADDING_M,
            pady=Theme.PADDING_M,
            height=12,
        )
        self.text_editor.pack(fill="x")

        # Configure text tags for formatting
        self.text_editor.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        self.text_editor.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        self.text_editor.tag_configure("underline", underline=True)

        # Load existing note if not new
        if not is_new:
            existing_note = self.load_note_file(note_id)
            if existing_note:
                self.title_entry.insert(0, existing_note.get("title", ""))
                self.text_editor.insert("1.0", existing_note.get("content", ""))
                self.apply_saved_formatting(existing_note.get("formatting", []))

        # Save button
        save_btn = ModernButton(
            self.main_frame,
            text="💾 Save Note",
            style="primary",
            command=lambda: self.save_current_note(is_new),
            font=Theme.FONT_BUTTON_LARGE,
            width=24,
        )
        save_btn.pack(pady=Theme.PADDING_M, ipady=2)

    def apply_format(self, format_type):
        """Apply formatting to selected text"""
        try:
            # Get selected text range
            start = self.text_editor.index("sel.first")
            end = self.text_editor.index("sel.last")

            # Toggle the tag
            current_tags = self.text_editor.tag_names(start)
            if format_type in current_tags:
                self.text_editor.tag_remove(format_type, start, end)
            else:
                self.text_editor.tag_add(format_type, start, end)

        except tk.TclError:
            # No text selected
            messagebox.showinfo("Format", "Please select text to format")

    def apply_saved_formatting(self, formatting_list):
        """Apply saved formatting to text editor"""
        for fmt in formatting_list:
            start = fmt["start"]
            end = fmt["end"]
            tag = fmt["tag"]
            self.text_editor.tag_add(tag, start, end)

    def get_current_formatting(self):
        """Get all formatting from text editor"""
        formatting = []
        for tag in ["bold", "italic", "underline"]:
            ranges = self.text_editor.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                formatting.append(
                    {"start": str(ranges[i]), "end": str(ranges[i + 1]), "tag": tag}
                )
        return formatting

    def save_current_note(self, is_new):
        """Save the current note to disk"""
        self.set_status("Saving note...", "saving")

        title = self.title_entry.get().strip()
        content = self.text_editor.get("1.0", "end-1c")
        formatting = self.get_current_formatting()

        if not title:
            title = "Untitled Note"

        if not content.strip():
            messagebox.showwarning("Empty Note", "Note content cannot be empty")
            self.set_status("Save cancelled", "error")
            return

        note_data = {
            "id": self.current_note_id,
            "title": title,
            "content": content,
            "formatting": formatting,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
        }

        if is_new:
            # Save the note file
            if self.save_note_file(note_data):
                # Add to index
                index_entry = {
                    "id": self.current_note_id,
                    "title": title,
                    "created": note_data["created"],
                    "modified": note_data["modified"],
                }
                self.notes.append(index_entry)

                if self.save_notes_index():
                    self.set_status("Note saved", "success")
                    messagebox.showinfo("Success", "Note saved successfully!")
                    self.show_main_menu()
        else:
            # Load existing note to preserve creation date
            existing_note = self.load_note_file(self.current_note_id)
            if existing_note:
                note_data["created"] = existing_note["created"]

            # Save the note file
            if self.save_note_file(note_data):
                # Update index
                for i, note in enumerate(self.notes):
                    if note["id"] == self.current_note_id:
                        self.notes[i] = {
                            "id": self.current_note_id,
                            "title": title,
                            "created": note_data["created"],
                            "modified": note_data["modified"],
                        }
                        break

                if self.save_notes_index():
                    self.set_status("Note updated", "success")
                    messagebox.showinfo("Success", "Note updated successfully!")
                    self.show_main_menu()

    def delete_note(self, note_id):
        """Delete a note file and remove from index"""
        if messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this note?"
        ):
            try:
                # Delete the note file
                note_filepath = NOTES_DIR / f"{note_id}.json"
                if note_filepath.exists():
                    note_filepath.unlink()

                # Remove from index
                self.notes = [note for note in self.notes if note["id"] != note_id]

                if self.save_notes_index():
                    self.set_status("Note deleted", "success")
                    messagebox.showinfo("Deleted", "Note deleted successfully!")
                    self.show_main_menu()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete note: {e}")
                self.set_status("Delete failed", "error")


def main():
    root = tk.Tk()
    NotesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
