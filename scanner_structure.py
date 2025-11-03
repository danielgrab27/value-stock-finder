import os
import json
from pathlib import Path
import fnmatch

class RepositoryScanner:
    def __init__(self, root_path="."):
        self.root_path = Path(root_path)
        self.ignore_patterns = [
            '__pycache__', '.git', '.vscode', '.idea', 'venv', 
            'env', '.env', 'node_modules', 'dist', 'build',
            '*.pyc', '*.pyo', '*.pyd', '.DS_Store', 'thumbs.db',
            '*.so', '*.dll', '*.exe', 'repository_structure.json'
        ]
    
    def should_ignore(self, path):
        """Check if path should be ignored"""
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path.name, pattern) or pattern in str(path):
                return True
        return False
    
    def get_file_info(self, file_path):
        """Get file information"""
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'path': str(file_path.relative_to(self.root_path)),
            'size': stat.st_size,
            'lines': self.count_lines(file_path),
            'modified': stat.st_mtime
        }
    
    def count_lines(self, file_path):
        """Count lines in a file (for text files)"""
        try:
            if file_path.suffix in ['.py', '.txt', '.json', '.yml', '.yaml', '.md', '.js', '.html', '.css', '.xml', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return len(f.readlines())
            return 0
        except:
            return 0
    
    def scan(self):
        """Scan the repository and return structure"""
        structure = {
            'root': str(self.root_path),
            'total_files': 0,
            'total_lines': 0,
            'total_size': 0,
            'structure': {},
            'file_types': {},
            'largest_files': []
        }
        
        all_files = []
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and not self.should_ignore(file_path):
                file_info = self.get_file_info(file_path)
                all_files.append(file_info)
                
                # Update totals
                structure['total_files'] += 1
                structure['total_lines'] += file_info['lines']
                structure['total_size'] += file_info['size']
                
                # Track file types
                ext = file_path.suffix.lower() or 'no_extension'
                structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
        
        # Build tree structure
        structure['structure'] = self.build_tree_structure(all_files)
        
        # Get largest files
        structure['largest_files'] = sorted(
            all_files, 
            key=lambda x: x['size'], 
            reverse=True
        )[:10]
        
        # Get files with most lines
        structure['most_lines_files'] = sorted(
            all_files, 
            key=lambda x: x['lines'], 
            reverse=True
        )[:10]
        
        return structure
    
    def build_tree_structure(self, files):
        """Build a tree structure from file list"""
        tree = {}
        
        for file_info in files:
            path_parts = file_info['path'].split(os.sep)
            current_level = tree
            
            for part in path_parts[:-1]:  # All but the last part (filename)
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            # Add file info at the final level
            filename = path_parts[-1]
            current_level[filename] = file_info
        
        return tree
    
    def generate_tree_diagram(self, structure, max_depth=4):
        """Generate a beautiful tree diagram"""
        def build_tree_lines(node, prefix="", depth=0, is_last=False):
            if depth > max_depth:
                return ["│   " * (depth-1) + "└── ..."]
                
            lines = []
            items = sorted(node.items())
            
            for i, (name, value) in enumerate(items):
                is_last_item = i == len(items) - 1
                connector = "└── " if is_last_item else "├── "
                
                if isinstance(value, dict) and 'path' not in value:  # Directory
                    lines.append(prefix + connector + "📁 " + name + "/")
                    
                    new_prefix = prefix + ("    " if is_last_item else "│   ")
                    lines.extend(build_tree_lines(value, new_prefix, depth + 1, is_last_item))
                else:  # File
                    line = prefix + connector + "📄 " + name
                    if isinstance(value, dict) and 'lines' in value and value['lines'] > 0:
                        line += f" ({value['lines']} lines)"
                    lines.append(line)
            
            return lines
        
        tree_lines = ["📂 " + structure['root']]
        tree_lines.extend(build_tree_lines(structure['structure']))
        return tree_lines
    
    def generate_summary(self, structure):
        """Generate a human-readable summary"""
        summary = []
        summary.append("=" * 60)
        summary.append("📊 REPOSITORY SCAN SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Root directory: {structure['root']}")
        summary.append(f"Total files: {structure['total_files']}")
        summary.append(f"Total lines: {structure['total_lines']:,}")
        summary.append(f"Total size: {structure['total_size'] / 1024 / 1024:.2f} MB")
        summary.append("")
        
        summary.append("📈 File types:")
        for ext, count in sorted(structure['file_types'].items(), key=lambda x: x[1], reverse=True):
            summary.append(f"  {ext}: {count} files")
        
        summary.append("")
        summary.append("🏆 Largest files (by size):")
        for i, file_info in enumerate(structure['largest_files'][:5], 1):
            summary.append(f"  {i}. {file_info['path']} ({file_info['size'] / 1024:.1f} KB)")
        
        summary.append("")
        summary.append("📝 Files with most lines:")
        for i, file_info in enumerate(structure['most_lines_files'][:5], 1):
            summary.append(f"  {i}. {file_info['path']} ({file_info['lines']} lines)")
        
        return "\n".join(summary)

def main():
    scanner = RepositoryScanner()
    
    print("🔍 Scanning repository...")
    structure = scanner.scan()
    
    # Generate and print summary
    print("\n" + scanner.generate_summary(structure))
    
    # Generate and print tree diagram
    print("\n" + "🌳 REPOSITORY TREE STRUCTURE")
    print("=" * 50)
    tree_lines = scanner.generate_tree_diagram(structure)
    for line in tree_lines:
        print(line)
    
    # Generate compact version for sharing
    print("\n" + "📤 COMPACT VERSION FOR SHARING")
    print("=" * 50)
    print(f"📋 {Path(structure['root']).name} - {structure['total_files']} files, {structure['total_lines']:,} lines")
    
    # Group files by directory
    dir_stats = {}
    for file_info in structure['most_lines_files']:
        if file_info['lines'] > 50:  # Only significant files
            dir_path = str(Path(file_info['path']).parent)
            if dir_path == '.':
                dir_path = 'root'
            if dir_path not in dir_stats:
                dir_stats[dir_path] = []
            dir_stats[dir_path].append(file_info)
    
    print("\n📁 MAIN DIRECTORIES:")
    for dir_path, files in sorted(dir_stats.items()):
        total_lines = sum(f['lines'] for f in files)
        file_count = len(files)
        print(f"• {dir_path}/ ({file_count} files, {total_lines} lines)")
        for file_info in files[:3]:  # Top 3 files per directory
            print(f"  └── {file_info['name']} ({file_info['lines']} lines)")

if __name__ == "__main__":
    main()
