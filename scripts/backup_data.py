#!/usr/bin/env python3
"""
A2A System Data Backup Script
Backs up tasks and agent data
"""
import json
import os
from datetime import datetime
from pathlib import Path
import shutil
import zipfile

class A2ABackup:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Files to backup
        self.backup_files = [
            "shared/tasks.json",
            "shared/agent_tasks.json",
            "database/a2a_system.db",  # If using SQLite
        ]
        
    def create_backup(self):
        """Create a timestamped backup"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"a2a_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Create temporary backup directory
        backup_path.mkdir(exist_ok=True)
        
        # Copy files to backup
        backed_up_files = []
        for file_path in self.backup_files:
            source = self.base_dir / file_path
            if source.exists():
                dest_dir = backup_path / Path(file_path).parent
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest_dir)
                backed_up_files.append(file_path)
                print(f"✓ Backed up: {file_path}")
            else:
                print(f"⚠ Skipped (not found): {file_path}")
        
        # Create backup metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "files": backed_up_files,
            "version": "1.0"
        }
        
        with open(backup_path / "backup_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        # Create zip archive
        zip_path = self.backup_dir / f"{backup_name}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_path)
                    zipf.write(file_path, arcname)
        
        # Remove temporary directory
        shutil.rmtree(backup_path)
        
        print(f"\n✅ Backup created: {zip_path}")
        print(f"📦 Size: {zip_path.stat().st_size / 1024:.1f} KB")
        
        return zip_path
    
    def cleanup_old_backups(self, keep_count=10):
        """Keep only the most recent backups"""
        backups = sorted(self.backup_dir.glob("a2a_backup_*.zip"))
        
        if len(backups) > keep_count:
            to_delete = backups[:-keep_count]
            for backup in to_delete:
                backup.unlink()
                print(f"🗑 Deleted old backup: {backup.name}")
    
    def list_backups(self):
        """List all available backups"""
        backups = sorted(self.backup_dir.glob("a2a_backup_*.zip"))
        
        print("\n📁 Available Backups:")
        for backup in backups:
            size_kb = backup.stat().st_size / 1024
            print(f"  - {backup.name} ({size_kb:.1f} KB)")
        
        return backups
    
    def restore_backup(self, backup_file):
        """Restore from a backup file"""
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_file}")
            return False
        
        # Create restore directory
        restore_dir = self.base_dir / "restore_temp"
        restore_dir.mkdir(exist_ok=True)
        
        # Extract backup
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(restore_dir)
        
        # Read metadata
        metadata_file = restore_dir / "backup_metadata.json"
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        print(f"\n📅 Backup from: {metadata['timestamp']}")
        print("Files to restore:")
        for file in metadata['files']:
            print(f"  - {file}")
        
        # Note: Actual restoration would require confirmation
        # and proper handling of live data
        print("\n⚠️  To complete restoration, manually copy files from:")
        print(f"   {restore_dir}")
        
        return True

def main():
    backup = A2ABackup()
    
    # Create new backup
    backup.create_backup()
    
    # Cleanup old backups
    backup.cleanup_old_backups()
    
    # List all backups
    backup.list_backups()

if __name__ == "__main__":
    main()