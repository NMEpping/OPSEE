"""
DEXPI extraction utilities.

Provides helper functions to parse DEXPI models and extract equipment
and instrumentation metadata into dictionary format suitable for
RO-Crate metadata generation.
"""

from typing import Dict, Any


def extract_equipment(dexpi_model) -> Dict[str, Dict[str, Any]]:
    """Extract equipment from pyDEXPI model.
    
    Parses the conceptualModel.taggedPlantItems from a loaded DEXPI model
    and converts to dictionary format for RO-Crate builder consumption.
    
    Args:
        dexpi_model: Loaded DEXPI model from ProteusSerializer.load()
    
    Returns:
        Dictionary mapping equipment IDs to metadata:
        {
            'eq_id': {
                'id': 'unique_identifier',
                'tag_name': 'R-101',
                'type': 'Reactor',
                'name': 'Main Reactor',
                'element': 'Equipment'
            },
            ...
        }
    """
    equipment = {}
    if hasattr(dexpi_model, 'conceptualModel') and dexpi_model.conceptualModel:
        for eq in dexpi_model.conceptualModel.taggedPlantItems:
            # Generate unique ID from DEXPI object
            eq_id = str(eq.id) if hasattr(eq, 'id') else str(id(eq))
            
            # Extract tag name with fallback chain
            tag_name = None
            if hasattr(eq, 'tagName') and eq.tagName:
                tag_name = eq.tagName
            elif hasattr(eq, 'componentName') and eq.componentName:
                tag_name = eq.componentName
            
            # Build equipment metadata dictionary
            equipment[eq_id] = {
                'id': eq_id,
                'tag_name': tag_name or eq_id,  # Fallback to ID if no tag
                'type': eq.__class__.__name__,   # e.g., 'Reactor', 'Tank'
                'name': eq.componentName if hasattr(eq, 'componentName') else '',
                'element': 'Equipment'
            }
    return equipment


def extract_instruments(dexpi_model) -> Dict[str, Dict[str, Any]]:
    """Extract instruments from pyDEXPI model.
    
    Parses both actuatingSystems and processSignalGeneratingSystems from
    the DEXPI conceptual model to extract all instrumentation metadata.
    
    Args:
        dexpi_model: Loaded DEXPI model from ProteusSerializer.load()
    
    Returns:
        Dictionary mapping instrument IDs to metadata:
        {
            'inst_id': {
                'id': 'unique_identifier',
                'tag_name': 'GC-001',
                'type': 'ActuatingSystem' | 'ProcessSignalGeneratingSystem',
                'description': 'Gas chromatograph',
                'element': 'ActuatingSystem' | 'MeasuringSystem'
            },
            ...
        }
    """
    instruments = {}
    if hasattr(dexpi_model, 'conceptualModel') and dexpi_model.conceptualModel:
        
        # Extract actuating systems (control instruments, valves)
        for act_sys in dexpi_model.conceptualModel.actuatingSystems:
            inst_id = str(act_sys.id) if hasattr(act_sys, 'id') else str(id(act_sys))
            
            # Extract tag name with multiple fallbacks
            tag_name = None
            if hasattr(act_sys, 'actuatingSystemNumber') and act_sys.actuatingSystemNumber:
                tag_name = act_sys.actuatingSystemNumber
            elif hasattr(act_sys, 'componentName') and act_sys.componentName:
                tag_name = act_sys.componentName
            
            # Extract description if available
            description = ''
            if hasattr(act_sys, 'typicalInformation') and act_sys.typicalInformation:
                description = act_sys.typicalInformation
            
            instruments[inst_id] = {
                'id': inst_id,
                'tag_name': tag_name or inst_id,
                'type': 'ActuatingSystem',
                'description': description,
                'element': 'ActuatingSystem'
            }
        
        # Extract process signal generating systems (measuring instruments)
        if hasattr(dexpi_model.conceptualModel, 'processSignalGeneratingSystems'):
            for psgs in dexpi_model.conceptualModel.processSignalGeneratingSystems:
                inst_id = str(psgs.id) if hasattr(psgs, 'id') else str(id(psgs))
                
                # Extract tag name with multiple fallbacks
                tag_name = None
                if hasattr(psgs, 'processSignalGeneratingSystemNumber') and psgs.processSignalGeneratingSystemNumber:
                    tag_name = psgs.processSignalGeneratingSystemNumber
                elif hasattr(psgs, 'componentName') and psgs.componentName:
                    tag_name = psgs.componentName
                
                # Extract description if available
                description = ''
                if hasattr(psgs, 'typicalInformation') and psgs.typicalInformation:
                    description = psgs.typicalInformation
                
                instruments[inst_id] = {
                    'id': inst_id,
                    'tag_name': tag_name or inst_id,
                    'type': 'ProcessSignalGeneratingSystem',
                    'description': description,
                    'element': 'MeasuringSystem'  # Classified as measuring device
                }
    return instruments
