"""
Validation utilities for OPSEE RO-Crates and DEXPI files.

This module provides validation functions for:
- RO-Crate metadata structure and completeness
- DEXPI XML files
- OPSEE profile compliance
"""

from typing import Dict, List, Tuple, Any
from pathlib import Path
import json
import logging

from jsonschema import validate as json_validate, ValidationError, Draft7Validator
from lxml import etree

logger = logging.getLogger(__name__)


def validate_crate(metadata_path: str) -> Dict[str, Any]:
    """
    Validate an RO-Crate metadata file.
    
    Args:
        metadata_path: Path to ro-crate-metadata.json
    
    Returns:
        Dictionary with validation results:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str]
        }
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Check basic RO-Crate structure
        if '@context' not in metadata:
            result['errors'].append("Missing @context")
            result['valid'] = False
        
        if '@graph' not in metadata:
            result['errors'].append("Missing @graph")
            result['valid'] = False
            return result
        
        graph = metadata['@graph']
        
        # Check for required entities following RO-Crate 1.1 specification
        # Root entity ('./')  describes the dataset
        # Metadata descriptor describes the metadata file itself
        root_entity = None
        metadata_entity = None
        
        for entity in graph:
            entity_id = entity.get('@id', '')
            if entity_id == './':
                root_entity = entity
            elif 'ro-crate-metadata.json' in entity_id:
                metadata_entity = entity
        
        if not root_entity:
            result['errors'].append("Missing root data entity (./)")
            result['valid'] = False
        
        if not metadata_entity:
            result['errors'].append("Missing metadata descriptor entity")
            result['valid'] = False
        
        # Check root entity properties
        if root_entity:
            if '@type' not in root_entity:
                result['warnings'].append("Root entity missing @type")
            
            if 'name' not in root_entity:
                result['warnings'].append("Root entity missing name")
            
            if 'description' not in root_entity:
                result['warnings'].append("Root entity missing description")
        
        # Check for authors
        has_authors = False
        if root_entity and 'author' in root_entity:
            has_authors = True
        
        if not has_authors:
            result['warnings'].append("No authors specified")
        
        # Check for OPSEE profile conformance
        if root_entity and 'conformsTo' in root_entity:
            if 'opsee' in str(root_entity['conformsTo']).lower():
                logger.info("Crate conforms to OPSEE profile")
        
        logger.info(f"Validation complete: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
        
    except FileNotFoundError:
        result['valid'] = False
        result['errors'].append(f"File not found: {metadata_path}")
    except json.JSONDecodeError as e:
        result['valid'] = False
        result['errors'].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_dexpi(xml_path: str) -> Dict[str, Any]:
    """
    Validate a DEXPI XML file.
    
    Args:
        xml_path: Path to DEXPI XML file
    
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Parse XML
        tree = etree.parse(xml_path)
        root = tree.getroot()
        
        # Check for basic DEXPI structure
        # Look for Equipment or similar elements
        equipment = root.xpath('.//*[local-name()="Equipment"]')
        instruments = root.xpath('.//*[local-name()="ActuatingSystem" or local-name()="Instrument"]')
        
        if not equipment and not instruments:
            result['warnings'].append("No equipment or instruments found")
        
        # Check for TagName attributes
        all_components = equipment + instruments
        missing_tags = 0
        
        for comp in all_components:
            if not comp.get('TagName') and not comp.get('Tag'):
                missing_tags += 1
        
        if missing_tags > 0:
            result['warnings'].append(f"{missing_tags} components missing TagName attribute")
        
        logger.info(f"DEXPI validation: {len(equipment)} equipment, {len(instruments)} instruments")
        
    except etree.XMLSyntaxError as e:
        result['valid'] = False
        result['errors'].append(f"XML syntax error: {str(e)}")
    except FileNotFoundError:
        result['valid'] = False
        result['errors'].append(f"File not found: {xml_path}")
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_profile(metadata_path: str, profile_schema_path: str) -> Dict[str, Any]:
    """
    Validate RO-Crate against OPSEE profile schema.
    
    Args:
        metadata_path: Path to ro-crate-metadata.json
        profile_schema_path: Path to OPSEE profile JSON schema
    
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Load metadata and schema
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        with open(profile_schema_path, 'r') as f:
            schema = json.load(f)
        
        # Validate against schema
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(metadata))
        
        if errors:
            result['valid'] = False
            for error in errors:
                result['errors'].append(f"{error.message} at {'.'.join(str(p) for p in error.path)}")
        
        logger.info(f"Profile validation: {len(errors)} errors")
        
    except FileNotFoundError as e:
        result['valid'] = False
        result['errors'].append(f"File not found: {str(e)}")
    except json.JSONDecodeError as e:
        result['valid'] = False
        result['errors'].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_file_links(metadata_path: str, crate_root: str) -> Dict[str, Any]:
    """
    Validate that all files referenced in the crate actually exist.
    
    Args:
        metadata_path: Path to ro-crate-metadata.json
        crate_root: Root directory of the crate
    
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'missing_files': []
    }
    
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        crate_path = Path(crate_root)
        graph = metadata.get('@graph', [])
        
        # Find all File entities
        for entity in graph:
            # Normalize @type to list for consistent processing
            entity_type = entity.get('@type', [])
            if not isinstance(entity_type, list):
                entity_type = [entity_type]
            
            if 'File' in entity_type:
                file_id = entity.get('@id', '')
                
                # Skip special files
                if 'ro-crate-metadata' in file_id or file_id.startswith('http'):
                    continue
                
                # Check if file exists
                file_path = crate_path / file_id
                if not file_path.exists():
                    result['missing_files'].append(file_id)
                    result['warnings'].append(f"Referenced file not found: {file_id}")
        
        if result['missing_files']:
            logger.warning(f"{len(result['missing_files'])} files missing from crate")
        
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def comprehensive_validation(crate_dir: str) -> Dict[str, Any]:
    """
    Run all validation checks on an RO-Crate.
    
    Args:
        crate_dir: Root directory of the RO-Crate
    
    Returns:
        Combined validation results
    """
    crate_path = Path(crate_dir)
    metadata_path = crate_path / 'ro-crate-metadata.json'
    
    results = {
        'crate_validation': validate_crate(str(metadata_path)),
        'file_links': validate_file_links(str(metadata_path), str(crate_path))
    }
    
    # Check if DEXPI file exists and validate
    # Automatically discovers DEXPI files by conformsTo property
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        for entity in metadata.get('@graph', []):
            if entity.get('conformsTo') == 'https://www.dexpi.org/':
                dexpi_file = crate_path / entity.get('@id', '')
                if dexpi_file.exists():
                    results['dexpi_validation'] = validate_dexpi(str(dexpi_file))
    except:
        pass
    
    # Determine overall validity
    all_valid = all(r.get('valid', True) for r in results.values())
    results['overall_valid'] = all_valid
    
    return results
