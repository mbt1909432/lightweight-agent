"""List Directory Tool - List Directory Contents"""
from typing import Dict, Any
from pathlib import Path
from ..base import Tool


class ListDirTool(Tool):
    """List directory contents tool"""
    
    @property
    def name(self) -> str:
        return "list_directory"
    
    @property
    def description(self) -> str:
        return "List files and subdirectories in a directory (non-recursive, only current directory level). Can view contents of specified directory."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "The path to the directory to list (relative to working directory or absolute path)"
                },
                "show_hidden": {
                    "type": "boolean",
                    "description": "Whether to show hidden files (files starting with .)",
                    "default": False
                }
            },
            "required": ["dir_path"]
        }
    
    async def execute(self, **kwargs) -> str:
        """
        Execute list directory
        
        :param kwargs: Contains dir_path and show_hidden
        :return: Directory contents list
        """
        dir_path = kwargs.get("dir_path")
        show_hidden = kwargs.get("show_hidden", False)
        
        if not dir_path:
            return f"Error: dir_path parameter is required"
        
        try:
            # Validate path
            resolved_path = self.session.validate_path(dir_path)
            
            # Check if path exists
            if not resolved_path.exists():
                return f"Error: Directory '{resolved_path}' does not exist"
            
            if not resolved_path.is_dir():
                return f"Error: '{resolved_path}' is not a directory"
            
            # List directory contents
            items = []
            for item in sorted(resolved_path.iterdir()):
                # Filter hidden files
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    items.append(f"[DIR]  {item.name}/")
                else:
                    size = item.stat().st_size
                    size_str = self._format_size(size)
                    items.append(f"[FILE] {item.name} ({size_str})")
            
            if not items:
                return f"Directory '{resolved_path}' is empty"
            
            result = f"Contents of '{resolved_path}':\n\n"
            result += "\n".join(items)
            result += f"\n\nTotal: {len(items)} items"
            
            return result
        
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: Failed to list directory '{dir_path}': {str(e)}"
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

