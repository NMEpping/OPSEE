"""
DEXPI extraction utilities using pyDEXPI library API.

Provides functions to parse DEXPI models and extract equipment, instruments,
and process connections into dictionary format for RO-Crate metadata generation.

Uses official pyDEXPI 1.1.0+ API:
- Equipment: ConceptualModel.taggedPlantItems (TaggedPlantItem objects)
- Instruments: ProcessInstrumentationFunctions with child ActuatingFunctions 
  and ProcessSignalGeneratingFunctions
- Connections: PipingNetworkSystems containing segments with piping connections
"""

from typing import Dict, Any, Optional, List
from pydexpi.dexpi_classes.pydantic_classes import DexpiModel, ConceptualModel


def extract_equipment(dexpi_model: DexpiModel) -> Dict[str, Dict[str, Any]]:
    """Extract equipment using pyDEXPI ConceptualModel.taggedPlantItems API.
    
    Uses official pyDEXPI API to access equipment through the conceptual model.
    Extracts hierarchical sub-components (chambers, nozzles, motors) using
    pyDEXPI compositional properties directly, not via getattr().
    
    Args:
        dexpi_model: DexpiModel instance loaded via ProteusSerializer.load()
    
    Returns:
        Dictionary of equipment items with their properties and sub-components
    """
    equipment = {}
    
    # Access conceptualModel from DexpiModel via pyDEXPI API
    if not dexpi_model.conceptualModel:
        return equipment
    
    conceptual_model = dexpi_model.conceptualModel
    
    # Use official pyDEXPI API: ConceptualModel.taggedPlantItems
    # This returns list of TaggedPlantItem objects with direct property access
    for eq in conceptual_model.taggedPlantItems:
        try:
            # Access pyDEXPI object properties directly (NOT via getattr)
            eq_id = str(eq.id)
            tag_name = eq.tagName or eq.componentName or eq_id  # type: ignore
            
            # Build equipment dictionary using pyDEXPI properties
            equipment[eq_id] = {
                'id': eq_id,
                'tag_name': str(tag_name),
                'type': eq.__class__.__name__,  # e.g., 'Pump', 'Tank', 'Reactor'
                'description': str(eq.equipmentDescription or ''),  # type: ignore
                'element': 'Equipment'
            }
            
            # Extract sub-components using pyDEXPI compositional attributes
            sub_components = {}
            
            # Chambers - access via direct pyDEXPI property
            if eq.chambers:  # type: ignore
                sub_components['chambers'] = [
                    {
                        'id': str(chamber.id),
                        'tag_name': str(chamber.subTagName or ''),
                        'type': chamber.__class__.__name__
                    }
                    for chamber in eq.chambers  # type: ignore
                ]
            
            # Nozzles - access via direct pyDEXPI property
            if eq.nozzles:  # type: ignore
                sub_components['nozzles'] = [
                    {
                        'id': str(nozzle.id),
                        'tag_name': str(nozzle.subTagName or ''),
                        'type': nozzle.__class__.__name__
                    }
                    for nozzle in eq.nozzles  # type: ignore
                ]
            
            # Motors - access via direct pyDEXPI property
            if eq.motors:  # type: ignore
                sub_components['motors'] = [
                    {
                        'id': str(motor.id),
                        'tag_name': str(motor.subTagName or ''),
                        'type': motor.__class__.__name__
                    }
                    for motor in eq.motors  # type: ignore
                ]
            
            if sub_components:
                equipment[eq_id]['sub_components'] = sub_components
        
        except Exception as e:
            print(f"Warning: Error extracting equipment {eq}: {e}")
            continue
    
    return equipment


