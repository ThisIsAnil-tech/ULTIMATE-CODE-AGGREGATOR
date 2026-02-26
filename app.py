# app_enhanced.py - WITH DEPTH-CONTROLLED FOLDER SELECTION
import streamlit as st
import os
import zipfile
import mimetypes
import chardet
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List, Tuple, Optional
import tempfile
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Ultimate Code Aggregator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        background: linear-gradient(45deg, #1E88E5, #0D47A1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .success-msg {
        padding: 1.5rem;
        background-color: rgba(76, 175, 80, 0.1);
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .error-msg {
        padding: 1.5rem;
        background-color: rgba(244, 67, 54, 0.1);
        border-radius: 10px;
        border-left: 5px solid #F44336;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1.5rem;
        background-color: rgba(30, 136, 229, 0.1);
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #E0E0E0;
    }
    
    .card {
        background-color: #F5F5F5;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-card {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #1E88E5, #0D47A1);
        color: white;
        border-radius: 10px;
        margin: 0.5rem;
    }
    
    .file-tree {
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9rem;
        line-height: 1.4;
        padding: 1rem;
        background-color: #F5F5F5;
        border-radius: 5px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        background-color: #1E88E5;
        color: white;
        border-radius: 4px;
        font-size: 0.8rem;
    }
    
    .folder-checkbox-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .folder-item {
        padding: 2px 0;
        font-family: 'Consolas', monospace;
        font-size: 0.9rem;
    }
    
    .folder-indent-0 { margin-left: 0px; }
    .folder-indent-1 { margin-left: 20px; }
    .folder-indent-2 { margin-left: 40px; }
    .folder-indent-3 { margin-left: 60px; }
    .folder-indent-4 { margin-left: 80px; }
    .folder-indent-5 { margin-left: 100px; }
    
    .depth-control {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .folder-summary {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# COMPLETE LIST OF FILE EXTENSIONS (Enhanced)
COMPLETE_EXTENSIONS = {
    # Programming Languages
    '.py': 'Python', '.pyw': 'Python Window', '.pyx': 'Cython', '.pyi': 'Python Stub',
    '.js': 'JavaScript', '.jsx': 'React JSX', '.ts': 'TypeScript', '.tsx': 'React TSX',
    '.java': 'Java', '.class': 'Java Class', '.jar': 'Java Archive',
    '.cpp': 'C++', '.cxx': 'C++', '.cc': 'C++', '.c': 'C', '.h': 'C Header',
    '.hpp': 'C++ Header', '.hxx': 'C++ Header', '.cs': 'C#', '.vb': 'VB.NET',
    '.fs': 'F#', '.fsx': 'F# Script', '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby',
    '.rbw': 'Ruby Window', '.rake': 'Ruby Rake', '.php': 'PHP', '.php3': 'PHP',
    '.php4': 'PHP', '.php5': 'PHP', '.phtml': 'PHP HTML', '.pl': 'Perl',
    '.pm': 'Perl Module', '.t': 'Perl Test', '.pod': 'Perl POD', '.swift': 'Swift',
    '.kt': 'Kotlin', '.kts': 'Kotlin Script', '.scala': 'Scala', '.sc': 'Scala Script',
    '.groovy': 'Groovy', '.gvy': 'Groovy', '.gy': 'Groovy', '.gsh': 'Groovy Shell',
    '.clj': 'Clojure', '.cljs': 'ClojureScript', '.cljc': 'Clojure Common',
    '.lua': 'Lua', '.r': 'R', '.R': 'R', '.rdata': 'R Data', '.rds': 'R Data',
    '.m': 'Objective-C/Matlab', '.mm': 'Objective-C++', '.f': 'Fortran',
    '.f90': 'Fortran 90', '.f95': 'Fortran 95', '.f03': 'Fortran 2003',
    '.pas': 'Pascal', '.pp': 'Pascal', '.d': 'D', '.dart': 'Dart',
    '.elm': 'Elm', '.erl': 'Erlang', '.hrl': 'Erlang Header', '.ex': 'Elixir',
    '.exs': 'Elixir Script', '.hs': 'Haskell', '.lhs': 'Literate Haskell',
    '.ml': 'OCaml', '.mli': 'OCaml Interface', '.fsi': 'F# Signature',
    '.fsx': 'F# Script', '.v': 'Verilog', '.vh': 'Verilog Header',
    '.sv': 'SystemVerilog', '.svh': 'SystemVerilog Header', '.vhd': 'VHDL',
    
    # Web Technologies
    '.html': 'HTML', '.htm': 'HTML', '.xhtml': 'XHTML', '.html5': 'HTML5',
    '.css': 'CSS', '.scss': 'SASS', '.sass': 'SASS', '.less': 'LESS',
    '.styl': 'Stylus', '.vue': 'Vue.js', '.svelte': 'Svelte', '.astro': 'Astro',
    '.php': 'PHP', '.asp': 'ASP', '.aspx': 'ASP.NET', '.jsp': 'JavaServer Pages',
    '.jspx': 'JavaServer Pages XML', '.wasm': 'WebAssembly',
    
    # Configuration Files
    '.json': 'JSON', '.jsonc': 'JSON with Comments', '.json5': 'JSON5',
    '.jsonld': 'JSON-LD', '.xml': 'XML', '.xml.dist': 'XML Distribution',
    '.xsl': 'XSLT', '.xslt': 'XSLT', '.xsd': 'XML Schema', '.dtd': 'DTD',
    '.yaml': 'YAML', '.yml': 'YAML', '.yaml.dist': 'YAML Distribution',
    '.toml': 'TOML', '.ini': 'INI', '.cfg': 'Config', '.conf': 'Config',
    '.properties': 'Properties', '.env': 'Environment', '.env.example': 'Env Example',
    '.editorconfig': 'Editor Config', '.prettierrc': 'Prettier', '.eslintrc': 'ESLint',
    '.babelrc': 'Babel', '.npmrc': 'NPM', '.yarnrc': 'Yarn', '.pnp.cjs': 'Plug n Play',
    
    # Shell Scripts
    '.sh': 'Shell', '.bash': 'Bash', '.zsh': 'Zsh', '.fish': 'Fish',
    '.ps1': 'PowerShell', '.psm1': 'PowerShell Module', '.psd1': 'PowerShell Data',
    '.ps1xml': 'PowerShell XML', '.bat': 'Batch', '.cmd': 'Command',
    '.vbs': 'VBScript', '.vbe': 'VBScript Encoded', '.wsf': 'Windows Script',
    '.wsh': 'Windows Script Host', '.awk': 'AWK', '.sed': 'SED',
    
    # Database
    '.sql': 'SQL', '.psql': 'PostgreSQL', '.ddl': 'DDL', '.dml': 'DML',
    '.sqlite': 'SQLite', '.db': 'Database', '.sqlitedb': 'SQLite DB',
    '.mdb': 'Access DB', '.frm': 'MySQL Format', '.myi': 'MySQL Index',
    '.myd': 'MySQL Data', '.ibd': 'InnoDB Data',
    
    # Documentation
    '.md': 'Markdown', '.markdown': 'Markdown', '.mdown': 'Markdown',
    '.mdwn': 'Markdown', '.mkd': 'Markdown', '.mkdn': 'Markdown',
    '.rst': 'reStructuredText', '.tex': 'LaTeX', '.ltx': 'LaTeX',
    '.aux': 'LaTeX Aux', '.bib': 'BibTeX', '.txt': 'Text', '.rtf': 'Rich Text',
    '.doc': 'Word', '.docx': 'Word', '.odt': 'OpenDocument Text',
    
    # Build & Package Managers
    '.dockerfile': 'Dockerfile', 'Dockerfile': 'Dockerfile',
    '.makefile': 'Makefile', 'Makefile': 'Makefile', 'makefile': 'Makefile',
    '.gradle': 'Gradle', '.gradle.kts': 'Gradle Kotlin', '.pom': 'Maven POM',
    '.xml': 'Maven POM', '.cmake': 'CMake', '.bazel': 'Bazel', '.bzl': 'Bazel',
    '.bazelrc': 'Bazel Config', '.buckconfig': 'Buck Config',
    
    # IDE & Editor
    '.vscode': 'VS Code', '.code-workspace': 'VS Code Workspace',
    '.idea': 'IntelliJ IDEA', '.iml': 'IntelliJ Module',
    '.sln': 'Visual Studio', '.csproj': 'C# Project', '.vcxproj': 'C++ Project',
    '.fsproj': 'F# Project', '.vbproj': 'VB Project', '.xproj': '.NET Core Project',
    
    # Data & Serialization
    '.csv': 'CSV', '.tsv': 'TSV', '.xlsx': 'Excel', '.xls': 'Excel',
    '.parquet': 'Parquet', '.feather': 'Feather', '.arrow': 'Arrow',
    '.h5': 'HDF5', '.hdf5': 'HDF5', '.nc': 'NetCDF', '.zarr': 'Zarr',
    '.avro': 'Avro', '.orc': 'ORC', '.pkl': 'Pickle', '.pickle': 'Pickle',
    '.joblib': 'Joblib', '.npy': 'NumPy Array', '.npz': 'NumPy Zipped',
    
    # Web Assets
    '.svg': 'SVG', '.svgz': 'SVG', '.ai': 'Illustrator', '.eps': 'EPS',
    '.ps': 'PostScript', '.psd': 'Photoshop', '.xcf': 'GIMP',
    '.sketch': 'Sketch', '.fig': 'Figma',
    
    # Fonts
    '.ttf': 'TrueType', '.otf': 'OpenType', '.woff': 'Web Open Font',
    '.woff2': 'Web Open Font 2', '.eot': 'Embedded OpenType',
    
    # Executables & Libraries
    '.exe': 'Executable', '.dll': 'Dynamic Library', '.so': 'Shared Object',
    '.dylib': 'Dynamic Library', '.lib': 'Static Library', '.a': 'Static Archive',
    '.o': 'Object File', '.obj': 'Object File', '.class': 'Java Class',
    
    # Archives
    '.zip': 'ZIP Archive', '.tar': 'TAR Archive', '.gz': 'GZIP Archive',
    '.tgz': 'GZIP TAR', '.bz2': 'BZIP2 Archive', '.xz': 'XZ Archive',
    '.rar': 'RAR Archive', '.7z': '7-Zip Archive', '.zst': 'Zstandard',
    
    # Version Control
    '.gitignore': 'Git Ignore', '.gitattributes': 'Git Attributes',
    '.gitmodules': 'Git Modules', '.gitkeep': 'Git Keep',
    '.svn': 'SVN', '.hgignore': 'Mercurial Ignore', '.hg': 'Mercurial',
    
    # CI/CD
    '.travis.yml': 'Travis CI', '.circleci': 'CircleCI', '.gitlab-ci.yml': 'GitLab CI',
    '.jenkinsfile': 'Jenkins', '.drone.yml': 'Drone CI', '.github': 'GitHub Actions',
    '.azure-pipelines.yml': 'Azure Pipelines', '.codefresh.yml': 'Codefresh',
    
    # Logs & Outputs
    '.log': 'Log', '.out': 'Output', '.err': 'Error', '.debug': 'Debug',
    '.trace': 'Trace', '.dump': 'Dump',
    
    # Temporary
    '.tmp': 'Temporary', '.temp': 'Temporary', '.bak': 'Backup',
    '.backup': 'Backup', '.old': 'Old', '.orig': 'Original',
    
    # Misc
    '.lock': 'Lock', '.pid': 'PID', '.socket': 'Socket',
    '.key': 'Key', '.pem': 'PEM', '.crt': 'Certificate', '.csr': 'CSR',
}

class CodeAggregator:
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_bytes': 0,
            'files_by_type': {},
            'processing_time': 0,
            'ignored_files': 0,
            'errors': 0,
            'binary_files': 0,
            'large_files': 0
        }
        self.processed_files = []
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(min(10000, os.path.getsize(file_path)))  # Read up to 10KB
                if not raw_data:
                    return 'utf-8'
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8') or 'utf-8'
        except Exception as e:
            return 'utf-8'
    
    def is_binary(self, file_path: str) -> bool:
        """Check if file is binary by reading first chunk."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk  # Binary files typically contain null bytes
        except:
            return True
    
    def get_folders(self, directory: str, max_depth: int = None) -> List[Dict]:
        """Get all folders recursively with their paths and levels, limited by max_depth."""
        folders = []
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                level = root.replace(directory, '').count(os.sep)
                
                # Skip if beyond max depth
                if max_depth is not None and level > max_depth:
                    dirs[:] = []  # Don't traverse deeper
                    continue
                
                rel_path = os.path.relpath(root, directory)
                if rel_path == '.':
                    continue
                    
                folders.append({
                    'path': root,
                    'name': os.path.basename(root),
                    'rel_path': rel_path,
                    'level': level
                })
        except Exception as e:
            st.error(f"Error reading folders: {str(e)}")
        
        return sorted(folders, key=lambda x: x['rel_path'])
    
    def get_file_tree(self, directory: str, max_depth: int = 3, max_files_per_dir: int = 10, 
                      excluded_folders: List[str] = None, folder_depth: int = None) -> str:
        """Generate ASCII file tree structure with excluded folders and depth control."""
        tree = []
        if excluded_folders is None:
            excluded_folders = []
            
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                level = root.replace(directory, '').count(os.sep)
                
                # Apply depth limit for tree display
                if max_depth is not None and level > max_depth:
                    dirs[:] = []  # Don't traverse deeper
                    continue
                
                # Check if current directory should be excluded
                rel_path = os.path.relpath(root, directory)
                if rel_path != '.' and any(rel_path.startswith(excluded) for excluded in excluded_folders):
                    continue
                
                # Filter out excluded subdirectories
                dirs[:] = [d for d in dirs if not any(
                    os.path.join(rel_path, d).startswith(excluded) 
                    for excluded in excluded_folders
                )]
                
                indent = ' ' * 2 * level
                dir_name = os.path.basename(root)
                if level == 0:
                    dir_name = os.path.basename(directory) or directory
                tree.append(f"{indent}📁 {dir_name}/")
                
                subindent = ' ' * 2 * (level + 1)
                # Sort files by extension
                files.sort()
                shown_files = 0
                for file in files:
                    if shown_files >= max_files_per_dir:
                        break
                    # Skip hidden files
                    if file.startswith('.'):
                        continue
                    ext = os.path.splitext(file)[1]
                    icon = "📄" if ext in COMPLETE_EXTENSIONS else "📎"
                    tree.append(f"{subindent}{icon} {file}")
                    shown_files += 1
                
                if len(files) > max_files_per_dir:
                    tree.append(f"{subindent}... and {len(files) - max_files_per_dir} more files")
        except Exception as e:
            tree.append(f"Error reading directory: {str(e)}")
        
        return '\n'.join(tree)
    
    def should_ignore_file(self, filename: str, gitignore_patterns: List[str]) -> bool:
        """Check if file should be ignored based on gitignore patterns."""
        for pattern in gitignore_patterns:
            if pattern in filename or (pattern.endswith('/') and pattern[:-1] in filename):
                return True
        return False
    
    def traverse_and_write_code(self, source_dir: str, output_file: str, 
                               include_ext: List[str] = None,
                               exclude_ext: List[str] = None,
                               exclude_dirs: List[str] = None,
                               include_line_numbers: bool = False,
                               respect_gitignore: bool = False,
                               max_file_size_mb: int = 5,
                               include_hidden: bool = False) -> Tuple[bool, str, Dict]:
        """Enhanced version with exact paths and all features."""
        
        # Reset stats
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_bytes': 0,
            'files_by_type': {},
            'processing_time': 0,
            'ignored_files': 0,
            'errors': 0,
            'binary_files': 0,
            'large_files': 0
        }
        self.processed_files = []
        
        start_time = time.time()
        
        # Default values
        if include_ext is None:
            include_ext = list(COMPLETE_EXTENSIONS.keys())
        if exclude_ext is None:
            exclude_ext = []
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                           'env', 'dist', 'build', '.idea', '.vscode', '.DS_Store']
        
        # Convert to sets for faster lookup
        include_ext_set = set(include_ext)
        exclude_ext_set = set(exclude_ext)
        
        # Read .gitignore if requested
        gitignore_patterns = []
        if respect_gitignore:
            gitignore_path = os.path.join(source_dir, '.gitignore')
            if os.path.exists(gitignore_path):
                try:
                    with open(gitignore_path, 'r', encoding='utf-8') as f:
                        gitignore_patterns = [line.strip() for line in f 
                                            if line.strip() and not line.startswith('#')]
                except:
                    pass
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as txt_file:
                # Write header
                txt_file.write(f"Code Aggregator Export\n")
                txt_file.write(f"=" * 100 + "\n")
                txt_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                txt_file.write(f"Source Directory: {os.path.abspath(source_dir)}\n")
                txt_file.write(f"Total Files Found: {sum(1 for _ in Path(source_dir).rglob('*') if _.is_file())}\n")
                txt_file.write("=" * 100 + "\n\n")
                
                # Write excluded folders
                if exclude_dirs:
                    txt_file.write(f"Excluded Folders:\n")
                    for folder in exclude_dirs:
                        txt_file.write(f"  - {folder}\n")
                    txt_file.write("=" * 100 + "\n\n")
                
                # Traverse through all directories and files
                file_count = 0
                for root, dirs, files in os.walk(source_dir):
                    # Check if current directory should be excluded
                    rel_path = os.path.relpath(root, source_dir)
                    if rel_path != '.' and any(rel_path.startswith(excluded) for excluded in exclude_dirs):
                        continue
                    
                    # Remove excluded directories from traversal
                    dirs[:] = [d for d in dirs if not any(
                        os.path.join(rel_path, d).startswith(excluded) 
                        for excluded in exclude_dirs
                    )]
                    
                    # Remove hidden directories if not included
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    # Sort for consistent output
                    dirs.sort()
                    files.sort()
                    
                    for file in files:
                        # Skip hidden files if not included
                        if not include_hidden and file.startswith('.'):
                            self.stats['ignored_files'] += 1
                            continue
                        
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        # Skip based on gitignore patterns
                        if respect_gitignore and self.should_ignore_file(file_path, gitignore_patterns):
                            self.stats['ignored_files'] += 1
                            continue
                        
                        # Check file size first
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size > max_file_size_mb * 1024 * 1024:
                                self.stats['large_files'] += 1
                                continue
                        except:
                            self.stats['errors'] += 1
                            continue
                        
                        # Check if it's a text file
                        if self.is_binary(file_path):
                            self.stats['binary_files'] += 1
                            continue
                        
                        # Apply extension filters
                        if include_ext and file_ext not in include_ext_set:
                            continue
                        if exclude_ext and file_ext in exclude_ext_set:
                            continue
                        
                        try:
                            # Get EXACT absolute path
                            abs_path = os.path.abspath(file_path)
                            
                            # Detect encoding
                            encoding = self.detect_encoding(file_path)
                            
                            # Read file content
                            with open(file_path, 'r', encoding=encoding, errors='ignore') as code_file:
                                content = code_file.read()
                            
                            # Calculate line count
                            line_count = content.count('\n') + 1 if content else 0
                            
                            # Update statistics
                            self.stats['total_files'] += 1
                            self.stats['total_lines'] += line_count
                            self.stats['total_bytes'] += file_size
                            
                            # Count by file type
                            file_type = COMPLETE_EXTENSIONS.get(file_ext, 'Unknown')
                            self.stats['files_by_type'][file_type] = self.stats['files_by_type'].get(file_type, 0) + 1
                            
                            # Store for processed files list
                            self.processed_files.append({
                                'path': abs_path,
                                'type': file_type,
                                'lines': line_count,
                                'size': file_size
                            })
                            
                            # Write to output file with EXACT path
                            txt_file.write(f"// FILE: {abs_path}\n")
                            txt_file.write(f"// RELATIVE: {rel_path}\n")
                            txt_file.write(f"// TYPE: {file_type} | SIZE: {file_size:,} bytes | LINES: {line_count:,}\n")
                            txt_file.write("=" * 100 + "\n\n")
                            
                            # Add line numbers if requested
                            if include_line_numbers:
                                lines = content.split('\n')
                                numbered_content = '\n'.join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
                                txt_file.write(numbered_content)
                            else:
                                txt_file.write(content)
                            
                            txt_file.write("\n\n" + "=" * 100 + "\n\n")
                            
                            file_count += 1
                            
                            # Update progress every 10 files
                            if file_count % 10 == 0:
                                st.session_state['progress'] = file_count
                            
                        except Exception as e:
                            error_msg = f"// Error reading {file_path}: {str(e)[:200]}\n"
                            txt_file.write(error_msg)
                            txt_file.write("=" * 100 + "\n\n")
                            self.stats['errors'] += 1
                            continue
            
            self.stats['processing_time'] = time.time() - start_time
            return True, output_file, self.stats
            
        except Exception as e:
            return False, str(e), self.stats
    
    def create_zip_archive(self, source_dir: str, output_zip: str, 
                          include_ext: List[str] = None,
                          exclude_dirs: List[str] = None) -> Tuple[bool, str, int]:
        """Create ZIP archive of all code files."""
        file_count = 0
        try:
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    # Check if current directory should be excluded
                    rel_path = os.path.relpath(root, source_dir)
                    if rel_path != '.' and exclude_dirs and any(rel_path.startswith(excluded) for excluded in exclude_dirs):
                        continue
                    
                    # Remove excluded directories from traversal
                    if exclude_dirs:
                        dirs[:] = [d for d in dirs if not any(
                            os.path.join(rel_path, d).startswith(excluded) 
                            for excluded in exclude_dirs
                        )]
                    
                    for file in files:
                        file_ext = os.path.splitext(file)[1].lower()
                        if include_ext and file_ext not in include_ext:
                            continue
                        
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
                        file_count += 1
            
            return True, output_zip, file_count
        except Exception as e:
            return False, str(e), file_count

def main():
    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'output_path' not in st.session_state:
        st.session_state.output_path = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'progress' not in st.session_state:
        st.session_state.progress = 0
    if 'excluded_folders' not in st.session_state:
        st.session_state.excluded_folders = []
    if 'folder_list' not in st.session_state:
        st.session_state.folder_list = []
    if 'current_source_dir' not in st.session_state:
        st.session_state.current_source_dir = None
    if 'folder_depth' not in st.session_state:
        st.session_state.folder_depth = 3
    if 'tree_depth' not in st.session_state:
        st.session_state.tree_depth = 3
    
    # Initialize aggregator
    aggregator = CodeAggregator()
    
    # Header
    st.markdown('<h1 class="main-header">🧬 Ultimate Code Aggregator</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File type selection
        st.subheader("📄 File Types")
        
        # Category selection
        categories = {
            "Programming": ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt'],
            "Web": ['.html', '.css', '.jsx', '.tsx', '.vue', '.svelte', '.scss', '.less'],
            "Config": ['.json', '.yaml', '.toml', '.ini', '.xml', '.env'],
            "Scripts": ['.sh', '.bash', '.ps1', '.bat', '.cmd', '.vbs'],
            "Data": ['.csv', '.sql', '.parquet', '.json', '.xml'],
            "Docs": ['.md', '.txt', '.rst', '.tex']
        }
        
        selected_categories = []
        for cat, exts in categories.items():
            if st.checkbox(f"{cat} ({len(exts)})", value=True):
                selected_categories.extend(exts)
        
        # Custom extensions
        custom_ext = st.text_input(
            "Custom extensions (comma-separated):",
            placeholder=".txt,.log,.custom",
            help="Add custom file extensions not in the list"
        )
        
        # Features toggles
        st.subheader("✨ Features")
        include_line_numbers = st.checkbox("Include line numbers", value=False, 
                                          help="Add line numbers to each file")
        respect_gitignore = st.checkbox("Respect .gitignore", value=True,
                                       help="Skip files listed in .gitignore")
        create_zip = st.checkbox("Create ZIP archive", value=False,
                                help="Create a ZIP file with all processed files")
        include_hidden = st.checkbox("Include hidden files", value=False,
                                    help="Include files and folders starting with '.'")
        
        # Depth Control Section
        st.subheader("📏 Depth Control")
        
        with st.container():
            st.markdown('<div class="depth-control">', unsafe_allow_html=True)
            
            # Tree view depth slider
            tree_depth = st.slider(
                "Tree view depth:",
                min_value=1,
                max_value=10,
                value=st.session_state.tree_depth,
                help="How deep to show in the directory tree preview"
            )
            st.session_state.tree_depth = tree_depth
            
            # Folder selection depth slider
            folder_depth = st.slider(
                "Folder selection depth:",
                min_value=1,
                max_value=10,
                value=st.session_state.folder_depth,
                help="How deep to scan for folders in the selection list"
            )
            st.session_state.folder_depth = folder_depth
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Folder selection section
        st.subheader("📁 Select Folders to Exclude")
        
        # Check if source directory is valid
        source_dir = st.session_state.get('dir_input', '')
        if source_dir and os.path.exists(source_dir):
            # Get folders if source directory changed or depth changed
            if (st.session_state.current_source_dir != source_dir or 
                st.session_state.get('last_folder_depth') != folder_depth):
                st.session_state.current_source_dir = source_dir
                st.session_state.folder_list = aggregator.get_folders(source_dir, max_depth=folder_depth)
                st.session_state.excluded_folders = []
                st.session_state.last_folder_depth = folder_depth
            
            # Display folder checkboxes
            if st.session_state.folder_list:
                with st.container():
                    st.markdown('<div class="folder-checkbox-container">', unsafe_allow_html=True)
                    
                    # Select/Deselect all buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Select All", key="select_all_folders"):
                            st.session_state.excluded_folders = [f['rel_path'] for f in st.session_state.folder_list]
                            st.rerun()
                    with col2:
                        if st.button("Deselect All", key="deselect_all_folders"):
                            st.session_state.excluded_folders = []
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Create checkboxes for each folder with indentation
                    for folder in st.session_state.folder_list:
                        indent_class = f"folder-indent-{folder['level']}"
                        folder_name = folder['name']
                        rel_path = folder['rel_path']
                        
                        # Create unique key for each checkbox
                        checkbox_key = f"folder_{rel_path.replace(os.sep, '_')}"
                        
                        # Check if folder is currently excluded
                        is_checked = rel_path in st.session_state.excluded_folders
                        
                        # Display checkbox with indentation using CSS classes
                        st.markdown(f'<div class="folder-item {indent_class}">', unsafe_allow_html=True)
                        checked = st.checkbox(
                            f"📁 {folder_name}",
                            value=is_checked,
                            key=checkbox_key,
                            help=f"Path: {rel_path}"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Update excluded folders list
                        if checked and rel_path not in st.session_state.excluded_folders:
                            st.session_state.excluded_folders.append(rel_path)
                        elif not checked and rel_path in st.session_state.excluded_folders:
                            st.session_state.excluded_folders.remove(rel_path)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show summary
                    total_folders = len(st.session_state.folder_list)
                    excluded_count = len(st.session_state.excluded_folders)
                    
                    st.markdown('<div class="folder-summary">', unsafe_allow_html=True)
                    st.info(f"📊 **{total_folders}** folders found at depth {folder_depth}")
                    if excluded_count > 0:
                        st.warning(f"🚫 Excluding **{excluded_count}** folder(s)")
                    else:
                        st.success(f"✅ No folders excluded")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(f"📂 No folders found at depth {folder_depth}")
        else:
            st.info("👆 Enter a valid directory path above to see folders")
        
        st.markdown("---")
        
        # Statistics display
        st.subheader("📊 Supported Extensions")
        st.write(f"**{len(COMPLETE_EXTENSIONS)}** file types supported")
        
        # Quick stats
        for cat, exts in categories.items():
            count = len([ext for ext in exts if ext in COMPLETE_EXTENSIONS])
            st.progress(count/len(exts), text=f"{cat}: {count}/{len(exts)}")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Process", "🔍 Preview", "📊 Statistics", "ℹ️ About"])
    
    with tab1:
        # Directory input
        st.subheader("📂 Select Source Directory")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            source_dir = st.text_input(
                "Directory path:",
                placeholder="C:\\projects\\my-app or /home/user/projects",
                key="dir_input",
                help="Enter the full path to the directory you want to process"
            )
        
        with col2:
            if st.button("📁 Browse Current"):
                st.info(f"📌 Current working directory: `{os.getcwd()}`")
        
        # File tree preview with depth control and excluded folders
        if source_dir and os.path.exists(source_dir):
            with st.expander("📁 Directory Tree Preview", expanded=True):
                # Add tree depth control here too
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"Tree depth: {st.session_state.tree_depth}")
                with col2:
                    if st.button("🔄 Refresh Tree"):
                        st.rerun()
                
                with st.spinner("Generating tree..."):
                    file_tree = aggregator.get_file_tree(
                        source_dir, 
                        max_depth=st.session_state.tree_depth,
                        max_files_per_dir=8,
                        excluded_folders=st.session_state.excluded_folders,
                        folder_depth=st.session_state.folder_depth
                    )
                    st.code(file_tree, language="text")
                    
                    # Show excluded folders summary
                    if st.session_state.excluded_folders:
                        st.markdown("**🚫 Excluded Folders:**")
                        for folder in st.session_state.excluded_folders[:10]:
                            st.markdown(f"- `{folder}`")
                        if len(st.session_state.excluded_folders) > 10:
                            st.markdown(f"... and {len(st.session_state.excluded_folders) - 10} more")
        elif source_dir:
            st.error(f"❌ Directory not found: `{source_dir}`")
        
        # Output options
        st.subheader("💾 Output Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            output_name = st.text_input(
                "Output filename:",
                value="code_export",
                help="Without extension"
            )
        
        with col2:
            output_format = st.selectbox(
                "Format:",
                [".txt", ".md"],
                help="Output file format"
            )
        
        # Process button
        st.markdown("---")
        process_col1, process_col2, process_col3 = st.columns([1, 2, 1])
        with process_col2:
            if st.button("🚀 Start Aggregation", type="primary", use_container_width=True):
                if not source_dir or not os.path.exists(source_dir):
                    st.error("❌ Please enter a valid directory path!")
                else:
                    # Clean path
                    source_dir_clean = source_dir.rstrip('>').strip()
                    
                    # Prepare extensions
                    include_extensions = selected_categories.copy()
                    
                    # Add custom extensions
                    if custom_ext:
                        custom_list = ['.' + ext.strip().lstrip('.') for ext in custom_ext.split(',') if ext.strip()]
                        include_extensions.extend(custom_list)
                    
                    # Remove duplicates
                    include_extensions = list(set(include_extensions))
                    
                    # Prepare output path
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"{output_name}_{timestamp}{output_format}"
                    output_path = os.path.join(tempfile.gettempdir(), output_filename)
                    
                    # Get excluded folders from session state
                    exclude_list = st.session_state.excluded_folders.copy()
                    
                    # Add default excluded directories
                    default_excludes = ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                                       'env', 'dist', 'build', '.idea', '.vscode', '.DS_Store']
                    exclude_list.extend([d for d in default_excludes if d not in exclude_list])
                    
                    # Advanced options
                    max_file_size = 10  # Default value
                    
                    # Process
                    with st.spinner("Processing files... This may take a while."):
                        # Progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Process files
                        success, result, stats = aggregator.traverse_and_write_code(
                            source_dir=source_dir_clean,
                            output_file=output_path,
                            include_ext=include_extensions,
                            exclude_dirs=exclude_list,
                            include_line_numbers=include_line_numbers,
                            respect_gitignore=respect_gitignore,
                            max_file_size_mb=max_file_size,
                            include_hidden=include_hidden
                        )
                        
                        progress_bar.progress(100)
                        
                        if success:
                            # Store in session state
                            st.session_state.processed_data = result
                            st.session_state.output_path = output_path
                            st.session_state.stats = stats
                            
                            # Success display
                            st.balloons()
                            
                            st.markdown('<div class="success-msg">', unsafe_allow_html=True)
                            st.success("✅ Processing completed successfully!")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Statistics cards
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("📄 Files Processed", stats['total_files'])
                            with col2:
                                st.metric("📏 Total Lines", f"{stats['total_lines']:,}")
                            with col3:
                                st.metric("⏱️ Processing Time", f"{stats['processing_time']:.2f}s")
                            with col4:
                                st.metric("📊 File Types", len(stats['files_by_type']))
                            
                            # Additional stats
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("⚠️ Errors", stats['errors'])
                            with col2:
                                st.metric("💾 Binary Skipped", stats['binary_files'])
                            with col3:
                                st.metric("📦 Large Skipped", stats['large_files'])
                            
                            # Download section
                            st.subheader("📥 Download Results")
                            
                            # Read output file
                            try:
                                with open(output_path, 'r', encoding='utf-8') as f:
                                    file_content = f.read()
                                
                                # Download buttons
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label=f"⬇️ Download {output_format.upper()}",
                                        data=file_content,
                                        file_name=output_filename,
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                
                                with col2:
                                    # Create ZIP if requested
                                    if create_zip and stats['total_files'] > 0:
                                        zip_filename = output_filename.replace(output_format, '.zip')
                                        zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
                                        
                                        zip_success, zip_result, zip_count = aggregator.create_zip_archive(
                                            source_dir_clean, zip_path, include_extensions, exclude_list
                                        )
                                        
                                        if zip_success and zip_count > 0:
                                            with open(zip_path, 'rb') as zf:
                                                zip_data = zf.read()
                                            st.download_button(
                                                label=f"📦 Download ZIP ({zip_count} files)",
                                                data=zip_data,
                                                file_name=zip_filename,
                                                mime="application/zip",
                                                use_container_width=True
                                            )
                            
                                # File info
                                with st.expander("📋 File Information", expanded=True):
                                    st.info(f"**Location:** `{output_path}`")
                                    st.info(f"**Size:** {os.path.getsize(output_path):,} bytes")
                                    
                                    # Show excluded folders
                                    if exclude_list:
                                        st.info(f"**Excluded Folders:** {', '.join(exclude_list[:10])}")
                                        if len(exclude_list) > 10:
                                            st.info(f"... and {len(exclude_list) - 10} more")
                                    
                                    # File type distribution
                                    if stats['files_by_type']:
                                        st.subheader("📊 File Type Distribution")
                                        for file_type, count in sorted(stats['files_by_type'].items(), key=lambda x: x[1], reverse=True)[:15]:
                                            percentage = (count / stats['total_files']) * 100
                                            st.write(f"• {file_type}: {count} files ({percentage:.1f}%)")
                            
                            except Exception as e:
                                st.error(f"Error reading output file: {str(e)}")
                        
                        else:
                            st.error(f"❌ Error: {result}")
    
    with tab2:
        st.subheader("🔍 File Preview")
        
        if st.session_state.output_path and os.path.exists(st.session_state.output_path):
            try:
                with open(st.session_state.output_path, 'r', encoding='utf-8') as f:
                    preview_content = f.read(5000)  # Show first 5000 chars
                
                st.code(preview_content, language='text')
                
                if len(preview_content) == 5000:
                    st.caption("📝 Showing first 5,000 characters. Use download for full file.")
                    
                # Show processed files list
                if hasattr(aggregator, 'processed_files') and aggregator.processed_files:
                    with st.expander("📋 Processed Files"):
                        for file_info in aggregator.processed_files[:50]:  # Show first 50
                            st.text(f"📄 {file_info['path']} ({file_info['lines']} lines)")
                        if len(aggregator.processed_files) > 50:
                            st.info(f"... and {len(aggregator.processed_files) - 50} more files")
            except Exception as e:
                st.error(f"Error reading preview: {str(e)}")
        else:
            st.info("📌 Process a directory first to see preview here.")
    
    with tab3:
        st.subheader("📊 Statistics Dashboard")
        
        if st.session_state.stats:
            stats = st.session_state.stats
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📄 Total Files", stats['total_files'])
            with col2:
                st.metric("📏 Lines of Code", f"{stats['total_lines']:,}")
            with col3:
                st.metric("💾 Total Size", f"{stats['total_bytes'] / 1024:.2f} KB")
            with col4:
                st.metric("⏱️ Processing Time", f"{stats['processing_time']:.2f}s")
            
            # Processing details
            st.subheader("⚙️ Processing Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("⚠️ Errors", stats['errors'])
            with col2:
                st.metric("💾 Binary Files Skipped", stats['binary_files'])
            with col3:
                st.metric("📦 Large Files Skipped", stats['large_files'])
            
            # File type distribution
            if stats['files_by_type']:
                st.subheader("📊 File Type Distribution")
                
                # Create DataFrame for visualization
                df = pd.DataFrame({
                    'File Type': list(stats['files_by_type'].keys()),
                    'Count': list(stats['files_by_type'].values())
                }).sort_values('Count', ascending=False)
                
                # Display as bar chart
                st.bar_chart(df.set_index('File Type'))
                
                # Display as table
                with st.expander("📋 Detailed Distribution"):
                    st.dataframe(df, use_container_width=True)
        else:
            st.info("📌 Process a directory first to see statistics.")
        
        # Global statistics
        st.subheader("🌍 Global Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Extensions", len(COMPLETE_EXTENSIONS))
        with col2:
            text_files = sum(1 for ext in COMPLETE_EXTENSIONS.keys() 
                           if ext in ['.txt', '.md', '.rst', '.tex', '.log'])
            st.metric("Documentation", text_files)
        with col3:
            config_files = len([ext for ext in COMPLETE_EXTENSIONS.keys() 
                              if ext in ['.json', '.yaml', '.toml', '.ini', '.xml', '.env']])
            st.metric("Config Files", config_files)
        with col4:
            code_files = len([ext for ext in COMPLETE_EXTENSIONS.keys() 
                            if ext in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']])
            st.metric("Code Files", code_files)
        
        # File type categories visualization
        st.subheader("📁 File Categories")
        
        # Categorize extensions
        categories = {
            "Programming": [ext for ext in COMPLETE_EXTENSIONS.keys() 
                          if ext in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt']],
            "Web": [ext for ext in COMPLETE_EXTENSIONS.keys() 
                   if ext in ['.html', '.css', '.jsx', '.tsx', '.vue', '.svelte', '.scss', '.less']],
            "Config": [ext for ext in COMPLETE_EXTENSIONS.keys() 
                      if ext in ['.json', '.yaml', '.toml', '.ini', '.xml', '.env']],
            "Scripts": [ext for ext in COMPLETE_EXTENSIONS.keys() 
                       if ext in ['.sh', '.bash', '.ps1', '.bat', '.cmd', '.vbs']],
            "Data": [ext for ext in COMPLETE_EXTENSIONS.keys() 
                    if ext in ['.csv', '.sql', '.parquet', '.json', '.xml']],
            "Documentation": [ext for ext in COMPLETE_EXTENSIONS.keys() 
                            if ext in ['.md', '.txt', '.rst', '.tex']],
            "Other": []
        }
        
        # Calculate counts
        category_counts = {}
        for category, extensions in categories.items():
            if category != "Other":
                category_counts[category] = len(extensions)
        
        # Add other category
        all_extensions = set(COMPLETE_EXTENSIONS.keys())
        categorized_extensions = set()
        for exts in categories.values():
            categorized_extensions.update(exts)
        category_counts["Other"] = len(all_extensions - categorized_extensions)
        
        # Create DataFrame for chart
        chart_data = pd.DataFrame({
            'Category': list(category_counts.keys()),
            'Count': list(category_counts.values())
        })
        
        st.bar_chart(chart_data.set_index('Category'))
    
    with tab4:
        st.subheader("ℹ️ About")
        
        st.markdown("""
        ### Ultimate Code Aggregator 🧬
        
        A powerful tool for aggregating and analyzing code files from any directory.
        
        #### ✨ Features:
        - 📁 Process entire directories recursively
        - 🔍 Auto-detect file encodings
        - 📊 Real-time statistics and metrics
        - 🎯 Filter by file types and extensions
        - 🚫 Respect .gitignore patterns
        - 📦 Create ZIP archives
        - 🔢 Optional line numbers
        - 🌓 Dark/Light mode support
        - 📱 Responsive design
        - 📁 **Interactive folder selection** - Choose specific folders to exclude
        - 📏 **Depth control** - Control how deep to scan for folders and display trees
        
        #### 🚀 How to use:
        1. Enter the source directory path
        2. Configure file types and options
        3. **Adjust depth controls** to see folders at different levels
        4. **Select folders to exclude** in the sidebar
        5. Click "Start Aggregation"
        6. Download the results
        
        #### 📊 Supported formats:
        - **200+** file extensions
        - **30+** programming languages
        - **20+** configuration formats
        - **15+** documentation types
        
        #### 🔒 Privacy:
        - All processing is done locally
        - No data is sent to external servers
        - Files never leave your computer
        
        #### 📝 Tips:
        - Use the depth sliders to control folder visibility
        - Lower depth values show fewer folders for easier selection
        - Higher depth values show all subfolders for precise control
        - The tree view updates in real-time as you select/deselect folders
        - Use "Select All" / "Deselect All" for quick folder selection
        - Custom extensions can be added for unknown file types
        
        #### 🆘 Support:
        For issues or feature requests, please contact the developer.
        
        ---
        **Version:** 2.2.0  
        **Last Updated:** 2024  
        **Developer:** Your Name  
        """)
    
    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)
    with footer_col1:
        st.caption("🔄 Real-time processing")
    with footer_col2:
        st.caption("🔒 Local processing only")
    with footer_col3:
        st.caption("📊 200+ file types")
    with footer_col4:
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()