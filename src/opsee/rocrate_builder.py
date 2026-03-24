"""
RO-Crate builder for OPSEE chemical engineering experiments.

This module provides utilities to construct RO-Crates with domain-specific
metadata for chemical and bioprocess engineering.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import logging
import shutil

from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from rocrate.model.contextentity import ContextEntity
from rocrate.model.file import File

logger = logging.getLogger(__name__)


class OPSEECrateBuilder:
    """
    Builder class for creating OPSEE-compliant RO-Crates.
    
    Implements the OPSEE RO-Crate profile for chemical and bioprocess
    engineering experiments. Copies all referenced files into the RO-Crate
    directory to create a self-contained, portable package.
    """
    
    PROFILE_URI = "https://w3id.org/opsee/ro-crate-profile/chemical-engineering/1.0"
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the crate builder.
        
        Args:
            output_dir: Directory where RO-Crate will be created.
                       All referenced files will be copied into this directory.
                       If None, defaults to current directory.
        """
        self.crate = None
        self.output_dir = Path(output_dir) if output_dir else Path('.')
        self.copied_files = []  # Track copied files for logging
    
    def build_crate(self, crate_data: Dict) -> ROCrate:
        """
        Build an RO-Crate from collected metadata.
        Supports zero to many experiments on a single experimental setup (one DEXPI file).
        
        Args:
            crate_data: Dictionary containing:
                - general: General crate metadata
                - authors: List of authors
                - dexpi: Single DEXPI file shared across all experiments
                - experiments: List of experiments (0 to many), each with:
                    - id: Experiment identifier
                    - experimental_parameters: Parameters for this experiment
                    - analytical_files: Data files for this experiment
                    - engineering_assets: Assets for this experiment
        
        Returns:
            ROCrate instance
        """
        # Initialize crate
        self.crate = ROCrate()
        
        # Set general metadata
        self._set_general_metadata(crate_data.get('general', {}))
        
        # Add authors
        self._add_authors(crate_data.get('authors', []))
        
        # Add the single shared DEXPI file (if provided)
        if crate_data.get('dexpi'):
            self._add_dexpi(crate_data['dexpi'])
        
        # Process experiments (0 to many)
        experiments = crate_data.get('experiments', [])
        
        if experiments:
            logger.info(f"Building crate with {len(experiments)} experiments")
            experiment_entities = []
            
            for exp in experiments:
                exp_id = exp.get('id', f"exp_{experiments.index(exp) + 1}")
                
                # Add experimental parameters for this experiment
                if exp.get('experimental_parameters'):
                    exp_entity = self._add_experimental_parameters(
                        exp['experimental_parameters'], 
                        experiment_id=exp_id
                    )
                    experiment_entities.append(exp_entity)
                
                # Add analytical files for this experiment
                for file_data in exp.get('analytical_files', []):
                    self._add_analytical_file(
                        file_data, 
                        crate_data.get('dexpi', {}), 
                        experiment_id=exp_id
                    )
                
                # Add engineering assets for this experiment
                for asset_data in exp.get('engineering_assets', []):
                    self._add_engineering_asset(
                        asset_data, 
                        crate_data.get('dexpi', {}), 
                        experiment_id=exp_id
                    )
            
            # Link all experiments to root
            if experiment_entities:
                self.crate.root_dataset['hasPart'] = experiment_entities
        else:
            logger.info("Building crate with no experiments (setup only)")
        
        # Mark crate as conforming to OPSEE profile
        self.crate.root_dataset['conformsTo'] = self.PROFILE_URI
        
        logger.info("RO-Crate built successfully")
        return self.crate
    
    def _set_general_metadata(self, general: Dict):
        """Set general crate-level metadata on root dataset.
        
        Populates the root dataset entity with general metadata including
        name, description, keywords, license, and timestamps following
        RO-Crate specification and Dublin Core terms.
        
        Args:
            general: Dictionary containing general metadata fields:
                - name: Human-readable crate name
                - description: Detailed description of crate contents
                - keywords: List of keywords for discovery
                - license: License identifier (e.g., 'CC-BY-4.0')
                - dateCreated: ISO 8601 formatted creation date
        """
        root = self.crate.root_dataset
        
        if general.get('name'):
            root['name'] = general['name']
        
        if general.get('description'):
            root['description'] = general['description']
        
        if general.get('keywords'):
            root['keywords'] = general['keywords']
        
        if general.get('license'):
            root['license'] = general['license']
        
        if general.get('dateCreated'):
            root['dateCreated'] = general['dateCreated']
        
        # Add dateModified
        root['dateModified'] = datetime.now().isoformat()
    
    def _add_authors(self, authors: List[Dict]):
        """Add authors and contributors to the crate.
        
        Creates Person entities for each author with ORCID-based identifiers
        where available. Links all authors to the root dataset following
        schema.org and RO-Crate conventions.
        
        Args:
            authors: List of dictionaries, each containing:
                - name: Full name of the person (required)
                - orcid: ORCID identifier without URL prefix (optional)
                - affiliation: Organization affiliation (optional)
                - role: Role in the research (e.g., 'Author', 'DataCollector')
        """
        author_entities = []
        
        for author_data in authors:
            # Create ORCID-based ID if available, otherwise use local ID
            if author_data.get('orcid'):
                person_id = f"https://orcid.org/{author_data['orcid']}"
            else:
                # Create a local identifier
                name_slug = author_data['name'].lower().replace(' ', '-')
                person_id = f"#{name_slug}"
            
            person = self.crate.add(Person(
                self.crate,
                person_id,
                properties={
                    'name': author_data['name'],
                    'affiliation': author_data.get('affiliation'),
                }
            ))
            
            # Store role information (will be used when linking)
            person['roleName'] = author_data.get('role', 'Author')
            
            author_entities.append(person)
        
        # Add to root dataset
        if author_entities:
            self.crate.root_dataset['author'] = author_entities
    
    def _copy_and_add_file(self, source_path: str, dest_relative_path: str, 
                          properties: dict) -> File:
        """Copy a file into the RO-Crate directory and add to metadata.
        
        This method ensures all files are physically copied into the RO-Crate,
        making it self-contained and portable. The source file is copied to
        the specified relative path within the output directory.
        
        Args:
            source_path: Original file location (absolute or relative path)
            dest_relative_path: Where to place in crate (e.g., 'data/raw/file.csv')
            properties: Metadata properties for the file entity
        
        Returns:
            File entity added to crate
        
        Raises:
            FileNotFoundError: If source file doesn't exist
            IOError: If file copy fails
        """
        source = Path(source_path)
        dest = self.output_dir / dest_relative_path
        
        # Create parent directories
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file if it exists
        if source.exists():
            shutil.copy2(source, dest)  # copy2 preserves metadata
            self.copied_files.append((str(source), str(dest_relative_path)))
            logger.info(f"Copied: {source.name} → {dest_relative_path}")
        else:
            logger.warning(f"Source file not found: {source}")
            raise FileNotFoundError(f"Cannot copy non-existent file: {source}")
    
        # Add to RO-Crate using ABSOLUTE path where we copied the file
        # The rocrate library needs to find the file at write time
        # Use dest_path parameter to specify the relative path in metadata
        return self.crate.add_file(
            str(dest.absolute()),
            dest_path=dest_relative_path,
            properties=properties
        )

    
    def _get_media_type(self, file_path: str) -> str:
        """Determine IANA media type from file extension.
        
        Args:
            file_path: Path to file
        
        Returns:
            IANA media type string
        """
        ext = Path(file_path).suffix.lower()
        format_map = {
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.yaml': 'application/x-yaml',
            '.yml': 'application/x-yaml',
            '.step': 'application/step',
            '.stp': 'application/step',
            '.iges': 'application/iges',
            '.igs': 'application/iges',
            '.stl': 'model/stl',
            '.dwg': 'application/acad',
            '.dxf': 'application/dxf',
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        return format_map.get(ext, 'application/octet-stream')
    
    
    def _add_dexpi(self, dexpi_data: Dict):
        """Add single shared DEXPI file and equipment entities to the crate.
        
        Copies the DEXPI XML file into data/engineering/ directory within the crate.
        
        Args:
            dexpi_data: DEXPI data dictionary with equipment and instruments
        """
        # Add the DEXPI file itself (shared across all experiments)
        dexpi_path = dexpi_data.get('path')
        dexpi_file = None
        
        if dexpi_path:
            dest_path = f"data/engineering/{Path(dexpi_path).name}"
            try:
                # Copy DEXPI file into crate
                dexpi_file = self._copy_and_add_file(
                    dexpi_path,
                    dest_path,
                    properties={
                        '@type': ['File', 'SoftwareSourceCode'],
                        'name': f'DEXPI P&ID: {Path(dexpi_path).stem}',
                        'description': 'DEXPI XML file containing process setup and instrumentation',
                        'encodingFormat': 'application/xml',
                        'conformsTo': {'@id': 'https://www.dexpi.org/'}
                    }
                )
            except FileNotFoundError as e:
                logger.error(f"Failed to copy DEXPI file: {e}")
                raise
        
        # Add equipment as contextual entities (shared across experiments)
        equipment = dexpi_data.get('equipment', {})
        for eq_id, eq_data in equipment.items():
            # Create ProcessEquipment entity following schema.org vocabulary
            eq_entity = self.crate.add(ContextEntity(
                self.crate,
                f"#equipment-{eq_id}",
                properties={
                    '@type': 'ProcessEquipment',
                    'name': eq_data.get('name') or eq_data['tag_name'],
                    'identifier': eq_data['tag_name'],
                    'additionalType': eq_data.get('type'),
                    'description': f"{eq_data.get('type', 'Equipment')} {eq_data['tag_name']}"
                }
            ))
            
            # Link to DEXPI file
            if dexpi_file:
                eq_entity['isDefinedIn'] = dexpi_file
        
        # Add instruments as contextual entities (shared across experiments)
        instruments = dexpi_data.get('instruments', {})
        for inst_id, inst_data in instruments.items():
            # Create AnalyticalInstrument entity with measurement capability metadata
            inst_entity = self.crate.add(ContextEntity(
                self.crate,
                f"#instrument-{inst_id}",
                properties={
                    '@type': 'AnalyticalInstrument',
                    'name': inst_data.get('description') or inst_data['tag_name'],
                    'identifier': inst_data['tag_name'],
                    'additionalType': inst_data.get('type'),
                    'description': inst_data.get('description', '')
                }
            ))
            
            # Link to DEXPI file
            if dexpi_file:
                inst_entity['isDefinedIn'] = dexpi_file
    
    def _add_experimental_parameters(self, params: Dict, experiment_id: Optional[str] = None):
        """Add experimental parameters as a contextual entity.
        
        Args:
            params: Experimental parameters dictionary
            experiment_id: Optional experiment ID for multi-experiment crates
            
        Returns:
            The created experiment entity
        """
        import json
        
        entity_id = f'#experiment-{experiment_id}' if experiment_id else '#experiment'
        
        # Convert nested dicts to JSON strings to avoid RO-Crate validation errors
        # RO-Crate doesn't allow arbitrary nested objects without @id fields
        exp_properties = {
            '@type': 'ChemicalExperiment',
            'name': params.get('experiment', {}).get('title', 'Experiment'),
            'description': params.get('experiment', {}).get('description', '')
        }
        
        # Add conditions as JSON string if present
        if params.get('conditions'):
            exp_properties['experimentalConditions'] = json.dumps(params['conditions'], indent=2)
        
        # Add methodology as JSON string if present
        if params.get('methodology'):
            exp_properties['methodology'] = json.dumps(params['methodology'], indent=2)
        
        exp_entity = self.crate.add(ContextEntity(
            self.crate,
            entity_id,
            properties=exp_properties
        ))
        
        # Link experiment to root (for single experiment mode)
        if not experiment_id:
            self.crate.root_dataset['about'] = exp_entity
        
        return exp_entity
    
    def _add_analytical_file(self, file_data: Dict, dexpi_data: Dict, experiment_id: Optional[str] = None):
        """
        Add an analytical data file with links to shared instruments.
        
        Copies the data file into the appropriate experiment directory within the crate.
        Files are organized by experiment ID and processing status (raw vs processed).
        
        Args:
            file_data: File metadata including path and instrument link
            dexpi_data: DEXPI data for resolving instrument references
            experiment_id: Optional experiment ID for organizing files
        """
        file_path = file_data['path']
        
        # Prepare file properties
        properties = {
            '@type': ['File', 'Dataset'],
            'name': Path(file_path).name,
            'description': file_data.get('description', ''),
            'additionalType': file_data.get('data_type', 'RawData'),
            'encodingFormat': self._get_media_type(file_path)
        }
        
        # Determine destination path based on data type and experiment
        # Organizes files by experiment ID and processing status (raw vs processed)
        data_type = file_data.get('data_type', 'RawData')
        if experiment_id:
            # Organize by experiment
            if 'Raw' in data_type or 'Calibration' in data_type:
                dest_path = f"data/experiments/{experiment_id}/raw/{Path(file_path).name}"
            else:
                dest_path = f"data/experiments/{experiment_id}/processed/{Path(file_path).name}"
        else:
            # No experiment ID - default structure
            if 'Raw' in data_type or 'Calibration' in data_type:
                dest_path = f"data/raw/{Path(file_path).name}"
            else:
                dest_path = f"data/processed/{Path(file_path).name}"
        
        # Copy file into crate
        try:
            data_file = self._copy_and_add_file(file_path, dest_path, properties)
        except FileNotFoundError as e:
            logger.error(f"Failed to copy analytical file: {e}")
            raise
        
        # Link to shared instrument (no experiment prefix since instruments are shared)
        instrument_id = file_data.get('instrument_id')
        if instrument_id:
            # Find the instrument entity in the crate
            inst_entity_id = f"#instrument-{instrument_id}"
            inst_entity = self.crate.dereference(inst_entity_id)
            
            if inst_entity:
                data_file['instrument'] = inst_entity
                data_file['wasGeneratedBy'] = inst_entity
    
    def _add_engineering_asset(self, asset_data: Dict, dexpi_data: Dict, experiment_id: Optional[str] = None):
        """
        Add an engineering asset (CAD, drawing, etc.) with links to shared equipment.
        
        Copies the asset file into the appropriate directory within the crate.
        Assets are organized by experiment ID if provided.
        
        Args:
            asset_data: Asset metadata including path and equipment link
            dexpi_data: DEXPI data for resolving equipment references
            experiment_id: Optional experiment ID for organizing files
        """
        asset_path = asset_data['path']
        
        properties = {
            '@type': ['File', 'DigitalDocument'],
            'name': Path(asset_path).name,
            'description': asset_data.get('description', ''),
            'additionalType': asset_data.get('asset_type', 'EngineeringAsset'),
            'encodingFormat': self._get_media_type(asset_path)
        }
        
        # Organize by experiment if ID provided
        if experiment_id:
            dest_path = f"data/experiments/{experiment_id}/engineering/{Path(asset_path).name}"
        else:
            dest_path = f"data/engineering/{Path(asset_path).name}"
        
        # Copy file into crate
        try:
            asset_file = self._copy_and_add_file(asset_path, dest_path, properties)
        except FileNotFoundError as e:
            logger.error(f"Failed to copy engineering asset: {e}")
            raise
        
        # Link to shared equipment (no experiment prefix since equipment is shared)
        equipment_id = asset_data.get('equipment_id')
        if equipment_id:
            # Find the equipment entity in the crate
            eq_entity_id = f"#equipment-{equipment_id}"
            eq_entity = self.crate.dereference(eq_entity_id)
            
            if eq_entity:
                asset_file['about'] = eq_entity
                # Create bidirectional link: equipment -> hasRepresentation -> asset
                # This supports navigation in both directions in the RO-Crate graph
                if not eq_entity.get('hasRepresentation'):
                    eq_entity['hasRepresentation'] = []
                eq_entity.append_to('hasRepresentation', asset_file)


def create_crate(crate_data: Dict) -> ROCrate:
    """
    Convenience function to create an OPSEE RO-Crate.
    
    Args:
        crate_data: Dictionary with all crate metadata
    
    Returns:
        ROCrate instance
    """
    builder = OPSEECrateBuilder()
    return builder.build_crate(crate_data)