def extract_instruments(dexpi_model: DexpiModel) -> Dict[str, Dict[str, Any]]:
    """Extract instruments using pyDEXPI ProcessInstrumentationFunction API.
    
    Uses official pyDEXPI API to access instrumentation through:
    - ProcessInstrumentationFunctions.actuatingFunctions (control instruments)
    - ProcessInstrumentationFunctions.processSignalGeneratingFunctions (measurement)
    - Direct ProcessSignalGeneratingSystems and ActuatingSystems for fallback
    
    Args:
        dexpi_model: DexpiModel instance loaded via ProteusSerializer.load()
    
    Returns:
        Dictionary mapping instrument IDs to metadata including type and variables
    """
    instruments = {}
    
    if not dexpi_model.conceptualModel:
        return instruments
    
    conceptual_model = dexpi_model.conceptualModel
    
    # ========================================================================
    # Extract instruments via ProcessInstrumentationFunctions API
    # ========================================================================
    # This accesses the parent function decomposition's child functions directly
    for p_inst_fn in conceptual_model.processInstrumentationFunctions:
        try:
            fn_id = str(p_inst_fn.id)
            fn_number = p_inst_fn.processInstrumentationFunctionNumber or fn_id
            
            # Extract actuating functions (control instruments) using direct API access
            for act_fn in p_inst_fn.actuatingFunctions:
                inst_id = str(act_fn.id)
                tag_name = act_fn.actuatingFunctionNumber or inst_id  # type: ignore
                
                instruments[inst_id] = {
                    'id': inst_id,
                    'tag_name': str(tag_name),
                    'type': 'ActuatingFunction',
                    'parent_function': str(fn_number),
                    'element': 'ActuatingSystem'
                }
            
            # Extract signal generating functions (measurement) using direct API access
            for sig_gen_fn in p_inst_fn.processSignalGeneratingFunctions:
                inst_id = str(sig_gen_fn.id)
                tag_name = (
                    sig_gen_fn.processSignalGeneratingFunctionNumber or
                    inst_id
                )
                
                instruments[inst_id] = {
                    'id': inst_id,
                    'tag_name': str(tag_name),
                    'type': 'ProcessSignalGeneratingFunction',
                    'sensor_type': str(sig_gen_fn.sensorType or ''),
                    'parent_function': str(fn_number),
                    'element': 'MeasuringSystem'
                }
        
        except Exception as e:
            print(f"Warning: Error extracting from ProcessInstrumentationFunction: {e}")
            continue
    
    # ========================================================================
    # Fallback: Extract direct ProcessSignalGeneratingSystems
    # ========================================================================
    for psgs in conceptual_model.processSignalGeneratingSystems:
        try:
            inst_id = str(psgs.id)
            tag_name = psgs.processSignalGeneratingSystemNumber or inst_id
            
            instruments[inst_id] = {
                'id': inst_id,
                'tag_name': str(tag_name),
                'type': 'ProcessSignalGeneratingSystem',
                'element': 'MeasuringSystem'
            }
        except Exception as e:
            print(f"Warning: Error extracting ProcessSignalGeneratingSystem: {e}")
            continue
    
    # ========================================================================
    # Fallback: Extract direct ActuatingSystems
    # ========================================================================
    for act_sys in conceptual_model.actuatingSystems:
        try:
            inst_id = str(act_sys.id)
            tag_name = act_sys.actuatingSystemNumber or inst_id
            
            instruments[inst_id] = {
                'id': inst_id,
                'tag_name': str(tag_name),
                'type': 'ActuatingSystem',
                'element': 'ActuatingSystem'
            }
        except Exception as e:
            print(f"Warning: Error extracting ActuatingSystem: {e}")
            continue
    
    return instruments


def extract_connections(dexpi_model: DexpiModel) -> Dict[str, Dict[str, Any]]:
    """Extract process connections using pyDEXPI PipingNetworkSystems API.
    
    Uses official pyDEXPI API to access connections through hierarchical API:
    - ConceptualModel.pipingNetworkSystems (list of PipingNetworkSystem)
    - PipingNetworkSystem.segments (list of PipingNetworkSegment)
    - PipingNetworkSegment.connections (list of PipingConnection)
    
    All attributes accessed directly, not via getattr().
    
    Args:
        dexpi_model: DexpiModel instance loaded via ProteusSerializer.load()
    
    Returns:
        Dictionary mapping connection IDs to source/target flow information
    """
    connections = {}
    
    if not dexpi_model.conceptualModel:
        return connections
    
    conceptual_model = dexpi_model.conceptualModel
    
    # Access PipingNetworkSystems using direct pyDEXPI API (NOT getattr)
    for pn_system in conceptual_model.pipingNetworkSystems:
        try:
            system_id = str(pn_system.id)
            system_number = pn_system.pipingNetworkSystemGroupNumber or system_id
            
            # Access segments within piping network system directly via API
            for segment in pn_system.segments:
                try:
                    segment_id = str(segment.id)
                    segment_number = segment.segmentNumber or segment_id
                    
                    # Access connections within segment directly via API
                    for conn in segment.connections:
                        try:
                            conn_id = str(conn.id)
                            
                            # Get source and target using direct pyDEXPI API properties
                            source_item = conn.sourceItem
                            target_item = conn.targetItem
                            
                            source_id = str(source_item.id) if source_item else ''
                            target_id = str(target_item.id) if target_item else ''
                            
                            connections[conn_id] = {
                                'id': conn_id,
                                'from_item': source_id,
                                'to_item': target_id,
                                'type': conn.__class__.__name__,
                                'segment': str(segment_number),
                                'piping_network': str(system_number),
                                'element': 'PipingConnection'
                            }
                        except Exception as e:
                            print(f"Warning: Error extracting connection in segment: {e}")
                            continue
                
                except Exception as e:
                    print(f"Warning: Error extracting segment from piping network: {e}")
                    continue
        
        except Exception as e:
            print(f"Warning: Error extracting PipingNetworkSystem: {e}")
            continue
    
    return connections
