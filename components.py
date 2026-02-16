"""
Reusable UI components for the Notes application.
"""

import tkinter as tk
from theme import Theme


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


class StatusBar(tk.Frame):
    """Modern status bar with status indicator"""

    def __init__(self, parent):
        super().__init__(parent, bg=Theme.BG_SECONDARY, height=30)
        self.pack(side="bottom", fill="x")
        self.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            self,
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
            self,
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
