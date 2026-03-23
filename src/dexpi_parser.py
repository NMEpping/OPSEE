"""
DEXPI XML Parser using pydexpi for extracting process equipment and instrumentation.

This module uses the pydexpi library to parse DEXPI (Data Exchange in the Process Industry)
XML files to extract equipment, instruments, and their properties for linking to
experimental data in RO-Crates.
"""

from typing import Dict, Optional
from pathlib import Path
import logging

try:
    from pydexpi import DexpiDocument
except ImportError:
    raise ImportError(
        "pydexpi is required for DEXPI parsing. Install with: uv pip install pydexpi"
    )

logger = logging.getLogger(__name__)


class DexpiParser:
    """
    Parser for DEXPI XML files using pydexpi library.
    
    Extracts equipment and instrumentation metadata from P&ID representations
    following the DEXPI standard.
    """
    
    def __init__(self, xml_path: str):
        """
        Initialize parser with DEXPI XML file.
        
        Args:
            xml_path: Path to the DEXPI XML file
        """
        self.xml_path = Path(xml_path)
        if not self.xml_path.exists():
            raise FileNotFoundError(f"DEXPI file not found: {xml_path}")
        
        # Load DEXPI document using pydexpi
        self.doc = DexpiDocument.from_file(str(self.xml_path))
        logger.info(f"Loaded DEXPI document: {self.xml_path.name}")
    
    def get_equipment(self) -> Dict[str, Dict]:
        """
        Extract all equipment items from DEXPI using pydexpi.
        
        Returns:
            Dictionary mapping equipment IDs to their properties:
            {
                'eq_id': {
                    'tag_name': 'R-101',
                    'type': 'Reactor',
                    'name': 'Main Reactor',
                    'id': 'Equipment-1'
                }
            }
        """
        equipment = {}
        
        # Get all equipment from the document
        for eq in self.doc.equipment:
            eq_id = eq.id
            
            # Extract tag name (ActuatingSystemNumber or similar)
            tag_name = None
            if hasattr(eq, 'tag_name'):
                tag_name = eq.tag_name
            elif hasattr(eq, 'generic_attributes'):
                for attr in eq.generic_attributes:
                    if 'tag' in attr.name.lower() or 'number' in attr.name.lower():
                        tag_name = attr.value
                        break
            
            # Get equipment type/class
            eq_type = eq.component_class if hasattr(eq, 'component_class') else 'Unknown'
            eq_name = eq.component_name if hasattr(eq, 'component_name') else ''
            
            equipment[eq_id] = {
                'id': eq_id,
                'tag_name': tag_name or eq_id,
                'type': eq_type,
                'name': eq_name,
                'element': 'Equipment'
            }
        
        logger.info(f"Extracted {len(equipment)} equipment items")
        return equipment
    
    def get_instruments(self) -> Dict[str, Dict]:
        """
        Extract all analytical instruments and actuating systems from DEXPI using pydexpi.
        
        Returns:
            Dictionary mapping instrument IDs to their properties:
            {
                'inst_id': {
        
        Returns:
            Dictionary mapping instrument IDs to their properties:
            {
                'inst_id': {
                    'tag_name': 'GC-001',
                    'type': 'AnalyticalInstrument',
                    'description': 'Gas Chromatograph',
                    'id': 'ActuatingSystem-1'
                }
            }
        """
        instruments = {}
        
        # Get actuating systems from the document
        for act_sys in self.doc.actuating_systems:
            inst_id = act_sys.id
            
            # Extract tag/number
            tag_name = None
            if hasattr(act_sys, 'tag_name'):
                tag_name = act_sys.tag_name
            elif hasattr(act_sys, 'generic_attributes'):
                for attr in act_sys.generic_attributes:
                    if 'number' in attr.name.lower():
                        tag_name = attr.value
                        break
            
            # Get type
            inst_type = act_sys.component_class if hasattr(act_sys, 'component_class') else 'ActuatingSystem'
            description = act_sys.component_name if hasattr(act_sys, 'component_name') else ''
            
            instruments[inst_id] = {
                'id': inst_id,
                'tag_name': tag_name or inst_id,
                'type': inst_type,
                'description': description,
                'element': 'ActuatingSystem'
            }
        
        logger.info(f"Extracted {len(instruments)} instruments/actuating systems")
        return instruments
    
    def get_plant_info(self) -> Dict:
        """
        Extract plant information and metadata from DEXPI.
        
        Returns:
            Dictionary with plant information
        """
        info = {}
        
        if hasattr(self.doc, 'plant_information'):
            plant_info = self.doc.plant_information
            if plant_info:
                info['application'] = getattr(plant_info, 'application', None)
                info['version'] = getattr(plant_info, 'application_version', None)
                info['discipline'] = getattr(plant_info, 'discipline', None)
                info['originating_system'] = getattr(plant_info, 'originating_system', None)
        
        return info
    
    def find_by_tag_name(self, tag_name: str) -> Optional[Dict]:
        """
        Find a component by its TagName across equipment and instruments.
        
        Args:
            tag_name: The TagName to search for (e.g., 'R-101', 'GC-001')
        
        Returns:
            Component dictionary if found, None otherwise
        """
        # Search in equipment
        equipment = self.get_equipment()
        for eq_id, eq_data in equipment.items():
            if eq_data.get('tag_name') == tag_name:
                return eq_data
        
        # Search in instruments
        instruments = self.get_instruments()
        for inst_id, inst_data in instruments.items():
            if inst_data.get('tag_name') == tag_name:
                return inst_data
        
        return None
    
    def get_all_tag_names(self) -> list:
        """
        Get a list of all TagNames in the DEXPI file.
        
        Returns:
            List of TagName strings
        """
        tag_names = []
        
        equipment = self.get_equipment()
        tag_names.extend([eq['tag_name'] for eq in equipment.values() if eq.get('tag_name')])
        
        instruments = self.get_instruments()
        tag_names.extend([inst['tag_name'] for inst in instruments.values() if inst.get('tag_name')])
        
        return sorted(tag_names)
            Component properties dictionary if found, None otherwise
        """
        # Search in all component types
        all_components = {
            **self.get_equipment(),
            **self.get_instruments(),
            **self.get_nozzles(),
            **self.get_piping()
        }
        
        for comp_id, comp_data in all_components.items():
            if comp_data.get('tag_name') == tag_name:
                return comp_data
        
        return None
    
    def get_all_components(self) -> Dict[str, Dict]:
        """
        Get all components (equipment, instruments, nozzles, piping).
        
        Returns:
            Dictionary of all components
        """
        return {
            **self.get_equipment(),
            **self.get_instruments(),
            **self.get_nozzles(),
            **self.get_piping()
        }
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the DEXPI XML structure.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if file is well-formed XML
        try:
            etree.parse(str(self.xml_path))
        except etree.XMLSyntaxError as e:
            issues.append(f"XML syntax error: {str(e)}")
            return False, issues
        
        # Check for basic DEXPI structure
        equipment = self.get_equipment()
        instruments = self.get_instruments()
        
        if not equipment and not instruments:
            issues.append("No equipment or instruments found in DEXPI file")
        
        # Check for components without TagNames
        all_components = self.get_all_components()
        missing_tags = [c for c in all_components.values() 
                       if not c.get('tag_name') or c['tag_name'] == c['id']]
        
        if missing_tags:
            issues.append(f"{len(missing_tags)} components missing TagName attributes")
        
        is_valid = len(issues) == 0
        return is_valid, issues


def parse_dexpi(xml_path: str) -> DexpiParser:
    """
    Convenience function to parse a DEXPI file.
    
    Args:
        xml_path: Path to DEXPI XML file
    
    Returns:
        DexpiParser instance
    """
    return DexpiParser(xml_path)
