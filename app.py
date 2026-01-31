# app_enhanced.py - CORRECTED VERSION
import streamlit as st
import os
import sys
import zipfile
import mimetypes
import chardet
from pathlib import Path
import pygments
from pygments import lexers
from pygments.formatters import HtmlFormatter
from datetime import datetime
import json
import time
from typing import Dict, List, Tuple, Optional
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Ultimate Code Aggregator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS with dark/light mode support
st.markdown("""
<style>
    :root {
        --primary-color: #1E88E5;
        --secondary-color: #0D47A1;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #F44336;
        --text-color: #333333;
        --bg-color: #FFFFFF;
        --card-bg: #F5F5F5;
        --border-color: #E0E0E0;
    }
    
    [data-theme="dark"] {
        --primary-color: #64B5F6;
        --secondary-color: #1976D2;
        --success-color: #81C784;
        --warning-color: #FFB74D;
        --danger-color: #E57373;
        --text-color: #E0E0E0;
        --bg-color: #121212;
        --card-bg: #1E1E1E;
        --border-color: #424242;
    }
    
    .main-header {
        font-size: 2.8rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .success-msg {
        padding: 1.5rem;
        background-color: rgba(76, 175, 80, 0.1);
        border-radius: 10px;
        border-left: 5px solid var(--success-color);
        margin: 1rem 0;
        color: var(--text-color);
    }
    
    .error-msg {
        padding: 1.5rem;
        background-color: rgba(244, 67, 54, 0.1);
        border-radius: 10px;
        border-left: 5px solid var(--danger-color);
        margin: 1rem 0;
        color: var(--text-color);
    }
    
    .info-box {
        padding: 1.5rem;
        background-color: rgba(30, 136, 229, 0.1);
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        color: var(--text-color);
    }
    
    .card {
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-card {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border-radius: 10px;
        margin: 0.5rem;
    }
    
    .file-tree {
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.9rem;
        line-height: 1.4;
        padding: 1rem;
        background-color: var(--card-bg);
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
        background-color: var(--primary-color);
        color: white;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# COMPLETE LIST OF FILE EXTENSIONS
COMPLETE_EXTENSIONS = {
    # Programming Languages
    '.py': 'Python', '.js': 'JavaScript', '.jsx': 'React JSX', '.ts': 'TypeScript',
    '.tsx': 'React TSX', '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.h': 'C Header',
    '.hpp': 'C++ Header', '.cs': 'C#', '.vb': 'VB.NET', '.fs': 'F#', '.go': 'Go',
    '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP', '.pl': 'Perl', '.pm': 'Perl Module',
    '.swift': 'Swift', '.kt': 'Kotlin', '.kts': 'Kotlin Script', '.scala': 'Scala',
    '.sc': 'Scala Script', '.groovy': 'Groovy', '.clj': 'Clojure', '.cljs': 'ClojureScript',
    '.lua': 'Lua', '.r': 'R', '.m': 'Objective-C/Matlab', '.mm': 'Objective-C++',
    '.f': 'Fortran', '.f90': 'Fortran 90', '.pas': 'Pascal', '.dart': 'Dart',
    '.elm': 'Elm', '.erl': 'Erlang', '.ex': 'Elixir', '.exs': 'Elixir Script',
    '.hs': 'Haskell', '.lhs': 'Literate Haskell', '.ml': 'OCaml', '.mli': 'OCaml Interface',
    
    # Web Technologies
    '.html': 'HTML', '.htm': 'HTML', '.xhtml': 'XHTML', '.css': 'CSS',
    '.scss': 'SASS', '.sass': 'SASS', '.less': 'LESS', '.styl': 'Stylus',
    '.vue': 'Vue.js', '.svelte': 'Svelte', '.astro': 'Astro',
    
    # Configuration Files
    '.json': 'JSON', '.jsonc': 'JSON with Comments', '.xml': 'XML',
    '.yaml': 'YAML', '.yml': 'YAML', '.toml': 'TOML',
    '.ini': 'INI', '.cfg': 'Config', '.conf': 'Config',
    '.properties': 'Properties', '.env': 'Environment',
    
    # Shell Scripts
    '.sh': 'Shell', '.bash': 'Bash', '.zsh': 'Zsh', '.fish': 'Fish',
    '.ps1': 'PowerShell', '.psm1': 'PowerShell Module',
    '.bat': 'Batch', '.cmd': 'Command', '.vbs': 'VBScript',
    
    # Database
    '.sql': 'SQL', '.psql': 'PostgreSQL', '.ddl': 'DDL',
    
    # Documentation
    '.md': 'Markdown', '.markdown': 'Markdown', '.rst': 'reStructuredText',
    '.tex': 'LaTeX', '.txt': 'Text', '.rtf': 'Rich Text',
    
    # Build & Package Managers
    '.dockerfile': 'Dockerfile', 'dockerfile': 'Dockerfile',
    '.makefile': 'Makefile', 'makefile': 'Makefile',
    '.gradle': 'Gradle', '.pom': 'Maven POM',
    '.cmake': 'CMake', '.bazel': 'Bazel',
    
    # IDE & Editor
    '.vscode': 'VS Code', '.idea': 'IntelliJ',
    '.sln': 'Visual Studio', '.csproj': 'C# Project',
    '.vcxproj': 'C++ Project',
    
    # Data & Serialization
    '.csv': 'CSV', '.tsv': 'TSV', '.xlsx': 'Excel',
    '.parquet': 'Parquet', '.feather': 'Feather',
    '.h5': 'HDF5', '.hdf5': 'HDF5',
    
    # Graphics & Vector
    '.svg': 'SVG', '.ai': 'Illustrator', '.psd': 'Photoshop',
    
    # Audio & Video
    '.mp3': 'MP3', '.wav': 'WAV', '.mp4': 'MP4',
    
    # Fonts
    '.ttf': 'TrueType', '.otf': 'OpenType',
    
    # Executables & Libraries
    '.exe': 'Executable', '.dll': 'Dynamic Library',
    '.so': 'Shared Object', '.dylib': 'Dynamic Library',
    
    # Archives
    '.zip': 'ZIP', '.tar': 'TAR', '.gz': 'GZIP',
    '.rar': 'RAR', '.7z': '7-Zip',
    
    # Virtual Environments
    '.venv': 'Python venv', '.env': 'Environment',
    '.virtualenv': 'Virtualenv',
    
    # Misc
    '.gitignore': 'Git Ignore', '.gitattributes': 'Git Attributes',
    '.editorconfig': 'Editor Config', '.prettierrc': 'Prettier',
    '.eslintrc': 'ESLint', '.babelrc': 'Babel',
    '.npmrc': 'NPM', '.yarnrc': 'Yarn',
    '.travis.yml': 'Travis CI', '.circleci': 'CircleCI',
    '.jenkinsfile': 'Jenkins', '.gitlab-ci.yml': 'GitLab CI',
}

class CodeAggregator:
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_bytes': 0,
            'files_by_type': {},
            'processing_time': 0
        }
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet."""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'
    
    def get_file_tree(self, directory: str, max_depth: int = 3) -> str:
        """Generate ASCII file tree structure."""
        tree = []
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, '').count(os.sep)
            if level > max_depth:
                continue
            
            indent = ' ' * 2 * level
            tree.append(f"{indent}📁 {os.path.basename(root)}/")
            
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # Show only first 10 files per directory
                ext = os.path.splitext(file)[1]
                icon = "📄" if ext in COMPLETE_EXTENSIONS else "📎"
                tree.append(f"{subindent}{icon} {file}")
            
            if len(files) > 10:
                tree.append(f"{subindent}... and {len(files) - 10} more files")
        
        return '\n'.join(tree)
    
    def traverse_and_write_code(self, source_dir: str, output_file: str, 
                               include_ext: List[str] = None,
                               exclude_ext: List[str] = None,
                               exclude_dirs: List[str] = None,
                               include_line_numbers: bool = False,
                               respect_gitignore: bool = False) -> Tuple[bool, str, Dict]:
        """Enhanced version with exact paths and all features."""
        
        # Reset stats
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_bytes': 0,
            'files_by_type': {},
            'processing_time': 0,
            'ignored_files': 0
        }
        
        start_time = time.time()
        
        # Default values
        if include_ext is None:
            include_ext = list(COMPLETE_EXTENSIONS.keys())
        if exclude_ext is None:
            exclude_ext = []
        if exclude_dirs is None:
            exclude_dirs = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        
        # Read .gitignore if requested
        gitignore_patterns = []
        if respect_gitignore:
            gitignore_path = os.path.join(source_dir, '.gitignore')
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r') as f:
                    gitignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        try:
            with open(output_file, 'w', encoding='utf-8') as txt_file:
                # Write header
                txt_file.write(f"Code Aggregator Export\n")
                txt_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                txt_file.write(f"Source Directory: {os.path.abspath(source_dir)}\n")
                txt_file.write("=" * 100 + "\n\n")
                
                # Traverse through all directories and files
                for root, dirs, files in os.walk(source_dir):
                    # Remove excluded directories
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_ext = os.path.splitext(file)[1].lower()
                        
                        # Skip files without extension
                        if not file_ext:
                            continue
                        
                        # Apply filters
                        if include_ext and file_ext not in include_ext:
                            continue
                        if exclude_ext and file_ext in exclude_ext:
                            continue
                        
                        # Skip binary files
                        mime_type = mimetypes.guess_type(file_path)[0]
                        if mime_type and not mime_type.startswith('text/'):
                            continue
                        
                        try:
                            # Get EXACT absolute path
                            abs_path = os.path.abspath(file_path)
                            
                            # Detect encoding
                            encoding = self.detect_encoding(file_path)
                            
                            # Read file content
                            with open(file_path, 'r', encoding=encoding, errors='ignore') as code_file:
                                content = code_file.read()
                            
                            # Skip if file is too large (> 5MB)
                            if len(content) > 5 * 1024 * 1024:
                                continue
                            
                            # Calculate line count (fix for f-string issue)
                            line_count = content.count('\n') + 1
                            
                            # Update statistics
                            self.stats['total_files'] += 1
                            self.stats['total_lines'] += line_count
                            self.stats['total_bytes'] += len(content.encode('utf-8'))
                            
                            # Count by file type
                            file_type = COMPLETE_EXTENSIONS.get(file_ext, 'Unknown')
                            self.stats['files_by_type'][file_type] = self.stats['files_by_type'].get(file_type, 0) + 1
                            
                            # Write to output file with EXACT path
                            txt_file.write(f"// FILE: {abs_path}\n")
                            txt_file.write(f"// TYPE: {file_type} | SIZE: {len(content):,} bytes | LINES: {line_count}\n")
                            txt_file.write("=" * 100 + "\n\n")
                            
                            # Add line numbers if requested
                            if include_line_numbers:
                                lines = content.split('\n')
                                numbered_content = '\n'.join(f"{i+1:4d} | {line}" for i, line in enumerate(lines))
                                txt_file.write(numbered_content)
                            else:
                                txt_file.write(content)
                            
                            txt_file.write("\n\n" + "=" * 100 + "\n\n")
                            
                        except Exception as e:
                            error_msg = f"// Error reading {file_path}: {str(e)[:100]}\n"
                            txt_file.write(error_msg)
                            txt_file.write("=" * 100 + "\n\n")
                            continue
            
            self.stats['processing_time'] = time.time() - start_time
            return True, output_file, self.stats
            
        except Exception as e:
            return False, str(e), self.stats
    
    def create_zip_archive(self, source_dir: str, output_zip: str, 
                          include_ext: List[str] = None) -> Tuple[bool, str]:
        """Create ZIP archive of all code files."""
        try:
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_ext = os.path.splitext(file)[1].lower()
                        if include_ext and file_ext not in include_ext:
                            continue
                        
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            return True, output_zip
        except Exception as e:
            return False, str(e)

