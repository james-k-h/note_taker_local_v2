"""
View components for different screens in the Notes application.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
from theme import Theme
from components import ModernButton


class MainMenuView:
    """Main menu view with navigation options"""

    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks

    def render(self):
        """Render the main menu"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Header section
        header_frame = tk.Frame(self.parent, bg=Theme.BG_PRIMARY)
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
        divider = tk.Frame(self.parent, bg=Theme.BORDER, height=1)
        divider.pack(fill="x", pady=Theme.PADDING_L)

        # Button container
        button_container = tk.Frame(self.parent, bg=Theme.BG_PRIMARY)
        button_container.pack(fill="both", expand=True, pady=Theme.PADDING_M)

        # New Note button
        new_note_btn = ModernButton(
            button_container,
            text="✏️ Create New Note",
            style="primary",
            command=self.callbacks["create_new_note"],
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
            command=lambda: self.callbacks["show_notes_list"](7),
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
            command=lambda: self.callbacks["show_notes_list"](30),
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
            command=lambda: self.callbacks["show_notes_list"](None),
            font=Theme.FONT_BUTTON_LARGE,
            width=24,
            height=2,
        )
        all_btn.pack(pady=Theme.PADDING_S, ipady=2)


class NotesListView:
    """View for displaying a list of notes"""

    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks

    def render(self, notes, days_filter=None):
        """Render the notes list"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Header with back button
        header_frame = tk.Frame(self.parent, bg=Theme.BG_PRIMARY)
        header_frame.pack(fill="x", pady=(0, Theme.PADDING_L))

        back_btn = ModernButton(
            header_frame,
            text="← Back",
            style="ghost",
            command=self.callbacks["show_main_menu"],
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
        divider = tk.Frame(self.parent, bg=Theme.BORDER, height=1)
        divider.pack(fill="x", pady=Theme.PADDING_M)

        # Notes container with scrollbar
        canvas_frame = tk.Frame(self.parent, bg=Theme.BG_PRIMARY)
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

        if not notes:
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
        for note in notes:
            self._create_note_card(scrollable_frame, note)

    def _create_note_card(self, parent, note):
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
            command=lambda n=note: self.callbacks["open_note"](n["id"]),
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
            command=lambda n=note: self.callbacks["delete_note"](n["id"]),
            font=Theme.FONT_BUTTON,
            padx=16,
            pady=6,
        )
        delete_btn.pack(side="left")


class NoteEditorView:
    """View for creating/editing notes"""

    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.title_entry = None
        self.text_editor = None

    def render(self, note_id, is_new=False, existing_note=None):
        """Render the note editor"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()

        # Header with back button
        header_frame = tk.Frame(self.parent, bg=Theme.BG_PRIMARY)
        header_frame.pack(fill="x", pady=(0, Theme.PADDING_L))

        back_btn = ModernButton(
            header_frame,
            text="← Back",
            style="ghost",
            command=self.callbacks["show_main_menu"],
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
        divider = tk.Frame(self.parent, bg=Theme.BORDER, height=1)
        divider.pack(fill="x", pady=Theme.PADDING_M)

        # Title input
        title_frame = tk.Frame(self.parent, bg=Theme.BG_PRIMARY)
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
        toolbar_frame = tk.Frame(self.parent, bg=Theme.BG_SECONDARY)
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
            command=lambda: self.callbacks["apply_format"]("bold"),
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=4,
        )
        bold_btn.pack(side="left", padx=2)

        italic_btn = ModernButton(
            toolbar_frame,
            text="I",
            style="ghost",
            command=lambda: self.callbacks["apply_format"]("italic"),
            font=("Segoe UI", 10, "italic"),
            padx=8,
            pady=4,
        )
        italic_btn.pack(side="left", padx=2)

        underline_btn = ModernButton(
            toolbar_frame,
            text="U",
            style="ghost",
            command=lambda: self.callbacks["apply_format"]("underline"),
            font=("Segoe UI", 10, "underline"),
            padx=8,
            pady=4,
        )
        underline_btn.pack(side="left", padx=2)

        # Text editor
        editor_frame = tk.Frame(self.parent, bg=Theme.BG_PRIMARY)
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
        self.text_editor.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.text_editor.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        self.text_editor.tag_configure("underline", underline=True)

        # Load existing note if not new
        if not is_new and existing_note:
            self.title_entry.insert(0, existing_note.get("title", ""))
            self.text_editor.insert("1.0", existing_note.get("content", ""))
            self._apply_saved_formatting(existing_note.get("formatting", []))

        # Save button
        save_btn = ModernButton(
            self.parent,
            text="💾 Save Note",
            style="primary",
            command=lambda: self.callbacks["save_note"](is_new),
            font=Theme.FONT_BUTTON_LARGE,
            width=24,
        )
        save_btn.pack(pady=Theme.PADDING_M, ipady=2)

    def _apply_saved_formatting(self, formatting_list):
        """Apply saved formatting to text editor"""
        for fmt in formatting_list:
            start = fmt["start"]
            end = fmt["end"]
            tag = fmt["tag"]
            self.text_editor.tag_add(tag, start, end)

    def get_title(self):
        """Get the current title"""
        return self.title_entry.get().strip() if self.title_entry else ""

    def get_content(self):
        """Get the current content"""
        return self.text_editor.get("1.0", "end-1c") if self.text_editor else ""

    def get_formatting(self):
        """Get all formatting from text editor"""
        if not self.text_editor:
            return []

        formatting = []
        for tag in ["bold", "italic", "underline"]:
            ranges = self.text_editor.tag_ranges(tag)
            for i in range(0, len(ranges), 2):
                formatting.append(
                    {"start": str(ranges[i]), "end": str(ranges[i + 1]), "tag": tag}
                )
        return formatting

    def apply_format_to_selection(self, format_type):
        """Apply formatting to selected text"""
        if not self.text_editor:
            return

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
