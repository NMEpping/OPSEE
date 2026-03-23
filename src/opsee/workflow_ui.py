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
    
    def __init__(self, crate_data: CrateData, ui_manager: 'WorkflowUI', 
                 default_path: str = None, exp_id: str = 'exp_1', exp_name: str = ''):
        """Initialize experiment configuration section.
        
        Args:
            crate_data: CrateData instance to store experiments
            ui_manager: WorkflowUI instance to update current_experiment
            default_path: Default directory for file browser
            exp_id: Initial experiment ID
            exp_name: Initial experiment name
        """
        self.crate_data = crate_data
        self.ui_manager = ui_manager
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
                
                # Update WorkflowUI's current_experiment so other sections can access it
                self.ui_manager.current_experiment = self.current_experiment
                
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


class AnalyticalDataFilesSection:
    """Encapsulates analytical data file management."""
    
    def __init__(self, crate_data: CrateData, ui: 'WorkflowUI'):
        """Initialize analytical data files section.
        
        Args:
            crate_data: CrateData instance
            ui: WorkflowUI instance for accessing DEXPI options
        """
        self.crate_data = crate_data
        self.ui = ui
        
        self.fc = FileChooser(
            path=os.path.join(os.getcwd(), 'example'),
            title='<b>Select data file:</b>',
            show_hidden=False
        )
        self.fc.use_dir_icons = True
        
        self.w_instrument = widgets.Dropdown(
            options=ui.get_instrument_options(),
            description='Instrument:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px')
        )
        
        self.w_data_type = widgets.Dropdown(
            options=['RawData', 'ProcessedData', 'CalibrationData', 'DerivedData'],
            value='RawData',
            description='Data Type:',
            style={'description_width': '150px'}
        )
        
        self.w_description = widgets.Textarea(
            placeholder='Description of the data file...',
            description='Description:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='700px', height='80px')
        )
        
        self.btn_add = widgets.Button(
            description='Add Data File',
            button_style='success',
            icon='plus',
            layout=widgets.Layout(width='130px')
        )
        
        self.btn_refresh = widgets.Button(
            description='Refresh Instruments',
            button_style='warning',
            icon='refresh',
            layout=widgets.Layout(width='160px')
        )
        
        self.out_status = widgets.Output()
        self.btn_add.on_click(self._on_add)
        self.btn_refresh.on_click(self._on_refresh)
    
    def _on_refresh(self, b):
        with self.out_status:
            clear_output(wait=True)
            self.w_instrument.options = self.ui.get_instrument_options()
            print("✅ Instrument list refreshed from shared DEXPI")
    
    def _on_add(self, b):
        with self.out_status:
            clear_output()
            
            if not self.fc.selected:
                print("❌ Please select a data file using the file browser above")
                return
            
            if not self.w_instrument.value:
                print("❌ Please select an instrument (load DEXPI first)")
                return
            
            if self.ui.current_experiment is None:
                print("❌ Please load experiment parameters first")
                return
            
            self.ui.current_experiment.add_analytical_file(
                path=self.fc.selected,
                instrument_id=self.w_instrument.value,
                data_type=self.w_data_type.value,
                description=self.w_description.value
            )
            
            print(f"✅ Added data file: {Path(self.fc.selected).name}")
            print(f"   Total files: {len(self.ui.current_experiment.analytical_files)}")
            
            self.fc.reset()
            self.w_description.value = ''
    
    def render(self) -> widgets.VBox:
        return widgets.VBox([
            widgets.HTML("<h4>Analytical Data Files</h4>"),
            widgets.HTML("<p>💡 <em>Browse to select data files - they will be copied into the RO-Crate.</em></p>"),
            self.fc,
            self.w_instrument,
            self.w_data_type,
            self.w_description,
            widgets.HBox([self.btn_add, self.btn_refresh]),
            self.out_status
        ])


