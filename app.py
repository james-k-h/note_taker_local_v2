"""
Notes Application - Main application class
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from dotenv import load_dotenv
import json
import sys
from pathlib import Path
import threading
from datetime import datetime

from theme import Theme
from components import StatusBar
from storage import NoteStorage
from views import MainMenuView, NotesListView, NoteEditorView


BASE_DIR = Path(__file__).resolve().parent


class NotesApp:
    """Main Notes Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Notes")
        self.root.geometry("520x650")
        self.root.configure(bg=Theme.BG_PRIMARY)

        # Make window non-resizable for consistent layout
        self.root.resizable(False, False)

        # Initialize storage
        self.storage = NoteStorage(BASE_DIR)
        self.notes = self.storage.load_notes_index()
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
        self.status_bar = StatusBar(root)

        # Initialize views
        self._init_views()

        # Show main menu
        self.show_main_menu()

    def _init_views(self):
        """Initialize all view objects with callbacks"""
        self.main_menu_view = MainMenuView(
            self.main_frame,
            callbacks={
                "create_new_note": self.create_new_note,
                "show_notes_list": self.show_notes_list,
            },
        )

        self.notes_list_view = NotesListView(
            self.main_frame,
            callbacks={
                "show_main_menu": self.show_main_menu,
                "open_note": self.open_note,
                "delete_note": self.delete_note,
            },
        )

        self.note_editor_view = NoteEditorView(
            self.main_frame,
            callbacks={
                "show_main_menu": self.show_main_menu,
                "save_note": self.save_current_note,
                "apply_format": self.apply_format,
            },
        )

    def show_main_menu(self):
        """Display main menu"""
        self.status_bar.set_status("Ready", "ready")
        self.main_menu_view.render()

    def create_new_note(self):
        """Create a new note"""
        note_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_note_id = note_id
        self.note_editor_view.render(note_id, is_new=True)

    def show_notes_list(self, days_filter=None):
        """Display list of notes filtered by days"""
        self.status_bar.set_status("Viewing notes", "ready")
        filtered_notes = self.storage.filter_notes_by_days(self.notes, days_filter)
        self.notes_list_view.render(filtered_notes, days_filter)

    def open_note(self, note_id):
        """Open an existing note for editing"""
        self.current_note_id = note_id
        existing_note = self.storage.load_note_file(note_id)
        self.note_editor_view.render(note_id, is_new=False, existing_note=existing_note)

    def apply_format(self, format_type):
        """Apply formatting to selected text in editor"""
        self.note_editor_view.apply_format_to_selection(format_type)

    def save_current_note(self, is_new):
        """Save the current note to disk"""
        print(
            f"save_current_note called: is_new={is_new}, note_id={self.current_note_id}"
        )
        self.status_bar.set_status("Saving note...", "saving")

        title = self.note_editor_view.get_title()
        content = self.note_editor_view.get_content()
        formatting = self.note_editor_view.get_formatting()

        print(f"Title: {title}, Content length: {len(content)}")

        if not title:
            title = "Untitled Note"

        if not content.strip():
            messagebox.showwarning("Empty Note", "Note content cannot be empty")
            self.status_bar.set_status("Save cancelled", "error")
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
            print("Creating new note...")
            # Save the note file
            if self.storage.save_note_file(note_data):
                # Add to index
                index_entry = {
                    "id": self.current_note_id,
                    "title": title,
                    "created": note_data["created"],
                    "modified": note_data["modified"],
                }
                self.notes.append(index_entry)

                if self.storage.save_notes_index(self.notes):
                    self.status_bar.set_status("Note saved", "success")
                    messagebox.showinfo("Success", "Note saved successfully!")
                    self.show_main_menu()
        else:
            # Load existing note to preserve creation date
            existing_note = self.storage.load_note_file(self.current_note_id)
            if existing_note:
                note_data["created"] = existing_note["created"]

            # Save the note file
            if self.storage.save_note_file(note_data):
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

                if self.storage.save_notes_index(self.notes):
                    self.status_bar.set_status("Note updated", "success")
                    messagebox.showinfo("Success", "Note updated successfully!")
                    self.show_main_menu()

    def delete_note(self, note_id):
        """Delete a note file and remove from index"""
        if messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this note?"
        ):
            # Delete the note file
            if self.storage.delete_note_file(note_id):
                # Remove from index
                self.notes = [note for note in self.notes if note["id"] != note_id]

                if self.storage.save_notes_index(self.notes):
                    self.status_bar.set_status("Note deleted", "success")
                    messagebox.showinfo("Deleted", "Note deleted successfully!")
                    self.show_main_menu()


def main():
    root = tk.Tk()
    NotesApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
