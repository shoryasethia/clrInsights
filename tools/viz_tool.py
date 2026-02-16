import io
import base64
from typing import Any, Optional
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def _smart_ylim(y_values):
    """Calculate smart Y-axis limits that show differences clearly."""
    y_min = min(y_values)
    y_max = max(y_values)
    y_range = y_max - y_min
    
    # If all values are very close (range < 10% of max), zoom in
    if y_range > 0 and y_max > 0 and y_range / y_max < 0.15:
        padding = y_range * 0.3 if y_range > 0 else y_max * 0.05
        return max(0, y_min - padding * 3), y_max + padding
    
    # Default: start from 0
    return 0, y_max * 1.1


def _style_chart(fig, ax):
    """Apply consistent professional styling to charts."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#555')
    ax.spines['bottom'].set_color('#555')
    ax.tick_params(colors='#555', labelsize=7)
    ax.title.set_fontsize(9)
    ax.title.set_fontweight('bold')
    ax.title.set_color('#333')
    ax.xaxis.label.set_color('#555')
    ax.yaxis.label.set_color('#555')
    ax.xaxis.label.set_fontsize(7)
    ax.yaxis.label.set_fontsize(7)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')


class VisualizationTool:
    """Tool for creating data visualizations."""
    
    name = "create_visualization"
    description = """Create charts and visualizations from data."""
    
    @staticmethod
    def create_bar_chart(
        data: list[dict[str, Any]],
        x_col: str,
        y_col: str,
        title: str = "",
        color: str = "#4285F4"
    ) -> str:
        """Create bar chart with smart Y-axis scaling."""
        fig, ax = plt.subplots(figsize=(4, 2.5))
        
        x_values = [str(row[x_col]) for row in data]
        y_values = [float(row[y_col]) for row in data]
        
        bars = ax.bar(x_values, y_values, color=color, width=0.6, edgecolor='white', linewidth=0.5)
        
        # Add value labels on top of bars
        for bar, val in zip(bars, y_values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f'{val:,.2f}' if val != int(val) else f'{int(val):,}',
                    ha='center', va='bottom', fontsize=6, color='#333', fontweight='bold')
        
        ax.set_xlabel(x_col.replace('_', ' ').title())
        ax.set_ylabel(y_col.replace('_', ' ').title())
        ax.set_title(title if title else f"{y_col} by {x_col}")
        
        # Smart Y-axis scaling
        y_bottom, y_top = _smart_ylim(y_values)
        ax.set_ylim(y_bottom, y_top)
        
        plt.xticks(rotation=30, ha='right', fontsize=7)
        ax.grid(axis='y', alpha=0.2, linestyle='--')
        _style_chart(fig, ax)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def create_line_chart(
        data: list[dict[str, Any]],
        x_col: str,
        y_col: str,
        title: str = "",
        color: str = "#0F9D58"
    ) -> str:
        """Create line chart with smart Y-axis scaling."""
        fig, ax = plt.subplots(figsize=(4, 2.5))
        
        x_values = [str(row[x_col]) for row in data]
        y_values = [float(row[y_col]) for row in data]
        
        ax.plot(x_values, y_values, marker='o', color=color, linewidth=1.5, markersize=3)
        ax.fill_between(range(len(x_values)), y_values, alpha=0.1, color=color)
        
        ax.set_xlabel(x_col.replace('_', ' ').title())
        ax.set_ylabel(y_col.replace('_', ' ').title())
        ax.set_title(title if title else f"{y_col} over {x_col}")
        
        y_bottom, y_top = _smart_ylim(y_values)
        ax.set_ylim(y_bottom, y_top)
        
        plt.xticks(rotation=30, ha='right', fontsize=7)
        ax.grid(True, alpha=0.2, linestyle='--')
        _style_chart(fig, ax)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def create_pie_chart(
        data: list[dict[str, Any]],
        label_col: str,
        value_col: str,
        title: str = ""
    ) -> str:
        """Create pie chart."""
        fig, ax = plt.subplots(figsize=(4, 3))
        
        labels = [str(row[label_col]) for row in data]
        values = [float(row[value_col]) for row in data]
        
        colors = ['#4285F4', '#EA4335', '#FBBC04', '#34A853', '#FF6D01', '#46BDC6', '#7B61FF', '#E8710A']
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, 
               colors=colors[:len(values)], textprops={'fontsize': 7})
        ax.set_title(title if title else f"{value_col} distribution")
        _style_chart(fig, ax)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def create_dual_axis_chart(
        data: list[dict[str, Any]],
        x_col: str,
        y_col: str,
        y2_col: str,
        title: str = "",
        bar_color: str = "#4285F4",
        line_color: str = "#EA4335"
    ) -> str:
        """Create dual-axis chart: bars on left axis, line on right axis."""
        fig, ax1 = plt.subplots(figsize=(5, 3))
        
        x_values = [str(row[x_col]) for row in data]
        y1_values = [float(row[y_col]) for row in data]
        y2_values = [float(row[y2_col]) for row in data]
        x_pos = range(len(x_values))
        
        # Bars on left axis
        bars = ax1.bar(x_pos, y1_values, color=bar_color, width=0.6, alpha=0.8, label=y_col.replace('_', ' ').title())
        ax1.set_ylabel(y_col.replace('_', ' ').title(), fontsize=7, color=bar_color)
        ax1.tick_params(axis='y', labelcolor=bar_color, labelsize=7)
        y1_bottom, y1_top = _smart_ylim(y1_values)
        ax1.set_ylim(y1_bottom, y1_top)
        
        # Line on right axis
        ax2 = ax1.twinx()
        ax2.plot(x_pos, y2_values, color=line_color, marker='o', linewidth=1.5, markersize=4, label=y2_col.replace('_', ' ').title(), zorder=5)
        ax2.set_ylabel(y2_col.replace('_', ' ').title(), fontsize=7, color=line_color)
        ax2.tick_params(axis='y', labelcolor=line_color, labelsize=7)
        y2_bottom, y2_top = _smart_ylim(y2_values)
        ax2.set_ylim(y2_bottom, y2_top)
        ax2.spines['right'].set_color(line_color)
        ax2.spines['right'].set_visible(True)
        
        # Value labels on bars
        for bar, val in zip(bars, y1_values):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f'{int(val):,}' if val == int(val) else f'{val:,.1f}',
                    ha='center', va='bottom', fontsize=5, color=bar_color, fontweight='bold')
        
        # Value labels on line points
        for x, val in zip(x_pos, y2_values):
            ax2.text(x, val, f'{val:.1f}%' if val < 100 else f'{int(val):,}',
                    ha='center', va='bottom', fontsize=5, color=line_color, fontweight='bold')
        
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(x_values, rotation=30, ha='right', fontsize=6)
        ax1.set_title(title, fontsize=9, fontweight='bold', color='#333')
        ax1.grid(axis='y', alpha=0.15, linestyle='--')
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=6, framealpha=0.8)
        
        _style_chart(fig, ax1)
        ax2.spines['top'].set_visible(False)
        fig.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    def __call__(
        self,
        data: list[dict[str, Any]],
        chart_type: str,
        x_col: str,
        y_col: Optional[str] = None,
        title: str = "",
        **kwargs
    ) -> dict[str, Any]:
        """
        Create visualization from data.
        
        Args:
            data: List of dictionaries (query results)
            chart_type: Type of chart (bar, line, pie)
            x_col: Column for x-axis or labels
            y_col: Column for y-axis or values
            title: Chart title
            **kwargs: Additional chart parameters
            
        Returns:
            Dictionary with base64 image and metadata
        """
        if not data:
            return {
                'success': False,
                'error': 'No data provided for visualization',
                'image': None
            }
        
        try:
            if chart_type == 'bar':
                image_base64 = self.create_bar_chart(data, x_col, y_col, title)
            elif chart_type == 'line':
                image_base64 = self.create_line_chart(data, x_col, y_col, title)
            elif chart_type == 'pie':
                image_base64 = self.create_pie_chart(data, x_col, y_col, title)
            elif chart_type == 'dual_axis':
                y2_col = kwargs.get('y2_col')
                if not y2_col:
                    # Fallback: use 3rd column if available
                    columns = list(data[0].keys()) if data else []
                    y2_col = columns[2] if len(columns) > 2 else y_col
                image_base64 = self.create_dual_axis_chart(data, x_col, y_col, y2_col, title)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported chart type: {chart_type}',
                    'image': None
                }
            
            return {
                'success': True,
                'error': None,
                'image': image_base64,
                'chart_type': chart_type,
                'title': title
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Visualization error: {str(e)}',
                'image': None
            }


viz_tool = VisualizationTool()
