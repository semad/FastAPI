#!/usr/bin/env python3
"""
Entity Relationship Diagram Generator for FastAPI Models

This script generates ERDs from SQLAlchemy models in the FastAPI application.
It can output both visual diagrams (using matplotlib) and text representations.
"""

import os
import sys
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import argparse

# Add the src directory to the path so we can import the models
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    FancyBboxPatch = None
    print("Warning: matplotlib not available. Visual ERD generation disabled.")

from app.models.book import Book
from app.models.user import User
from app.models.post import Post
from app.models.tier import Tier
from app.models.rate_limit import RateLimit


class ERDGenerator:
    """Generates Entity Relationship Diagrams from SQLAlchemy models."""
    
    def __init__(self):
        self.models = {
            'User': User,
            'Book': Book,
            'Post': Post,
            'Tier': Tier,
            'RateLimit': RateLimit
        }
        self.relationships = []
        self.analyze_relationships()
    
    def analyze_relationships(self):
        """Analyze foreign key relationships between models."""
        for model_name, model_class in self.models.items():
            for column_name, column in model_class.__table__.columns.items():
                if hasattr(column, 'foreign_keys') and column.foreign_keys:
                    for fk in column.foreign_keys:
                        target_table = fk.column.table.name
                        target_model = self.get_model_by_table_name(target_table)
                        if target_model:
                            self.relationships.append({
                                'from_model': model_name,
                                'from_column': column_name,
                                'to_model': target_model,
                                'to_column': 'id',
                                'relationship_type': 'Many-to-One' if not column.nullable else 'Many-to-One (Optional)'
                            })
    
    def get_model_by_table_name(self, table_name: str) -> Optional[str]:
        """Get model name by table name."""
        for model_name, model_class in self.models.items():
            if model_class.__tablename__ == table_name:
                return model_name
        return None
    
    def get_model_info(self, model_name: str) -> Dict:
        """Extract model information including columns and their types."""
        model_class = self.models[model_name]
        info = {
            'name': model_name,
            'table_name': model_class.__tablename__,
            'columns': []
        }
        
        for column_name, column in model_class.__table__.columns.items():
            col_info = {
                'name': column_name,
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'unique': column.unique,
                'index': column.index,
                'foreign_key': bool(column.foreign_keys)
            }
            info['columns'].append(col_info)
        
        return info
    
    def generate_text_erd(self) -> str:
        """Generate a text-based ERD representation."""
        output = []
        output.append("=" * 80)
        output.append("ENTITY RELATIONSHIP DIAGRAM")
        output.append("=" * 80)
        output.append("")
        
        # Model definitions
        for model_name in self.models.keys():
            model_info = self.get_model_info(model_name)
            output.append(f"Entity: {model_info['name']} (Table: {model_info['table_name']})")
            output.append("-" * 50)
            
            for col in model_info['columns']:
                pk_marker = " [PK]" if col['primary_key'] else ""
                fk_marker = " [FK]" if col['foreign_key'] else ""
                nullable_marker = " [NULL]" if col['nullable'] else ""
                unique_marker = " [UNIQUE]" if col['unique'] else ""
                index_marker = " [INDEX]" if col['index'] else ""
                
                output.append(f"  {col['name']}: {col['type']}{pk_marker}{fk_marker}{nullable_marker}{unique_marker}{index_marker}")
            
            output.append("")
        
        # Relationships
        output.append("RELATIONSHIPS:")
        output.append("-" * 20)
        for rel in self.relationships:
            output.append(f"{rel['from_model']}.{rel['from_column']} -> {rel['to_model']}.{rel['to_column']} ({rel['relationship_type']})")
        
        output.append("")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def generate_visual_erd(self, output_path: str = "erd_diagram.png"):
        """Generate a visual ERD using matplotlib."""
        if not MATPLOTLIB_AVAILABLE:
            print("Error: matplotlib is required for visual ERD generation.")
            return False
        
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Define positions for entities
        positions = {
            'User': (2, 8),
            'Tier': (8, 8),
            'Book': (2, 5),
            'Post': (5, 5),
            'RateLimit': (8, 5)
        }
        
        # Draw entities
        entity_boxes = {}
        for model_name, (x, y) in positions.items():
            model_info = self.get_model_info(model_name)
            box = self.draw_entity(ax, x, y, model_info)
            entity_boxes[model_name] = box
        
        # Draw relationships
        for rel in self.relationships:
            if rel['from_model'] in positions and rel['to_model'] in positions:
                from_pos = positions[rel['from_model']]
                to_pos = positions[rel['to_model']]
                self.draw_relationship(ax, from_pos, to_pos, rel)
        
        # Add title
        ax.text(5, 9.5, 'FastAPI Database ERD', ha='center', va='center', 
                fontsize=20, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visual ERD saved to: {output_path}")
        return True
    
    def draw_entity(self, ax, x: float, y: float, model_info: Dict) -> FancyBboxPatch:
        """Draw an entity box on the plot."""
        # Calculate box dimensions based on content
        num_columns = len(model_info['columns'])
        box_height = max(0.8, num_columns * 0.15 + 0.3)
        box_width = 1.8
        
        # Draw entity box
        box = FancyBboxPatch(
            (x - box_width/2, y - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.1",
            facecolor='lightblue',
            edgecolor='black',
            linewidth=1.5
        )
        ax.add_patch(box)
        
        # Add entity name
        ax.text(x, y + box_height/2 - 0.1, model_info['name'], 
                ha='center', va='center', fontweight='bold', fontsize=12)
        
        # Add columns
        y_offset = y + box_height/2 - 0.3
        for col in model_info['columns']:
            # Determine column style based on properties
            if col['primary_key']:
                weight = 'bold'
                style = 'normal'
                color = 'red'
            elif col['foreign_key']:
                weight = 'normal'
                style = 'italic'
                color = 'blue'
            else:
                weight = 'normal'
                style = 'normal'
                color = 'black'
            
            # Add column markers
            markers = []
            if col['primary_key']:
                markers.append("PK")
            if col['foreign_key']:
                markers.append("FK")
            if col['unique']:
                markers.append("U")
            if col['index']:
                markers.append("I")
            
            marker_text = f" [{', '.join(markers)}]" if markers else ""
            column_text = f"{col['name']}: {col['type']}{marker_text}"
            
            ax.text(x, y_offset, column_text, ha='center', va='center', 
                   fontsize=8, style=style, weight=weight, color=color)
            y_offset -= 0.15
        
        return box
    
    def draw_relationship(self, ax, from_pos: Tuple[float, float], 
                        to_pos: Tuple[float, float], rel: Dict):
        """Draw a relationship line between entities."""
        # Calculate arrow position
        x1, y1 = from_pos
        x2, y2 = to_pos
        
        # Draw arrow
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', lw=1.5, color='red'))
        
        # Add relationship label
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y, rel['relationship_type'], 
               ha='center', va='center', fontsize=8, 
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))


def main():
    """Main function to run the ERD generator."""
    parser = argparse.ArgumentParser(description='Generate ERD for FastAPI models')
    parser.add_argument('--output', '-o', default='erd_diagram.png',
                       help='Output file path for visual ERD (default: erd_diagram.png)')
    parser.add_argument('--text-only', '-t', action='store_true',
                       help='Generate only text ERD')
    parser.add_argument('--visual-only', '-v', action='store_true',
                       help='Generate only visual ERD')
    
    args = parser.parse_args()
    
    generator = ERDGenerator()
    
    # Generate text ERD
    if not args.visual_only:
        text_erd = generator.generate_text_erd()
        print(text_erd)
        
        # Save text ERD to file
        text_output_path = args.output.replace('.png', '.txt')
        with open(text_output_path, 'w') as f:
            f.write(text_erd)
        print(f"Text ERD saved to: {text_output_path}")
    
    # Generate visual ERD
    if not args.text_only and MATPLOTLIB_AVAILABLE:
        success = generator.generate_visual_erd(args.output)
        if not success:
            print("Failed to generate visual ERD.")
    elif not args.text_only and not MATPLOTLIB_AVAILABLE:
        print("Visual ERD generation skipped - matplotlib not available.")


if __name__ == "__main__":
    main()
