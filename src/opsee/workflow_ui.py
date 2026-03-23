"""
Interactive workflow UI components and callbacks.

Provides reusable section classes for the OPSEE workflow notebook interface.
Each section encapsulates its widgets, callbacks, and display logic.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
from ipyfilechooser import FileChooser
import yaml

from .experiment import CrateData, Experiment


class OutputDirectorySection:
    """Encapsulates output directory selection with self-contained widgets and callbacks."""
    
    def __init__(self, crate_data: CrateData, default_name: str = 'my_rocrate', 
                 default_path: str = None):
        """Initialize output directory section.
        
        Args:
            crate_data: CrateData instance to store path
            default_name: Default directory name
            default_path: Default base path (defaults to cwd)
        """
        self.crate_data = crate_data
        self.default_path = default_path or os.getcwd()
        self.default_name = default_name
        
        # Create widgets
        self.fc = FileChooser(
            path=self.default_path,
            filename=default_name,
            title='<b>Select or create RO-Crate output directory:</b>',
            show_hidden=False,
            select_default=True,
            dir_icon='📁',
            dir_icon_append=True
        )
        self.fc.use_dir_icons = True
        
        self.btn_create = widgets.Button(
            description='Create Directory',
            button_style='info',
            icon='folder',
            layout=widgets.Layout(width='150px')
        )
        
        self.out_message = widgets.Output()
        self.btn_create.on_click(self._on_create)
    
    def _on_create(self, b):
        """Create output directory."""
        with self.out_message:
            clear_output()
            
            if not self.fc.selected:
                print("❌ Please select a directory using the file browser above")
                return
            
            try:
                crate_path = Path(self.fc.selected)
                crate_path.mkdir(parents=True, exist_ok=True)
                (crate_path / 'data' / 'engineering').mkdir(parents=True, exist_ok=True)
                (crate_path / 'data' / 'experiments').mkdir(parents=True, exist_ok=True)
                
                self.crate_data.set_output_directory(str(crate_path.absolute()))
                
                print(f"✅ RO-Crate directory created: {crate_path.absolute()}")
                print(f"\n📁 Directory structure:")
                print(f"  {crate_path.name}/")
                print(f"  ├── data/")
                print(f"  │   ├── engineering/")
                print(f"  │   └── experiments/")
                print(f"  └── ro-crate-metadata.json (will be created on export)")
                print(f"\n💡 All referenced files will be COPIED here automatically!")
                
            except Exception as e:
                print(f"✗ Error creating directory: {str(e)}")
    
    def render(self) -> widgets.VBox:
        """Render complete section with title and instructions."""
        return widgets.VBox([
            widgets.HTML("<h3>📂 Select RO-Crate Output Directory</h3>"),
            widgets.HTML("<p><strong style='color: #d73a49;'>⚠️ Start here!</strong> All files will be <strong>copied</strong> into this directory.</p>"),
            widgets.HTML("<p>💡 <em>Browse to select an existing folder or type a new folder name in the text box.</em></p>"),
            self.fc,
            self.btn_create,
            self.out_message
        ])


class GeneralMetadataSection:
    """Encapsulates general metadata input with self-contained widgets and callbacks."""
    
    def __init__(self, crate_data: CrateData, name: str = '', description: str = '',
                 keywords: str = '', license: str = 'CC-BY-4.0', date_created: str = None):
        """Initialize general metadata section.
        
        Args:
            crate_data: CrateData instance to store metadata
            name: Initial crate name
            description: Initial description
            keywords: Initial keywords (comma-separated)
            license: Initial license selection
            date_created: Initial date (defaults to today)
        """
        self.crate_data = crate_data
        
        self.w_name = widgets.Text(
            value=name,
            placeholder='e.g., Temperature Optimization Study',
            description='Crate Name:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px')
        )
        
        self.w_description = widgets.Textarea(
            value=description,
            placeholder='Detailed description of the study and experiments...',
            description='Description:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px', height='80px')
        )
        
        self.w_keywords = widgets.Text(
            value=keywords,
            placeholder='chemical engineering, FAIR, experimental data',
            description='Keywords:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px')
        )
        
        self.w_license = widgets.Dropdown(
            options=['CC-BY-4.0', 'CC-BY-SA-4.0', 'CC0-1.0', 'MIT', 'Apache-2.0'],
            value=license,
            description='License:',
            style={'description_width': '150px'}
        )
        
        self.w_date_created = widgets.Text(
            value=date_created or datetime.now().strftime('%Y-%m-%d'),
            description='Date Created:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.btn_save = widgets.Button(
            description='Save General Info',
            button_style='success',
            icon='check'
        )
        
        self.out_status = widgets.Output()
        self.btn_save.on_click(self._on_save)
    
    def _on_save(self, b):
        """Save general metadata to crate_data."""
        with self.out_status:
            clear_output()
            keywords = [k.strip() for k in self.w_keywords.value.split(',') if k.strip()]
            self.crate_data.set_general_metadata(
                name=self.w_name.value,
                description=self.w_description.value,
                keywords=keywords,
                license=self.w_license.value,
                date_created=self.w_date_created.value
            )
            print(f"✓ General metadata saved")
            print(f"  Crate: {self.w_name.value}")
    
    def render(self) -> widgets.VBox:
        """Render complete section."""
        return widgets.VBox([
            widgets.HTML("<h3>📝 General Metadata</h3>"),
            self.w_name,
            self.w_description,
            self.w_keywords,
            widgets.HBox([self.w_license, self.w_date_created]),
            self.btn_save,
            self.out_status
        ])


class AuthorsSection:
    """Encapsulates author input with self-contained widgets and callbacks."""
    
    def __init__(self, crate_data: CrateData):
        """Initialize authors section.
        
        Args:
            crate_data: CrateData instance to store authors
        """
        self.crate_data = crate_data
        
        self.w_name = widgets.Text(
            placeholder='Jane Doe',
            description='Name:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.w_orcid = widgets.Text(
            placeholder='0000-0000-0000-0000',
            description='ORCID:',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.w_affiliation = widgets.Text(
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


class DEXPISection:
    """Encapsulates DEXPI file loading with self-contained widgets and callbacks."""
    
    def __init__(self, crate_data: CrateData, default_path: str = None):
        """Initialize DEXPI section.
        
        Args:
            crate_data: CrateData instance to store DEXPI data
            default_path: Default directory for file browser
        """
        self.crate_data = crate_data
        default_path = default_path or os.path.join(os.getcwd(), 'example')
        
        self.fc = FileChooser(
            path=default_path,
            filename='C01V04-VER.EX01.xml',
            title='<b>Select DEXPI XML file:</b>',
            filter_pattern='*.xml',
            show_hidden=False,
            select_default=True
        )
        self.fc.use_dir_icons = True
        
        self.btn_load = widgets.Button(
            description='Load DEXPI',
            button_style='info',
            icon='upload',
            layout=widgets.Layout(width='120px')
        )
        
        self.out_status = widgets.Output()
        self.btn_load.on_click(self._on_load)
    
    def _on_load(self, b):
        """Load DEXPI file."""
        with self.out_status:
            clear_output()
            try:
                from pydexpi.loaders import ProteusSerializer
                from .dexpi_extraction import extract_equipment, extract_instruments
                
                if not self.fc.selected:
                    print("❌ Please select a DEXPI XML file")
                    return
                
                dexpi_file = Path(self.fc.selected)
                if not dexpi_file.exists():
                    print(f"❌ File not found: {dexpi_file}")
                    return
                
                loader = ProteusSerializer()
                dexpi_model = loader.load(str(dexpi_file.parent), dexpi_file.name)
                
                equipment = extract_equipment(dexpi_model)
                instruments = extract_instruments(dexpi_model)
                
                self.crate_data.set_dexpi(
                    path=str(dexpi_file.absolute()),
                    equipment=equipment,
                    instruments=instruments
                )
                
                print(f"✅ DEXPI loaded: {dexpi_file.name}")
                print(f"   Equipment items: {len(equipment)}")
                print(f"   Instruments: {len(instruments)}")
                
                if equipment:
                    print("\n   Sample equipment:")
                    for eq in list(equipment.values())[:5]:
                        print(f"     • {eq['tag_name']}: {eq['type']}")
                
                if instruments:
                    print("\n   Sample instruments:")
                    for inst in list(instruments.values())[:5]:
                        print(f"     • {inst['tag_name']}: {inst.get('description', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Error loading DEXPI: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def render(self) -> widgets.VBox:
        """Render complete section."""
        return widgets.VBox([
            widgets.HTML("<h3>🔧 Load DEXPI P&ID</h3>"),
            widgets.HTML("<p>Select a DEXPI XML file to extract equipment and instrument metadata.</p>"),
            self.fc,
            self.btn_load,
            self.out_status
        ])


class ExperimentConfigSection:
    """Encapsulates experiment configuration with self-contained widgets and callbacks."""
    
    def __init__(self, crate_data: CrateData, default_path: str = None, 
                 exp_id: str = 'exp_1', exp_name: str = ''):
        """Initialize experiment configuration section.
        
        Args:
            crate_data: CrateData instance to store experiments
            default_path: Default directory for file browser
            exp_id: Initial experiment ID
            exp_name: Initial experiment name
        """
        self.crate_data = crate_data
        default_path = default_path or os.path.join(os.getcwd(), 'templates')
        self.current_experiment = None
        
        self.w_exp_id = widgets.Text(
            value=exp_id,
            placeholder='exp_1',
            description='Experiment ID:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='400px')
        )
        
        self.w_exp_name = widgets.Text(
            value=exp_name,
            placeholder='Baseline Experiment',
            description='Experiment Name:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px')
        )
        
        self.fc_params = FileChooser(
            path=default_path,
            filename='experiment_parameters.yaml',
            title='<b>Select experiment parameters YAML file:</b>',
            filter_pattern='*.yaml',
            show_hidden=False,
            select_default=True
        )
        self.fc_params.use_dir_icons = True
        
        self.btn_load_params = widgets.Button(
            description='Load Parameters',
            button_style='info',
            icon='upload'
        )
        
        self.out_status = widgets.Output()
        self.btn_load_params.on_click(self._on_load)
    
    def _on_load(self, b):
        """Load experiment parameters."""
        with self.out_status:
            clear_output()
            try:
                if not self.fc_params.selected:
                    print("⚠ Please select a parameters file")
                    return
                
                params_path = Path(self.fc_params.selected)
                if not params_path.exists():
                    print(f"⚠ File not found: {params_path}")
                    return
                
                with open(params_path, 'r') as f:
                    params = yaml.safe_load(f)
                
                self.current_experiment = self.crate_data.add_experiment(self.w_exp_id.value)
                self.current_experiment.experimental_parameters = params
                
                print(f"✓ Parameters loaded for {self.w_exp_id.value}")
                if params.get('experiment'):
                    print(f"  Experiment: {params['experiment'].get('title', 'N/A')}")
                if params.get('conditions'):
                    print(f"  Conditions: {len(params['conditions'])} parameters")
                
            except Exception as e:
                print(f"✗ Error loading parameters: {str(e)}")
    
    def render(self) -> widgets.VBox:
        """Render complete section."""
        return widgets.VBox([
            widgets.HTML("<h3>🧪 Experiment Configuration</h3>"),
            self.w_exp_id,
            self.w_exp_name,
            widgets.HTML("<p><strong>Select experiment parameters file:</strong></p>"),
            self.fc_params,
            self.btn_load_params,
            self.out_status
        ])


class WorkflowUI:
    """Manages OPSEE workflow UI sections.
    
    Provides factory methods that return self-contained section objects.
    Each section encapsulates its widgets and callbacks.
    """
    
    def __init__(self, crate_data: CrateData):
        """Initialize UI manager with crate data store.
        
        Args:
            crate_data: CrateData instance to store metadata
        """
        self.crate_data = crate_data
        self.current_experiment: Experiment = None
    
    # ========================================================================
    # Section factory methods
    # ========================================================================
    
    def get_output_directory_section(self, default_name: str = 'my_rocrate',
                                     default_path: str = None) -> OutputDirectorySection:
        """Create output directory section.
        
        Args:
            default_name: Default directory name
            default_path: Default base path
        
        Returns:
            OutputDirectorySection instance
        """
        return OutputDirectorySection(self.crate_data, default_name, default_path)
    
    def get_general_metadata_section(self, name: str = '', description: str = '',
                                     keywords: str = '', license: str = 'CC-BY-4.0',
                                     date_created: str = None) -> GeneralMetadataSection:
        """Create general metadata section.
        
        Args:
            name: Initial crate name
            description: Initial description
            keywords: Initial keywords
            license: Initial license
            date_created: Initial date
        
        Returns:
            GeneralMetadataSection instance
        """
        return GeneralMetadataSection(self.crate_data, name, description, keywords, 
                                     license, date_created)
    
    def get_authors_section(self) -> AuthorsSection:
        """Create authors section.
        
        Returns:
            AuthorsSection instance
        """
        return AuthorsSection(self.crate_data)
    
    def get_dexpi_section(self, default_path: str = None) -> DEXPISection:
        """Create DEXPI section.
        
        Args:
            default_path: Default directory for file browser
        
        Returns:
            DEXPISection instance
        """
        return DEXPISection(self.crate_data, default_path)
    
    def get_experiment_config_section(self, default_path: str = None,
                                      exp_id: str = 'exp_1',
                                      exp_name: str = '') -> ExperimentConfigSection:
        """Create experiment configuration section.
        
        Args:
            default_path: Default directory for file browser
            exp_id: Initial experiment ID
            exp_name: Initial experiment name
        
        Returns:
            ExperimentConfigSection instance
        """
        section = ExperimentConfigSection(self.crate_data, default_path, exp_id, exp_name)
        # Keep current_experiment in sync
        section.current_experiment = self.current_experiment
        return section
    
    # ========================================================================
    # Helper methods
    # ========================================================================
    
    def get_instrument_options(self) -> List[Tuple[str, str]]:
        """Get available instruments from DEXPI.
        
        Returns:
            List of (label, id) tuples
        """
        if not self.crate_data.dexpi or not self.crate_data.dexpi.get('instruments'):
            return [('Load DEXPI first', None)]
        
        options = []
        for inst_id, inst_data in self.crate_data.dexpi['instruments'].items():
            label = f"{inst_data['tag_name']} - {inst_data.get('description', 'N/A')}"
            options.append((label, inst_id))
        return options
    
    def get_equipment_options(self) -> List[Tuple[str, str]]:
        """Get available equipment from DEXPI.
        
        Returns:
            List of (label, id) tuples
        """
        if not self.crate_data.dexpi or not self.crate_data.dexpi.get('equipment'):
            return [('Load DEXPI first', None)]
        
        options = []
        for eq_id, eq_data in self.crate_data.dexpi['equipment'].items():
            label = f"{eq_data['tag_name']} - {eq_data.get('type', 'N/A')}"
            options.append((label, eq_id))
        return options
