"""
Experiment configuration and data management.

Provides data structures and utilities for managing experiments and their
associated data files, parameters, and engineering assets throughout
the workflow.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AnalyticalFile:
    """Analytical data file metadata."""
    path: str
    instrument_id: str
    data_type: str  # RawData, ProcessedData, CalibrationData, DerivedData
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for RO-Crate builder."""
        return {
            'path': self.path,
            'instrument_id': self.instrument_id,
            'data_type': self.data_type,
            'description': self.description
        }


@dataclass
class EngineeringAsset:
    """Engineering asset metadata."""
    path: str
    equipment_id: str
    asset_type: str  # CADModel, TechnicalDrawing, GeometryFile, Specification, Photo
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for RO-Crate builder."""
        return {
            'path': self.path,
            'equipment_id': self.equipment_id,
            'asset_type': self.asset_type,
            'description': self.description
        }


@dataclass
class Experiment:
    """Single experiment configuration."""
    id: str
    experimental_parameters: Optional[Dict[str, Any]] = None
    analytical_files: List[AnalyticalFile] = field(default_factory=list)
    engineering_assets: List[EngineeringAsset] = field(default_factory=list)
    
    def add_analytical_file(self, path: str, instrument_id: str, 
                           data_type: str, description: str = ""):
        """Add an analytical data file."""
        self.analytical_files.append(
            AnalyticalFile(path, instrument_id, data_type, description)
        )
    
    def add_engineering_asset(self, path: str, equipment_id: str,
                             asset_type: str, description: str = ""):
        """Add an engineering asset."""
        self.engineering_assets.append(
            EngineeringAsset(path, equipment_id, asset_type, description)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for RO-Crate builder."""
        return {
            'id': self.id,
            'experimental_parameters': self.experimental_parameters,
            'analytical_files': [f.to_dict() for f in self.analytical_files],
            'engineering_assets': [a.to_dict() for a in self.engineering_assets]
        }


class CrateData:
    """Container for RO-Crate metadata throughout workflow."""
    
    def __init__(self):
        """Initialize empty crate data."""
        self.output_directory: Optional[str] = None
        self.general: Dict[str, Any] = {}
        self.authors: List[Dict[str, str]] = []
        self.dexpi: Optional[Dict[str, Any]] = None
        self.experiments: List[Experiment] = []
    
    def set_output_directory(self, path: str):
        """Set RO-Crate output directory."""
        self.output_directory = str(Path(path).absolute())
    
    def set_general_metadata(self, name: str, description: str = "",
                            keywords: List[str] = None, license: str = "",
                            date_created: str = ""):
        """Set general crate metadata."""
        self.general = {
            'name': name,
            'description': description,
            'keywords': keywords or [],
            'license': license,
            'dateCreated': date_created
        }
    
    def add_author(self, name: str, orcid: str = "", 
                   affiliation: str = "", role: str = "Author"):
        """Add an author/contributor."""
        self.authors.append({
            'name': name,
            'orcid': orcid or None,
            'affiliation': affiliation or None,
            'role': role
        })
    
    def set_dexpi(self, path: str, equipment: Dict = None, 
                  instruments: Dict = None):
        """Set shared DEXPI file and extracted metadata."""
        self.dexpi = {
            'path': str(Path(path).absolute()),
            'equipment': equipment or {},
            'instruments': instruments or {}
        }
    
    def add_experiment(self, exp_id: str) -> Experiment:
        """Create and add a new experiment."""
        exp = Experiment(id=exp_id)
        self.experiments.append(exp)
        return exp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for RO-Crate builder."""
        return {
            'output_directory': self.output_directory,
            'general': self.general,
            'authors': self.authors,
            'dexpi': self.dexpi,
            'experiments': [e.to_dict() for e in self.experiments]
        }
