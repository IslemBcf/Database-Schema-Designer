from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from math import atan2, cos, sin, pi


class CanvasWidget(QFrame):
    """
    Enhanced canvas with better relationship visualization.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._relationships = []  # List of (table_a_name, table_b_name, rel_type, widget_a, widget_b)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
    
    def add_relationship(self, table_a_name: str, table_b_name: str, rel_type: str, 
                        widget_a, widget_b):
        """Add a relationship to be drawn."""
        # Remove existing relationship between these tables if any (bidirectional)
        self._relationships = [
            r for r in self._relationships 
            if not ((r[0] == table_a_name and r[1] == table_b_name) or
                    (r[0] == table_b_name and r[1] == table_a_name))
        ]
        self._relationships.append((table_a_name, table_b_name, rel_type, widget_a, widget_b))
        self.update()
    
    def remove_relationship(self, table_a_name: str, table_b_name: str):
        """Remove a relationship."""
        self._relationships = [
            r for r in self._relationships 
            if not ((r[0] == table_a_name and r[1] == table_b_name) or
                    (r[0] == table_b_name and r[1] == table_a_name))
        ]
        self.update()
    
    def clear_relationships(self):
        """Clear all relationships."""
        self._relationships = []
        self.update()
    
    def update_relationship_widgets(self, table_widgets: dict):
        """Update widget references for relationships."""
        updated = []
        for rel in self._relationships:
            table_a_name, table_b_name, rel_type, _, _ = rel
            widget_a = table_widgets.get(table_a_name)
            widget_b = table_widgets.get(table_b_name)
            if widget_a and widget_b:
                updated.append((table_a_name, table_b_name, rel_type, widget_a, widget_b))
        self._relationships = updated
        self.update()
    
    def paintEvent(self, event):
        """Draw relationship lines between table widgets with enhanced visuals."""
        super().paintEvent(event)
        
        if not self._relationships:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw each relationship line
        for table_a_name, table_b_name, rel_type, widget_a, widget_b in self._relationships:
            if not widget_a or not widget_b or not widget_a.isVisible() or not widget_b.isVisible():
                continue
            
            # Get rectangles
            a_rect = widget_a.geometry()
            b_rect = widget_b.geometry()
            
            # Choose color based on relationship type - dark blue night theme
            if rel_type == "1-N":
                color = QColor("#3b82f6")  # Bright blue for 1-N
                line_width = 3
            else:  # N-N
                color = QColor("#8b5cf6")  # Purple for N-N
                line_width = 3
            
            # Calculate best connection points
            start_point, end_point = self._calculate_connection_points(a_rect, b_rect, rel_type)
            
            # Draw shadow for depth
            shadow_pen = QPen(QColor(0, 0, 0, 30), line_width + 2, Qt.SolidLine)
            painter.setPen(shadow_pen)
            painter.drawLine(start_point.x() + 2, start_point.y() + 2, 
                           end_point.x() + 2, end_point.y() + 2)
            
            # Draw the main line
            pen = QPen(color, line_width, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(start_point, end_point)
            
            # Draw relationship indicators
            if rel_type == "1-N":
                self._draw_one_to_many_indicator(painter, start_point, end_point, color)
            else:  # N-N
                self._draw_many_to_many_indicator(painter, start_point, end_point, color)
    
    def _calculate_connection_points(self, rect_a, rect_b, rel_type):
        """Calculate optimal connection points between two rectangles."""
        # Calculate centers
        center_a = rect_a.center()
        center_b = rect_b.center()
        
        # Determine which sides to connect based on relative positions
        dx = center_b.x() - center_a.x()
        dy = center_b.y() - center_a.y()
        
        # For 1-N, prefer horizontal connections
        if rel_type == "1-N":
            if abs(dx) > abs(dy):
                # Horizontal connection
                if dx > 0:  # B is to the right of A
                    start = QPoint(rect_a.right(), center_a.y())
                    end = QPoint(rect_b.left(), center_b.y())
                else:  # B is to the left of A
                    start = QPoint(rect_a.left(), center_a.y())
                    end = QPoint(rect_b.right(), center_b.y())
            else:
                # Vertical connection
                if dy > 0:  # B is below A
                    start = QPoint(center_a.x(), rect_a.bottom())
                    end = QPoint(center_b.x(), rect_b.top())
                else:  # B is above A
                    start = QPoint(center_a.x(), rect_a.top())
                    end = QPoint(center_b.x(), rect_b.bottom())
        else:  # N-N prefer vertical
            if abs(dy) > abs(dx):
                # Vertical connection
                if dy > 0:
                    start = QPoint(center_a.x(), rect_a.bottom())
                    end = QPoint(center_b.x(), rect_b.top())
                else:
                    start = QPoint(center_a.x(), rect_a.top())
                    end = QPoint(center_b.x(), rect_b.bottom())
            else:
                # Horizontal connection
                if dx > 0:
                    start = QPoint(rect_a.right(), center_a.y())
                    end = QPoint(rect_b.left(), center_b.y())
                else:
                    start = QPoint(rect_a.left(), center_a.y())
                    end = QPoint(rect_b.right(), center_b.y())
        
        return start, end
    
    def _draw_one_to_many_indicator(self, painter, start, end, color):
        """Draw arrow and notation for 1-N relationship."""
        # Draw '1' near start
        painter.setPen(QPen(color, 1))
        painter.setFont(painter.font())
        font = painter.font()
        font.setPixelSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        # Calculate position for '1'
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = (dx*dx + dy*dy) ** 0.5
        if length > 0:
            offset = 15
            one_x = start.x() + int(offset * dx / length)
            one_y = start.y() + int(offset * dy / length)
            painter.drawText(one_x - 10, one_y - 5, 20, 20, Qt.AlignCenter, "1")
        
        # Draw arrow head at end (many side)
        self._draw_arrow_head(painter, start, end, color)
        
        # Draw 'N' or '*' near end
        if length > 0:
            offset = 25
            n_x = end.x() - int(offset * dx / length)
            n_y = end.y() - int(offset * dy / length)
            painter.drawText(n_x - 10, n_y - 5, 20, 20, Qt.AlignCenter, "N")
    
    def _draw_many_to_many_indicator(self, painter, start, end, color):
        """Draw indicators for N-N relationship."""
        painter.setPen(QPen(color, 1))
        font = painter.font()
        font.setPixelSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = (dx*dx + dy*dy) ** 0.5
        
        if length > 0:
            # Draw 'N' near start
            offset = 15
            n1_x = start.x() + int(offset * dx / length)
            n1_y = start.y() + int(offset * dy / length)
            painter.drawText(n1_x - 10, n1_y - 5, 20, 20, Qt.AlignCenter, "N")
            
            # Draw 'N' near end
            n2_x = end.x() - int(offset * dx / length)
            n2_y = end.y() - int(offset * dy / length)
            painter.drawText(n2_x - 10, n2_y - 5, 20, 20, Qt.AlignCenter, "N")
        
        # Draw double-headed arrow
        self._draw_arrow_head(painter, start, end, color)
        self._draw_arrow_head(painter, end, start, color)
    
    def _draw_arrow_head(self, painter, start, end, color):
        """Draw an arrow head at the end point."""
        # Calculate direction
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = (dx*dx + dy*dy) ** 0.5
        
        if length == 0:
            return
        
        # Normalize
        dx /= length
        dy /= length
        
        # Arrow parameters
        arrow_size = 12
        arrow_angle = 25 * pi / 180  # 25 degrees in radians
        
        # Calculate arrow points
        angle = atan2(dy, dx)
        
        p1_x = end.x() - arrow_size * cos(angle - arrow_angle)
        p1_y = end.y() - arrow_size * sin(angle - arrow_angle)
        
        p2_x = end.x() - arrow_size * cos(angle + arrow_angle)
        p2_y = end.y() - arrow_size * sin(angle + arrow_angle)
        
        # Draw filled arrow head
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 2))
        
        path = QPainterPath()
        path.moveTo(end.x(), end.y())
        path.lineTo(p1_x, p1_y)
        path.lineTo(p2_x, p2_y)
        path.closeSubpath()
        
        painter.drawPath(path)
        painter.fillPath(path, QBrush(color))