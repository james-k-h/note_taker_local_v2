"""
Note storage and data management.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from tkinter import messagebox


class NoteStorage:
    """Handles all note storage operations"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.notes_dir = self.base_dir / "notes"
        self.notes_index_file = self.notes_dir / "notes_index.json"

        # Create notes directory if it doesn't exist
        try:
            self.notes_dir.mkdir(exist_ok=True)
            print(f"Notes directory: {self.notes_dir}")
        except Exception as e:
            print(f"Error creating notes directory: {e}")

    def load_notes_index(self):
        """Load notes index from JSON file"""
        try:
            if self.notes_index_file.exists():
                with open(self.notes_index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {e}")
            return []

    def save_notes_index(self, notes):
        """Save notes index to JSON file"""
        try:
            with open(self.notes_index_file, "w", encoding="utf-8") as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save notes index: {e}")
            return False

    def save_note_file(self, note_data):
        """Save individual note as a file on disk"""
        try:
            note_filename = f"{note_data['id']}.json"
            note_filepath = self.notes_dir / note_filename

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
            note_filepath = self.notes_dir / f"{note_id}.json"
            if note_filepath.exists():
                with open(note_filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load note: {e}")
            return None

    def delete_note_file(self, note_id):
        """Delete a note file from disk"""
        try:
            note_filepath = self.notes_dir / f"{note_id}.json"
            if note_filepath.exists():
                note_filepath.unlink()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete note file: {e}")
            return False

    def filter_notes_by_days(self, notes, days):
        """Filter notes by number of days"""
        if days is None:
            return sorted(notes, key=lambda x: x["created"], reverse=True)

        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = [
            note
            for note in notes
            if datetime.fromisoformat(note["created"]) >= cutoff_date
        ]
        return sorted(filtered, key=lambda x: x["created"], reverse=True)
