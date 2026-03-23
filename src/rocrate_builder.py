"""
RO-Crate builder for OPSEE chemical engineering experiments.

This module provides utilities to construct RO-Crates with domain-specific
metadata for chemical and bioprocess engineering.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import logging

from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from rocrate.model.contextentity import ContextEntity
from rocrate.model.file import File

logger = logging.getLogger(__name__)


class OPSEECrateBuilder:
    """
    Builder class for creating OPSEE-compliant RO-Crates.
    
    Implements the OPSEE RO-Crate profile for chemical and bioprocess
    engineering experiments.
    """
    
    PROFILE_URI = "https://w3id.org/opsee/ro-crate-profile/chemical-engineering/1.0"
    
    def __init__(self):
        """Initialize the crate builder."""
        self.crate = None
    
    def build_crate(self, crate_data: Dict) -> ROCrate:
        """
        Build an RO-Crate from collected metadata.
        Supports 0 to many experiments on a single experimental setup (one DEXPI file).
        
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
        """Set general crate-level metadata."""
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
        """Add authors and contributors to the crate."""
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
    
    
    def _add_dexpi(self, dexpi_data: Dict):
        """Add single shared DEXPI file and equipment entities to the crate.
        
        Args:
            dexpi_data: DEXPI data dictionary with equipment and instruments
        """
        # Add the DEXPI file itself (shared across all experiments)
        dexpi_path = dexpi_data.get('path')
        dexpi_file = None
        
        if dexpi_path and Path(dexpi_path).exists():
            dexpi_file = self.crate.add_file(
                dexpi_path,
                dest_path=f"data/engineering/{Path(dexpi_path).name}",
                properties={
                    '@type': ['File', 'SoftwareSourceCode'],
                    'name': 'Process P&ID (DEXPI)',
                    'description': 'DEXPI XML file containing process setup and instrumentation',
                    'encodingFormat': 'application/xml',
                    'conformsTo': 'https://www.dexpi.org/'
                }
            )
        
        # Add equipment as contextual entities (shared across experiments)
        equipment = dexpi_data.get('equipment', {})
        for eq_id, eq_data in equipment.items():
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
        entity_id = f'#experiment-{experiment_id}' if experiment_id else '#experiment'
        
        exp_entity = self.crate.add(ContextEntity(
            self.crate,
            entity_id,
            properties={
                '@type': 'ChemicalExperiment',
                'name': params.get('experiment', {}).get('title', 'Experiment'),
                'description': params.get('experiment', {}).get('description', ''),
                'experimentalConditions': params.get('conditions', {}),
                'methodology': params.get('methodology', {})
            }
        ))
        
        # Link experiment to root (for single experiment mode)
        if not experiment_id:
            self.crate.root_dataset['about'] = exp_entity
        
        return exp_entity
    
    def _add_analytical_file(self, file_data: Dict, dexpi_data: Dict, experiment_id: Optional[str] = None):
        """
        Add an analytical data file with links to shared instruments.
        
        Args:
            file_data: File metadata including path and instrument link
            dexpi_data: DEXPI data for resolving instrument references
            experiment_id: Optional experiment ID for organizing files
        """
        file_path = file_data['path']
        
        # Check if file exists, if not just reference it
        properties = {
            '@type': ['File', 'AnalyticalData'],
            'name': Path(file_path).name,
            'description': file_data.get('description', ''),
            'additionalType': file_data.get('data_type', 'RawData')
        }
        
        # Add encoding format based on extension
        ext = Path(file_path).suffix.lower()
        format_map = {
            '.csv': 'text/csv',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xml': 'application/xml'
        }
        if ext in format_map:
            properties['encodingFormat'] = format_map[ext]
        
        # Determine destination path based on data type and experiment
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
        
        # Add file to crate
        if Path(file_path).exists():
            data_file = self.crate.add_file(file_path, dest_path=dest_path, properties=properties)
        else:
            # File doesn't exist yet - add as reference
            data_file = self.crate.add(File(self.crate, dest_path, properties=properties))
        
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
        
        Args:
            asset_data: Asset metadata including path and equipment link
            dexpi_data: DEXPI data for resolving equipment references
            experiment_id: Optional experiment ID for organizing files
        """
        asset_path = asset_data['path']
        
        properties = {
            '@type': ['File', 'EngineeringAsset'],
            'name': Path(asset_path).name,
            'description': asset_data.get('description', ''),
            'additionalType': asset_data.get('asset_type', 'CADModel')
        }
        
        # Add encoding format based on extension
        ext = Path(asset_path).suffix.lower()
        format_map = {
            '.step': 'application/step',
            '.stp': 'application/step',
            '.iges': 'application/iges',
            '.igs': 'application/iges',
            '.stl': 'model/stl',
            '.dwg': 'application/acad',
            '.dxf': 'application/dxf',
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.png': 'image/png'
        }
        if ext in format_map:
            properties['encodingFormat'] = format_map[ext]
        
        # Organize by experiment if ID provided
        if experiment_id:
            dest_path = f"data/experiments/{experiment_id}/engineering/{Path(asset_path).name}"
        else:
            dest_path = f"data/engineering/{Path(asset_path).name}"
        
        # Add file to crate
        if Path(asset_path).exists():
            asset_file = self.crate.add_file(asset_path, dest_path=dest_path, properties=properties)
        else:
            # File doesn't exist yet - add as reference
            asset_file = self.crate.add(File(self.crate, dest_path, properties=properties))
        
        # Link to shared equipment (no experiment prefix since equipment is shared)
        equipment_id = asset_data.get('equipment_id')
        if equipment_id:
            # Find the equipment entity in the crate
            eq_entity_id = f"#equipment-{equipment_id}"
            eq_entity = self.crate.dereference(eq_entity_id)
            
            if eq_entity:
                asset_file['about'] = eq_entity
                # Create bidirectional link
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
