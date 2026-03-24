from rocrate.rocrate import ROCrate
from pathlib import Path
from .widgets import OutputDirectorySection, GeneralMetadataSection, AuthorsSection

class Ui():
    """
    User interface for OPSEE, built using ipywidgets.
    Provides interactive widgets for file selection, validation, and RO-Crate generation.
    """

    def __init__(self, working_dir: Path = Path.cwd()):
        self.ro_crate = ROCrate()
        self.output_directory_section = OutputDirectorySection(working_dir)
        self.general_metadata_section = GeneralMetadataSection(self.ro_crate)
        self.general_metadata_authors_section = AuthorsSection()

    def write_crate(self, rm_dir_before_write: bool = False):
        """Write the RO-Crate to the specified destination path."""
        try:
            self.output_directory = self.output_directory_section.output_directory
            if rm_dir_before_write and self.output_directory.exists():
                self.output_directory.rmdir()
            self.output_directory.mkdir(parents=True, exist_ok=True)
            self.ro_crate.write(self.output_directory)
            print(f"✅ RO-Crate successfully written to: {self.output_directory}")
        except Exception as e:
            print(f"❌ Error writing RO-Crate: {e}")