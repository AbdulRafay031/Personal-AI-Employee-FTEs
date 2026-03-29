"""
File System Watcher Module

Monitors a drop folder for new files and creates action files
in the Needs_Action folder for Claude Code to process.

This is a simple but powerful watcher that allows users to:
- Drop files into a folder for processing
- Automatically categorize based on file type/name
- Create structured action files with metadata

Usage:
    python filesystem_watcher.py /path/to/vault --watch-folder /path/to/drop
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Watchdog imports (install: pip install watchdog)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Watchdog not installed. Run: pip install watchdog")


class DropFolderHandler(FileSystemEventHandler):
    """
    Handles file system events in the drop folder.
    
    When a new file is created, it:
    1. Copies the file to the vault
    2. Creates a metadata action file in Needs_Action
    """
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
        self.processed_files: set = set()
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        source_path = Path(event.src_path)
        
        # Skip temporary files
        if source_path.name.startswith('~') or source_path.name.startswith('.'):
            return
        
        # Skip already processed files
        file_hash = self._hash_file(source_path)
        if file_hash in self.processed_files:
            return
        
        self.logger.info(f'New file detected: {source_path.name}')
        self.watcher.process_file(source_path, file_hash)
    
    def _hash_file(self, path: Path) -> str:
        """Generate a hash for the file to track duplicates."""
        try:
            hasher = hashlib.md5()
            with open(path, 'rb') as f:
                hasher.update(f.read(8192))
            return hasher.hexdigest()
        except Exception:
            return str(path)


class FileSystemWatcher(BaseWatcher):
    """
    Watches a drop folder for new files.
    
    When files are added, creates action files with:
    - File metadata (size, type, creation date)
    - Content preview (for text files)
    - Suggested actions based on file type
    """
    
    # File type categories
    FILE_CATEGORIES = {
        'invoice': ['invoice', 'bill', 'receipt', 'payment'],
        'contract': ['contract', 'agreement', 'nda', 'proposal'],
        'report': ['report', 'summary', 'analysis', 'statement'],
        'image': ['image', 'photo', 'screenshot', 'scan'],
        'data': ['csv', 'json', 'xml', 'excel', 'spreadsheet'],
    }
    
    # Supported text extensions for preview
    TEXT_EXTENSIONS = ['.txt', '.md', '.json', '.xml', '.csv', '.py', '.js', '.html']
    
    def __init__(self, vault_path: str, watch_folder: str, check_interval: int = 30):
        """
        Initialize File System Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            watch_folder: Path to folder to monitor
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        self.watch_folder = Path(watch_folder)
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        # Create processed files tracker
        self.processed_hashes_file = self.vault_path / '.processed_files'
        self.processed_hashes: set = set()
        self._load_processed_hashes()
        
        # Setup watchdog if available
        if WATCHDOG_AVAILABLE:
            self.observer = Observer()
            self.handler = DropFolderHandler(self)
            self.observer.schedule(self.handler, str(self.watch_folder), recursive=False)
        else:
            self.observer = None
    
    def _load_processed_hashes(self):
        """Load previously processed file hashes."""
        if self.processed_hashes_file.exists():
            try:
                self.processed_hashes = set(
                    self.processed_hashes_file.read_text().splitlines()
                )
            except Exception:
                self.processed_hashes = set()
    
    def _save_processed_hashes(self):
        """Save processed file hashes to disk."""
        try:
            # Keep only last 1000 hashes
            if len(self.processed_hashes) > 1000:
                self.processed_hashes = set(list(self.processed_hashes)[-500:])
            self.processed_hashes_file.write_text('\n'.join(self.processed_hashes))
        except Exception as e:
            self.logger.error(f'Failed to save processed hashes: {e}')
    
    def _hash_file(self, path: Path) -> str:
        """Generate MD5 hash for file tracking."""
        try:
            hasher = hashlib.md5()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return str(path)
    
    def _categorize_file(self, path: Path) -> str:
        """Determine file category based on name and extension."""
        name_lower = path.name.lower()
        suffix = path.suffix.lower()
        
        # Check name patterns
        for category, keywords in self.FILE_CATEGORIES.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        
        # Check by extension
        if suffix in ['.jpg', '.jpeg', '.png', '.gif', '.pdf']:
            return 'image'
        elif suffix in ['.csv', '.json', '.xml', '.xlsx', '.xls']:
            return 'data'
        elif suffix in ['.txt', '.md', '.doc', '.docx']:
            return 'document'
        elif suffix in ['.py', '.js', '.html', '.css']:
            return 'code'
        
        return 'general'
    
    def _get_text_preview(self, path: Path, max_lines: int = 50) -> Optional[str]:
        """Get text preview for supported file types."""
        if path.suffix.lower() not in self.TEXT_EXTENSIONS:
            return None
        
        try:
            content = path.read_text(encoding='utf-8', errors='replace')
            lines = content.splitlines()[:max_lines]
            preview = '\n'.join(lines)
            
            if len(content.splitlines()) > max_lines:
                preview += '\n... [truncated]'
            
            return preview
        except Exception:
            return None
    
    def _generate_suggested_actions(self, category: str, path: Path) -> List[str]:
        """Generate suggested actions based on file category."""
        actions = []
        
        if category == 'invoice':
            actions.append('- [ ] Extract invoice details (vendor, amount, due date)')
            actions.append('- [ ] Log to /Accounting/Current_Month.md')
            actions.append('- [ ] Schedule payment if approval required')
        elif category == 'contract':
            actions.append('- [ ] Review contract terms')
            actions.append('- [ ] Extract key dates and obligations')
            actions.append('- [ ] Create follow-up tasks')
        elif category == 'report':
            actions.append('- [ ] Read and summarize key findings')
            actions.append('- [ ] Flag action items')
        elif category == 'image':
            actions.append('- [ ] Review image content')
            actions.append('- [ ] Add to appropriate project folder')
        elif category == 'data':
            actions.append('- [ ] Analyze data content')
            actions.append('- [ ] Import to tracking system if needed')
        else:
            actions.append('- [ ] Review file content')
            actions.append('- [ ] Determine appropriate action')
        
        actions.append('- [ ] Archive file after processing')
        
        return actions
    
    def process_file(self, source_path: Path, file_hash: str):
        """
        Process a newly detected file.
        
        Args:
            source_path: Path to the new file
            file_hash: MD5 hash of the file
        """
        try:
            # Copy file to vault inbox
            dest_path = self.inbox / source_path.name
            
            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                dest_path = self.inbox / f'{stem}_{counter}{suffix}'
                counter += 1
            
            shutil.copy2(source_path, dest_path)
            self.logger.info(f'Copied file to vault: {dest_path.name}')
            
            # Create action file
            self.create_action_file({
                'source': source_path,
                'destination': dest_path,
                'hash': file_hash
            })
            
            # Mark as processed
            self.processed_hashes.add(file_hash)
            self._save_processed_hashes()
            
        except Exception as e:
            self.logger.error(f'Failed to process file: {e}')
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for new files in watch folder (fallback method).
        
        When using watchdog, this is not needed as events trigger processing.
        This method is used for initial scan or if watchdog is unavailable.
        
        Returns:
            Empty list (files are processed directly in event handler)
        """
        # Initial scan for existing files
        if not hasattr(self, '_initial_scan_done'):
            self._initial_scan_done = True
            for file_path in self.watch_folder.iterdir():
                if file_path.is_file():
                    file_hash = self._hash_file(file_path)
                    if file_hash not in self.processed_hashes:
                        self.process_file(file_path, file_hash)
        
        return []
    
    def create_action_file(self, file_info: Dict) -> Optional[Path]:
        """
        Create action file for a dropped file.
        
        Args:
            file_info: Dict with source, destination, and hash
            
        Returns:
            Path to created file
        """
        source = file_info['source']
        dest = file_info['destination']
        
        category = self._categorize_file(source)
        priority = 'high' if category in ['invoice', 'contract'] else 'medium'
        
        # Get file metadata
        stat = source.stat()
        size_kb = stat.st_size / 1024
        
        # Get text preview if available
        preview = self._get_text_preview(source)
        
        # Generate suggested actions
        actions = self._generate_suggested_actions(category, source)
        
        # Create content
        content = f'''{self.generate_frontmatter(
            item_type='file_drop',
            category=category,
            original_name=f'"{source.name}"',
            file_size=f'{size_kb:.1f} KB',
            priority=priority
        )}

## File Details

| Field | Value |
|-------|-------|
| **Original Name** | {source.name} |
| **Category** | {category} |
| **Size** | {size_kb:.1f} KB |
| **Created** | {datetime.fromtimestamp(stat.st_ctime).isoformat()} |
| **Modified** | {datetime.fromtimestamp(stat.st_mtime).isoformat()} |
| **Vault Location** | `/Inbox/{dest.name}` |

---

## File Preview

```
{preview if preview else '[Preview not available for this file type]'}
```

---

## Suggested Actions

{chr(10).join(actions)}

---

## Notes

```
Add processing notes here...
```
'''
        
        # Generate filename
        filename = f"FILE_{self.sanitize_filename(source.name)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        filepath = self.needs_action / filename
        
        try:
            filepath.write_text(content, encoding='utf-8')
            self.logger.info(f'Created action file: {filename}')
            return filepath
        except Exception as e:
            self.logger.error(f'Failed to create action file: {e}')
            return None
    
    def run(self):
        """
        Main run loop with watchdog support.
        """
        if WATCHDOG_AVAILABLE and self.observer:
            self.logger.info(f'Starting FileSystemWatcher with watchdog')
            self.observer.start()
            
            # Do initial scan
            self.check_for_updates()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info('FileSystemWatcher stopped by user')
                self.observer.stop()
            self.observer.join()
        else:
            # Fallback to polling
            self.logger.info('Starting FileSystemWatcher in polling mode (watchdog not available)')
            super().run()


# Import time for fallback mode
import time


def main():
    """Main entry point for File System Watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--watch-folder', required=True, help='Folder to monitor')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    
    args = parser.parse_args()
    
    watcher = FileSystemWatcher(args.vault_path, args.watch_folder, args.interval)
    watcher.run()


if __name__ == '__main__':
    main()