class EngineeringAssetsSection:
    """Encapsulates engineering assets management."""
    
    def __init__(self, crate_data: CrateData, ui: 'WorkflowUI'):
        """Initialize engineering assets section.
        
        Args:
            crate_data: CrateData instance
            ui: WorkflowUI instance for accessing DEXPI options
        """
        self.crate_data = crate_data
        self.ui = ui
        
        self.fc = FileChooser(
            path=os.path.join(os.getcwd(), 'example'),
            title='<b>Select engineering asset file:</b>',
            show_hidden=False
        )
        self.fc.use_dir_icons = True
        
        self.w_equipment = widgets.Dropdown(
            options=ui.get_equipment_options(),
            description='Equipment:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='600px')
        )
        
        self.w_asset_type = widgets.Dropdown(
            options=['CADModel', 'TechnicalDrawing', 'GeometryFile', 'Specification', 'Photo'],
            value='Photo',
            description='Asset Type:',
            style={'description_width': '150px'}
        )
        
        self.w_description = widgets.Textarea(
            placeholder='Description of the engineering asset...',
            description='Description:',
            style={'description_width': '150px'},
            layout=widgets.Layout(width='700px', height='80px')
        )
        
        self.btn_add = widgets.Button(
            description='Add Asset',
            button_style='success',
            icon='plus',
            layout=widgets.Layout(width='120px')
        )
        
        self.btn_refresh = widgets.Button(
            description='Refresh Equipment',
            button_style='warning',
            icon='refresh',
            layout=widgets.Layout(width='160px')
        )
        
        self.out_status = widgets.Output()
        self.btn_add.on_click(self._on_add)
        self.btn_refresh.on_click(self._on_refresh)
    
    def _on_refresh(self, b):
        with self.out_status:
            clear_output(wait=True)
            self.w_equipment.options = self.ui.get_equipment_options()
            print("✅ Equipment list refreshed from shared DEXPI")
    
    def _on_add(self, b):
        with self.out_status:
            clear_output()
            
            if not self.fc.selected:
                print("❌ Please select an asset file using the file browser above")
                return
            
            if not self.w_equipment.value:
                print("❌ Please select equipment (load DEXPI first)")
                return
            
            if self.ui.current_experiment is None:
                print("❌ Please load experiment parameters first")
                return
            
            self.ui.current_experiment.add_engineering_asset(
                path=self.fc.selected,
                equipment_id=self.w_equipment.value,
                asset_type=self.w_asset_type.value,
                description=self.w_description.value
            )
            
            print(f"✅ Added engineering asset: {Path(self.fc.selected).name}")
            print(f"   Total assets: {len(self.ui.current_experiment.engineering_assets)}")
            
            self.fc.reset()
            self.w_description.value = ''
    
    def render(self) -> widgets.VBox:
        return widgets.VBox([
            widgets.HTML("<h4>Engineering Assets</h4>"),
            widgets.HTML("<p>💡 <em>Browse to select engineering assets - they will be copied into the RO-Crate.</em></p>"),
            self.fc,
            self.w_equipment,
            self.w_asset_type,
            self.w_description,
            widgets.HBox([self.btn_add, self.btn_refresh]),
            self.out_status
        ])


