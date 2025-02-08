#!/usr/bin/env python3
import subprocess
import shutil
from pathlib import Path

image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}

class EpubBuilder:
    def __init__(self):
        self.project_dir = Path('.')
        self.content_dir = self.project_dir / 'content'
        self.output_dir = self.project_dir / 'output'
        self.temp_dir = self.output_dir / 'temp'
        
        # Try both .yaml and .yml extensions for metadata
        yaml_file = self.project_dir / 'metadata.yaml'
        yml_file = self.project_dir / 'metadata.yml'
        self.metadata_file = yml_file if yml_file.exists() else yaml_file
        
        self.css_file = self.project_dir / 'style.css'
        self.temp_toc_file = self.temp_dir / 'generated_toc.md'

    def create_directories(self):
        """Create necessary directories."""
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

    def cleanup_temp_dir(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def get_section_dirs(self):
        """Get all section directories in sorted order."""
        return sorted(d for d in self.content_dir.iterdir() if d.is_dir())

    def copy_images(self, section_dir, temp_section_dir):
        """Copy images to temporary directory."""
        image_files = [f for f in section_dir.iterdir() if f.suffix.lower() in image_extensions]
        for image_file in image_files:
            shutil.copy2(image_file, temp_section_dir)

    def prepare_temp_directory(self):
        """Prepare temporary directory with all necessary files."""
        self.cleanup_temp_dir()
        self.create_directories()
        
        temp_files = []

        def handle(file, parent_temp_dir):
            print(f"Handling {file} {file.is_file()}")
            if file.is_file():
                temp_file = parent_temp_dir / file.name
                shutil.copy2(file, temp_file)
                temp_files.append(temp_file)
            else:
                temp_subdir = parent_temp_dir / file.name
                temp_subdir.mkdir(exist_ok=True)
                self.copy_images(file, temp_subdir)
                sub_sections = sorted(f for f in file.iterdir() if f.is_dir() or f.suffix.lower() == '.md')
                for subfile in sub_sections:
                    # Recursively handle subdirectories
                    handle(subfile, temp_subdir)
        
        # Process each section
        for section_dir in self.get_section_dirs():
            handle(section_dir, self.temp_dir)
        
        return temp_files

    def build_epub(self):
        """Build epub file using pandoc."""
        try:
            # Prepare all files in temporary directory
            content_files = self.prepare_temp_directory()

            # Prepare pandoc command
            cmd = [
                'pandoc',
                '-f', 'markdown+smart',
                '-t', 'epub3',
                '--toc',
                '--toc-depth=3',
                '--resource-path', ":".join(str(f.parent) for f in content_files),  # Add resource path
                '-o', str(self.output_dir / 'book.epub'),
                str(self.metadata_file),
            ]

            # Add all content files to command
            cmd.extend(str(f) for f in content_files)
            
            # Add CSS if exists
            if self.css_file.exists():
                cmd.extend(['--css', str(self.css_file)])

            # Run pandoc command
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            print("✅ Successfully built epub!")

            # Cleanup
            self.cleanup_temp_dir()
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Error building epub: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            self.cleanup_temp_dir()
            return False

if __name__ == "__main__":
    builder = EpubBuilder()
    builder.build_epub()