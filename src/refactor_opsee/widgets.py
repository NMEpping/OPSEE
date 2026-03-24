from IPython.display import display, clear_output
import ipywidgets as widgets

from pathlib import Path
from ipyfilechooser import FileChooser

from datetime import datetime

from rocrate.rocrate import ROCrate
from rocrate.model import (Person,
                           Dataset,
                           RootDataset,
                           File,
                           ContextEntity)

class WidgetMeta:

    def __init__(self):
        self.widget = None

    def display(self):
        display(self.widget)


class OutputDirectorySection(WidgetMeta):
    """Encapsulates output directory selection with self-contained widgets and callbacks."""
    
    def __init__(self, working_dir: Path):
        """Initialize output directory section.
        
        Args:
            working_dir: Path to the working directory to start the file chooser in.
        """
        self.working_dir = working_dir
        self.fc = FileChooser(
            path=self.working_dir,
            filename='',  # Empty filename allows free navigation without conflicts
            title='<b>Select or create RO-Crate output directory:</b>',
            show_hidden=False,
            select_default=False,  # Don't pre-select to avoid conflicts
            dir_icon='📁',
            dir_icon_append=True
        )
        self.fc.use_dir_icons = True
        
        self.button_create = widgets.Button(
            description='Create Directory',
            button_style='info',
            icon='folder',
            layout=widgets.Layout(width='150px')
        )
        
        self.out_message = widgets.Output()
        self.button_create.on_click(self._on_create)
        self.widget = widgets.VBox([
            self.fc,
            self.button_create,
            self.out_message
        ])

    @property
    def output_directory(self):
        """Get the currently selected output directory path.
        
        Returns:
            str or None: The selected directory path, or None if no selection.
        """
        return self.fc.selected

    def _on_create(self, b):
        """Create output directory."""
        with self.out_message:
            clear_output()
            
            if not self.fc.selected:
                print("❌ Please select a directory using the file browser above")
                return
            
            try:
                crate_path = Path(self.fc.selected)
                crate_path.mkdir(parents=True, exist_ok=False)
                print(f"✅ RO-Crate directory created: {crate_path.absolute()}")
                
            except Exception as e:
                print(f"✗ Error creating directory: {str(e)}")
    
        self.widget = widgets.VBox([
                widgets.HTML("<h3>📂 Select RO-Crate Output Directory</h3>"),
                widgets.HTML("<p><strong style='color: #d73a49;'>⚠️ Start here!</strong> All files will be <strong>copied</strong> into this directory.</p>"),
                widgets.HTML("<p>💡 <em>Browse to select an existing folder or type a new folder name in the text box.</em></p>"),
                self.fc,
                self.button_create,
                self.out_message
            ])



class GeneralMetadataSection(WidgetMeta):
    """Encapsulates general metadata input with self-contained widgets and callbacks."""
    
    def __init__(self, ro_crate: ROCrate):
        """Initialize general metadata section.
        
        Args:
            ro_crate: ROCrate instance to store metadata
        """
        
        self.ro_crate = ro_crate

        self.w_name = widgets.Text(
            placeholder='e.g., Temperature Optimization Study',
            description='Crate Name:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px')
        )
        
        self.w_description = widgets.Textarea(
            placeholder='Detailed description of the study and experiments...',
            description='Description:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px', height='80px')
        )
        
        self.w_keywords = widgets.Text(
            placeholder='chemical engineering, FAIR, experimental data',
            description='Keywords:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px')
        )
        
        self.w_license = widgets.Dropdown(
            value='',
            options=['', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'CC0-1.0', 'MIT', 'Apache-2.0'],
            description='License:',
            style={'description_width': '150px'}
        )
        
        self.w_date_created = widgets.Text(
            value=datetime.now().strftime('%Y-%m-%d'),
            description='Date Created:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.button_save = widgets.Button(
            description='Save General Info',
            button_style='success',
            icon='check'
        )
        
        self.out_status = widgets.Output()
        self.button_save.on_click(self._on_save)
        self.widget = widgets.VBox([
            widgets.HTML("<h3>📝 General Metadata</h3>"),
            self.w_name,
            self.w_description,
            self.w_keywords,
            self.w_license,
            self.w_date_created,
            self.button_save,
            self.out_status
        ])

    def _on_save(self, b):
        """Save general metadata to crate_data."""
        with self.out_status:
            clear_output()
            self.set_general_metadata()
            print(f"✓ General metadata saved")
            print(f"  Crate: {self.w_name.value}")

        self.widget = widgets.VBox([
            widgets.HTML("<h3>📝 General Metadata</h3>"),
            self.w_name,
            self.w_description,
            self.w_keywords,
            self.w_license,
            self.w_date_created,
            self.button_save,
            self.out_status
        ])

    def set_general_metadata(self):

        name=self.w_name.value,
        description=self.w_description.value,
        keywords=[k.strip() for k in self.w_keywords.value.split(',') if k.strip()],
        license=self.w_license.value,
        date_created=self.w_date_created.value

        self.ro_crate.
        self.ro_crate.add()



class AuthorsSection(WidgetMeta):
    """Encapsulates author input with self-contained widgets and callbacks."""
    
    def __init__(self):
        """Initialize authors section.
        
        Args:
            crate_data: CrateData instance to store authors
        """
        
        self.w_name = widgets.Text(
            value='',
            placeholder='Jane Doe',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.w_orcid = widgets.Text(
            value='',
            placeholder='0000-0000-0000-0000',
            description='ORCID:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.w_affiliation = widgets.Text(
            value='',
            placeholder='University of Example',
            description='Affiliation:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.w_role = widgets.Dropdown(
            options=['Author', 'Contributor', 'DataCollector', 'DataCurator', 'ProjectLeader'],
            value='Author',
            description='Role:',
            style={'description_width': '120px'}
        )
        
        self.btn_add = widgets.Button(
            description='Add Author',
            button_style='primary',
            icon='plus'
        )
        
        self.out_status = widgets.Output()
        self.btn_add.on_click(self._on_add_author)
    
    def _on_add_author(self, b):
        """Add author to crate_data."""
        with self.out_status:
            if not self.w_name.value:
                print("⚠ Name is required")
                return
            
            self.crate_data.add_author(
                name=self.w_name.value,
                orcid=self.w_orcid.value,
                affiliation=self.w_affiliation.value,
                role=self.w_role.value
            )
            
            clear_output()
            print(f"✓ Added: {self.w_name.value} ({self.w_role.value})")
            print(f"  Total authors: {len(self.crate_data.authors)}")
            
            # Clear inputs
            self.w_name.value = ''
            self.w_orcid.value = ''
            self.w_affiliation.value = ''
    
    def render(self) -> widgets.VBox:
        """Render complete section."""
        return widgets.VBox([
            widgets.HTML("<h3>👥 Add Authors</h3>"),
            self.w_name,
            self.w_orcid,
            self.w_affiliation,
            self.w_role,
            self.btn_add,
            self.out_status
        ])