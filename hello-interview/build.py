#!/usr/bin/env python3
import subprocess
import re
import shutil
from pathlib import Path

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

    def get_chapter_files(self, section_dir):
        """Get all markdown files from a section directory in order."""
        return sorted(section_dir.glob('*.md'))

    def get_image_files(self, section_dir):
        """Get all image files from a section directory."""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}
        return [f for f in section_dir.iterdir() if f.suffix.lower() in image_extensions]

    def copy_images(self, section_dir, temp_section_dir):
        """Copy images to temporary directory."""
        for image_file in self.get_image_files(section_dir):
            shutil.copy2(image_file, temp_section_dir)

    def copy_and_adjust_chapter(self, chapter_file, temp_section_dir):
        """Copy chapter file and ensure image paths are correct."""
        # Read the original content
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Write to new location in temp directory
        temp_chapter_file = temp_section_dir / chapter_file.name
        with open(temp_chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return temp_chapter_file

    def extract_title(self, md_file):
        """Extract title from markdown file's first heading."""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if match:
                    return match.group(1).strip()
                
                filename = md_file.stem
                clean_name = re.sub(r'^\d+-', '', filename)
                return clean_name.replace('-', ' ').title()
        except Exception as e:
            print(f"Warning: Could not extract title from {md_file}: {e}")
            return md_file.stem

    def get_section_title(self, section_dir):
        """Extract section title from directory name."""
        clean_name = re.sub(r'^\d+-', '', section_dir.name)
        return clean_name.replace('-', ' ').title()

    def generate_toc(self):
        """Generate table of contents markdown file."""
        toc_content = ["# Table of Contents\n"]
        
        for section_dir in self.get_section_dirs():
            section_title = self.get_section_title(section_dir)
            toc_content.append(f"\n## {section_title}\n")
            
            temp_section_dir = self.temp_dir / section_dir.name
            for chapter_file in self.get_chapter_files(section_dir):
                chapter_title = self.extract_title(chapter_file)
                relative_path = (temp_section_dir / chapter_file.name).relative_to(self.temp_dir)
                toc_content.append(f"- [{chapter_title}]({relative_path})")

        with open(self.temp_toc_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(toc_content))

        return self.temp_toc_file

    def prepare_temp_directory(self):
        """Prepare temporary directory with all necessary files."""
        self.cleanup_temp_dir()
        self.create_directories()
        
        temp_files = []
        
        # Process each section
        for section_dir in self.get_section_dirs():
            temp_section_dir = self.temp_dir / section_dir.name
            temp_section_dir.mkdir(exist_ok=True)
            
            # Copy images first
            self.copy_images(section_dir, temp_section_dir)
            
            # Process chapters
            for chapter_file in self.get_chapter_files(section_dir):
                temp_chapter = self.copy_and_adjust_chapter(chapter_file, temp_section_dir)
                temp_files.append(temp_chapter)
        
        return temp_files

    def build_epub(self):
        """Build epub file using pandoc."""
        try:
            # Prepare all files in temporary directory
            content_files = self.prepare_temp_directory()

            toc_file = self.generate_toc()
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
                str(toc_file)
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
            
            # Print structure information
            print("\n📚 Book Structure:")
            for section_dir in self.get_section_dirs():
                section_title = self.get_section_title(section_dir)
                print(f"\n📑 Section: {section_title}")
                for chapter in self.get_chapter_files(section_dir):
                    chapter_title = self.extract_title(chapter)
                    print(f"  📄 {chapter_title}")
                images = self.get_image_files(section_dir)
                if images:
                    print(f"  🖼️ Images: {', '.join(img.name for img in images)}")
            
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