class ExperimentFinalizationSection:
    """Encapsulates experiment finalization UI."""
    
    def __init__(self, crate_data: CrateData, ui: 'WorkflowUI'):
        """Initialize experiment finalization section.
        
        Args:
            crate_data: CrateData instance
            ui: WorkflowUI instance
        """
        self.crate_data = crate_data
        self.ui = ui
        
        self.btn_add = widgets.Button(
            description='Add Experiment to Crate',
            button_style='primary',
            icon='check',
            layout=widgets.Layout(width='250px')
        )
        
        self.btn_reset = widgets.Button(
            description='Reset for New Experiment',
            button_style='warning',
            icon='refresh'
        )
        
        self.btn_skip = widgets.Button(
            description='Skip (No Experiments)',
            button_style='',
            icon='forward'
        )
        
        self.out_status = widgets.Output()
        self.btn_add.on_click(self._on_add)
        self.btn_reset.on_click(self._on_reset)
        self.btn_skip.on_click(self._on_skip)
    
    def _on_add(self, b):
        with self.out_status:
            clear_output()
            
            if self.ui.current_experiment is None:
                print("⚠ Please load experiment parameters first")
                return
            
            print(f"✓ Experiment '{self.ui.current_experiment.id}' added to crate")
            if self.ui.current_experiment.experimental_parameters:
                title = self.ui.current_experiment.experimental_parameters.get('experiment', {}).get('title', 'N/A')
                print(f"  Parameters: {title}")
            print(f"  Analytical files: {len(self.ui.current_experiment.analytical_files)}")
            print(f"  Engineering assets: {len(self.ui.current_experiment.engineering_assets)}")
            print(f"\n  Total experiments in crate: {len(self.crate_data.experiments)}")
            print("\n  ⚠ Remember to reset for next experiment!")
    
    def _on_reset(self, b):
        with self.out_status:
            clear_output()
            next_num = len(self.crate_data.experiments) + 1
            self.ui.current_experiment = None
            print(f"✓ Reset complete. Ready for experiment {next_num}")
    
    def _on_skip(self, b):
        with self.out_status:
            clear_output()
            print("ℹ️ Skipping experiments - RO-Crate will contain only setup (DEXPI)")
    
    def render(self) -> widgets.VBox:
        return widgets.VBox([
            widgets.HTML("<h4>Finalize Experiment</h4>"),
            widgets.HTML("<p><strong>Tip:</strong> You can add 0 to many experiments.</p>"),
            widgets.HBox([self.btn_add, self.btn_reset, self.btn_skip]),
            self.out_status
        ])


class ReviewMetadataSection:
    """Encapsulates metadata review UI."""
    
    def __init__(self, crate_data: CrateData):
        """Initialize review metadata section.
        
        Args:
            crate_data: CrateData instance
        """
        self.crate_data = crate_data
        
        self.btn_review = widgets.Button(
            description='Review Metadata',
            button_style='info',
            icon='eye'
        )
        
        self.out_review = widgets.Output()
        self.btn_review.on_click(self._on_review)
    
    def _on_review(self, b):
        with self.out_review:
            clear_output()
            print("=" * 70)
            print("RO-CRATE METADATA REVIEW")
            print("=" * 70)
            
            print(f"\n📦 GENERAL INFORMATION")
            print(f"  Name: {self.crate_data.general.get('name', 'Not set')}")
            print(f"  Keywords: {', '.join(self.crate_data.general.get('keywords', []))}")
            print(f"  License: {self.crate_data.general.get('license', 'Not set')}")
            
            print(f"\n👥 AUTHORS: {len(self.crate_data.authors)}")
            for author in self.crate_data.authors:
                print(f"  - {author['name']} ({author['role']})")
            
            print(f"\n🏭 SHARED EXPERIMENTAL SETUP")
            if self.crate_data.dexpi:
                print(f"  DEXPI: {Path(self.crate_data.dexpi['path']).name}")
                print(f"  Equipment: {len(self.crate_data.dexpi.get('equipment', {}))} items")
                print(f"  Instruments: {len(self.crate_data.dexpi.get('instruments', {}))} items")
            else:
                print("  ⚠ No DEXPI loaded")
            
            print(f"\n🔬 EXPERIMENTS: {len(self.crate_data.experiments)}")
            if not self.crate_data.experiments:
                print("  ℹ️ No experiments defined (setup-only RO-Crate)")
            else:
                for i, exp in enumerate(self.crate_data.experiments, 1):
                    print(f"\n  Experiment {i}: {exp.id}")
                    if exp.experimental_parameters:
                        title = exp.experimental_parameters.get('experiment', {}).get('title', 'N/A')
                        print(f"    Title: {title}")
                    print(f"    Analytical files: {len(exp.analytical_files)}")
                    print(f"    Engineering assets: {len(exp.engineering_assets)}")
            
            print("\n" + "=" * 70)
    
    def render(self) -> widgets.VBox:
        return widgets.VBox([
            widgets.HTML("<h3>Review Metadata</h3>"),
            self.btn_review,
            self.out_review
        ])


