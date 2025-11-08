# -*- coding: utf-8 -*-
"""
Pagination Helper
Eliminates duplicate pagination logic across UI tabs
"""


class PaginationHelper:
    """
    Reusable pagination logic
    Replaces duplicate pagination code in vehiculos_tab, funcionarios_tab, asignaciones_tab
    """

    def __init__(self, items_per_page: int = 15):
        """
        Initialize pagination helper

        Args:
            items_per_page: Number of items to display per page
        """
        self.items_per_page = items_per_page
        self.current_page = 1
        self.total_items = 0

    def set_total_items(self, total: int):
        """
        Set total number of items

        Args:
            total: Total number of items
        """
        self.total_items = max(0, total)

        # Adjust current page if it exceeds total pages
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        if self.items_per_page <= 0 or self.total_items <= 0:
            return 1
        return (self.total_items + self.items_per_page - 1) // self.items_per_page

    @property
    def start_index(self) -> int:
        """Get starting index for current page (0-based)"""
        return (self.current_page - 1) * self.items_per_page

    @property
    def end_index(self) -> int:
        """Get ending index for current page (exclusive)"""
        return min(self.start_index + self.items_per_page, self.total_items)

    def get_page_items(self, items: list) -> list:
        """
        Return items for current page

        Args:
            items: Full list of items

        Returns:
            Slice of items for current page
        """
        return items[self.start_index:self.end_index]

    def next_page(self) -> bool:
        """
        Move to next page

        Returns:
            True if page changed, False if already on last page
        """
        if self.current_page < self.total_pages:
            self.current_page += 1
            return True
        return False

    def previous_page(self) -> bool:
        """
        Move to previous page

        Returns:
            True if page changed, False if already on first page
        """
        if self.current_page > 1:
            self.current_page -= 1
            return True
        return False

    def first_page(self) -> bool:
        """
        Move to first page

        Returns:
            True if page changed, False if already on first page
        """
        if self.current_page != 1:
            self.current_page = 1
            return True
        return False

    def last_page(self) -> bool:
        """
        Move to last page

        Returns:
            True if page changed, False if already on last page
        """
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            return True
        return False

    def get_page_info(self) -> str:
        """
        Get formatted page information string

        Returns:
            Formatted string like "Pagina 2 de 5 (30 elementos)"
        """
        if self.total_items == 0:
            return "Pagina 0 de 0 (0 elementos)"

        return (
            f"Pagina {self.current_page} de {self.total_pages} "
            f"({self.total_items} elemento{'s' if self.total_items != 1 else ''})"
        )

    def get_button_states(self) -> dict:
        """
        Get enabled states for pagination buttons

        Returns:
            Dict with button states: {'first': bool, 'prev': bool, 'next': bool, 'last': bool}
        """
        return {
            'first': self.current_page > 1,
            'prev': self.current_page > 1,
            'next': self.current_page < self.total_pages,
            'last': self.current_page < self.total_pages,
        }

    def reset(self):
        """Reset pagination to first page"""
        self.current_page = 1