def main():
    # Initialize aggregator
    aggregator = CodeAggregator()
    
    # Header
    st.markdown('<h1 class="main-header">🧬 Ultimate Code Aggregator</h1>', unsafe_allow_html=True)
    
    # Dark/Light mode toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        dark_mode = st.toggle("🌙 Dark Mode", value=False)
        if dark_mode:
            st.markdown('<style>[data-theme="dark"]</style>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File type selection
        st.subheader("📄 File Types")
        selected_categories = st.multiselect(
            "Select categories:",
            ["All Programming", "Web", "Config", "Scripts", "Documentation", "Custom"],
            default=["All Programming"]
        )
        
        # Custom extensions
        custom_ext = st.text_input(
            "Custom extensions (comma-separated):",
            placeholder=".txt,.log,.custom",
            help="Add custom file extensions not in the list"
        )
        
        # Features toggles
        st.subheader("✨ Features")
        include_line_numbers = st.checkbox("Include line numbers", value=False)
        respect_gitignore = st.checkbox("Respect .gitignore", value=True)
        create_zip = st.checkbox("Create ZIP archive", value=False)
        
        # Exclude directories
        exclude_dirs = st.text_area(
            "Directories to exclude (one per line):",
            value=".git\n__pycache__\nnode_modules\n.venv\nvenv\nbuild\ndist",
            height=100
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            max_file_size = st.slider("Max file size (MB)", 1, 100, 5)
            encoding_detection = st.checkbox("Auto-detect encoding", value=True)
        
        st.markdown("---")
        
        # Statistics display
        st.subheader("📊 File Type Coverage")
        st.write(f"**{len(COMPLETE_EXTENSIONS)}** file types supported")
        
        # Quick stats
        categories = {
            "Programming": ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'],
            "Web": ['.html', '.css', '.jsx', '.tsx', '.vue', '.svelte'],
            "Config": ['.json', '.yaml', '.toml', '.ini', '.xml'],
            "Data": ['.csv', '.sql', '.parquet'],
            "Docs": ['.md', '.txt', '.rst']
        }
        
        for cat, exts in categories.items():
            count = len([ext for ext in exts if ext in COMPLETE_EXTENSIONS])
            st.progress(count/len(exts), text=f"{cat}: {count}/{len(exts)}")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Process", "🔍 Preview", "📊 Statistics", "⚡ Batch"])
    
    with tab1:
        # Directory input
        st.subheader("Select Source Directory")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            source_dir = st.text_input(
                "Directory path:",
                placeholder="C:\\projects\\my-app or /home/user/projects",
                key="dir_input"
            )
        
        with col2:
            if st.button("Browse Current"):
                st.info(f"Current: {os.getcwd()}")
        
        # File tree preview
        if source_dir and os.path.exists(source_dir):
            with st.expander("📁 Directory Tree Preview"):
                file_tree = aggregator.get_file_tree(source_dir)
                st.code(file_tree, language="text")
        
        # Output options
        st.subheader("Output Settings")
        
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
                [".txt", ".md", ".html"]
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
                    include_extensions = list(COMPLETE_EXTENSIONS.keys())
                    
                    # Add custom extensions
                    if custom_ext:
                        custom_list = [ext.strip() for ext in custom_ext.split(',') if ext.strip()]
                        include_extensions.extend(custom_list)
                    
                    # Prepare output path
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"{output_name}_{timestamp}{output_format}"
                    output_path = os.path.join(os.getcwd(), output_filename)
                    
                    # Prepare exclude directories
                    exclude_list = [d.strip() for d in exclude_dirs.split('\n') if d.strip()]
                    
                    # Process
                    with st.spinner("Processing files..."):
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
                            respect_gitignore=respect_gitignore
                        )
                        
                        progress_bar.progress(100)
                        
                        if success:
                            # Success display
                            st.balloons()
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📄 Files Processed", stats['total_files'])
                            with col2:
                                st.metric("📏 Total Lines", f"{stats['total_lines']:,}")
                            with col3:
                                st.metric("⏱️ Time", f"{stats['processing_time']:.2f}s")
                            
                            # Download section
                            st.subheader("📥 Download Results")
                            
                            # Read output file
                            with open(output_path, 'r', encoding='utf-8') as f:
                                file_content = f.read()
                            
                            # Download buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label=f"⬇️ Download {output_format.upper()}",
                                    data=file_content,
                                    file_name=output_filename,
                                    mime="text/plain" if output_format == '.txt' else "text/html",
                                    use_container_width=True
                                )
                            
                            with col2:
                                # Create ZIP if requested
                                if create_zip:
                                    zip_path = output_path.replace(output_format, '.zip')
                                    zip_success, zip_result = aggregator.create_zip_archive(
                                        source_dir_clean, zip_path, include_extensions
                                    )
                                    if zip_success:
                                        with open(zip_path, 'rb') as zf:
                                            zip_data = zf.read()
                                        st.download_button(
                                            label="📦 Download ZIP",
                                            data=zip_data,
                                            file_name=os.path.basename(zip_path),
                                            mime="application/zip",
                                            use_container_width=True
                                        )
                            
                            # File info
                            with st.expander("📋 File Information", expanded=True):
                                st.info(f"**Location:** `{os.path.abspath(output_path)}`")
                                st.info(f"**Size:** {os.path.getsize(output_path):,} bytes")
                                
                                # File type distribution
                                if stats['files_by_type']:
                                    st.subheader("File Type Distribution")
                                    for file_type, count in sorted(stats['files_by_type'].items(), key=lambda x: x[1], reverse=True)[:10]:
                                        st.write(f"{file_type}: {count} files")
                        
                        else:
                            st.error(f"❌ Error: {result}")
    
    with tab2:
        st.subheader("🔍 File Preview")
        
        if 'output_path' in locals() and os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                preview_content = f.read(10000)
                
            st.code(preview_content, language='text')
            
            if len(preview_content) == 10000:
                st.caption("Showing first 10,000 characters. Use download for full file.")
        else:
            st.info("Process a directory first to see preview here.")
    
    with tab3:
        st.subheader("📊 Statistics Dashboard")
        
        # Placeholder for statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Extensions", len(COMPLETE_EXTENSIONS))
        with col2:
            st.metric("Text Files", sum(1 for ext in COMPLETE_EXTENSIONS.keys() if mimetypes.guess_type(f"test{ext}")[0] and 'text' in mimetypes.guess_type(f"test{ext}")[0]))
        with col3:
            st.metric("Config Files", len([ext for ext in COMPLETE_EXTENSIONS.keys() if ext in ['.json', '.yaml', '.toml', '.ini', '.xml', '.env']]))
        with col4:
            st.metric("Code Files", len([ext for ext in COMPLETE_EXTENSIONS.keys() if ext in ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']]))
        
        # File type chart
        st.subheader("File Type Categories")
        
        # Categorize extensions
        categories = {
            "Programming": [ext for ext, name in COMPLETE_EXTENSIONS.items() if any(x in name.lower() for x in ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'php'])],
            "Web": [ext for ext, name in COMPLETE_EXTENSIONS.items() if any(x in name.lower() for x in ['html', 'css', 'jsx', 'tsx', 'vue', 'svelte'])],
            "Config": [ext for ext, name in COMPLETE_EXTENSIONS.items() if any(x in name.lower() for x in ['json', 'yaml', 'toml', 'ini', 'config', 'xml'])],
            "Scripts": [ext for ext, name in COMPLETE_EXTENSIONS.items() if any(x in name.lower() for x in ['shell', 'bash', 'powershell', 'batch'])],
            "Data": [ext for ext, name in COMPLETE_EXTENSIONS.items() if any(x in name.lower() for x in ['csv', 'sql', 'excel', 'parquet'])],
            "Documentation": [ext for ext, name in COMPLETE_EXTENSIONS.items() if any(x in name.lower() for x in ['markdown', 'text', 'latex'])],
            "Other": [ext for ext, name in COMPLETE_EXTENSIONS.items() if not any(x in name.lower() for x in ['python', 'javascript', 'java', 'c++', 'html', 'css', 'json', 'yaml', 'shell', 'csv', 'markdown'])]
        }
        
        # Create DataFrame for chart
        chart_data = {
            'Category': list(categories.keys()),
            'Count': [len(exts) for exts in categories.values()]
        }
        
        st.bar_chart(chart_data, x='Category', y='Count')
    
    with tab4:
        st.subheader("⚡ Batch Processing")
        st.info("Batch processing feature coming soon!")
        
        # Multiple directories input
        batch_dirs = st.text_area(
            "Multiple directories (one per line):",
            height=150,
            placeholder="C:\\project1\nC:\\project2\n/home/user/project3"
        )
        
        if st.button("Process Batch", disabled=True):
            st.warning("Batch processing is under development!")

    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    with footer_col1:
        st.caption("🔄 Real-time processing")
    with footer_col2:
        st.caption("🔒 Local processing only")
    with footer_col3:
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()