class ExportCrateSection:
    """Encapsulates RO-Crate export UI."""
    
    def __init__(self, crate_data: CrateData):
        """Initialize export crate section.
        
        Args:
            crate_data: CrateData instance
        """
        self.crate_data = crate_data
        
        self.w_validate = widgets.Checkbox(
            value=True,
            description='Validate after export',
            style={'description_width': 'initial'}
        )
        
        self.btn_export = widgets.Button(
            description='Export RO-Crate',
            button_style='success',
            icon='download',
            layout=widgets.Layout(width='200px')
        )
        
        self.out_status = widgets.Output()
        self.btn_export.on_click(self._on_export)
    
    def _on_export(self, b):
        with self.out_status:
            clear_output()
            try:
                from .rocrate_builder import OPSEECrateBuilder
                from .validators import validate_crate
                
                if not self.crate_data.output_directory:
                    print("❌ Error: No output directory selected!")
                    print("💡 Please go back to Section 0 and create/select an output directory first.")
                    return
                
                output_path = self.crate_data.output_directory
                
                print("🚀 Building RO-Crate...")
                print(f"📁 Output directory: {output_path}")
                
                # Build the crate
                builder = OPSEECrateBuilder(output_dir=output_path)
                crate = builder.build_crate(self.crate_data.to_dict())
                
                # Write to disk
                print(f"📝 Writing metadata to {output_path}...")
                crate.write(output_path)
                
                print("\n✅ RO-Crate exported successfully!")
                print(f"\n📄 Files created:")
                print(f"  - {output_path}/ro-crate-metadata.json")
                print(f"  - {output_path}/ro-crate-preview.html")
                
                # Validate if requested
                if self.w_validate.value:
                    print("\n🔍 Validating RO-Crate...")
                    validation_result = validate_crate(f"{output_path}/ro-crate-metadata.json")
                    if validation_result['valid']:
                        print("✓ Validation passed")
                    else:
                        print("⚠ Validation warnings:")
                        for warning in validation_result.get('warnings', []):
                            print(f"  - {warning}")
                
                print("\n" + "="*60)
                print("Next steps:")
                print("  1. Review ro-crate-metadata.json")
                print("  2. Open ro-crate-preview.html in a browser")
                print("  3. Share or publish your RO-Crate")
                print("="*60)
                
            except Exception as e:
                print(f"\n✗ Error exporting crate: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def render(self) -> widgets.VBox:
        output_dir_display = self.crate_data.output_directory or 'Not set - please complete Section 0 first!'
        return widgets.VBox([
            widgets.HTML("<h3>Export RO-Crate</h3>"),
            widgets.HTML(f"<p>📁 <strong>Output directory:</strong> <code>{output_dir_display}</code></p>"),
            self.w_validate,
            self.btn_export,
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
        section = ExperimentConfigSection(self.crate_data, self, default_path, exp_id, exp_name)
        return section
    
    def get_analytical_data_files_section(self) -> AnalyticalDataFilesSection:
        """Create analytical data files section.
        
        Returns:
            AnalyticalDataFilesSection instance
        """
        return AnalyticalDataFilesSection(self.crate_data, self)
    
    def get_engineering_assets_section(self) -> EngineeringAssetsSection:
        """Create engineering assets section.
        
        Returns:
            EngineeringAssetsSection instance
        """
        return EngineeringAssetsSection(self.crate_data, self)
    
    def get_experiment_finalization_section(self) -> ExperimentFinalizationSection:
        """Create experiment finalization section.
        
        Returns:
            ExperimentFinalizationSection instance
        """
        return ExperimentFinalizationSection(self.crate_data, self)
    
    def get_review_metadata_section(self) -> ReviewMetadataSection:
        """Create review metadata section.
        
        Returns:
            ReviewMetadataSection instance
        """
        return ReviewMetadataSection(self.crate_data)
    
    def get_export_crate_section(self) -> ExportCrateSection:
        """Create export crate section.
        
        Returns:
            ExportCrateSection instance
        """
        return ExportCrateSection(self.crate_data)
    
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
