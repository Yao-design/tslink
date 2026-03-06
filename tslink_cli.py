#!/usr/bin/env python3
"""
@file tslink_cli.py
@brief TS-Link CLI Tool - Spec converter and validator

Usage:
    # Validate Spec
    python tslink_cli.py -i HeartRate.yaml
    
    # Generate C Header
    python tslink_cli.py -i HeartRate.yaml -t c -o ./firmware/
    
    # Generate JSON
    python tslink_cli.py -i HeartRate.yaml -t json -o ./app/
    
    # Generate Markdown
    python tslink_cli.py -i HeartRate.yaml -t markdown -o ./docs/
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Tuple


try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_PARAMETER_ERROR = 2
EXIT_IO_ERROR = 3

# Valid formats (scalar and array)
VALID_FORMATS = {
    'u8', 'u16', 'u32', 'i8', 'i16', 'i32', 'f32', 'bool', 'void',
    'u8[]', 'u16[]', 'u32[]', 'i8[]', 'i16[]', 'i32[]', 'f32[]', 'bool[]'
}

# C keywords to check for name collision
C_KEYWORDS = {
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
    'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
    'inline', 'int', 'long', 'register', 'restrict', 'return', 'short',
    'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
    'unsigned', 'void', 'volatile', 'while'
}


def print_error(message: str):
    """Print error message to stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def print_success(message: str):
    """Print success message."""
    print(f"[OK] {message}")


class SpecValidator:
    """Validator for TS-Link YAML Spec."""
    
    def __init__(self, spec_path: Path, spec_data: dict):
        self.spec_path = spec_path
        self.spec = spec_data
        self.errors = []
    
    def add_error(self, message: str, line: int = None):
        """Add validation error."""
        if line:
            self.errors.append(f"{self.spec_path}:{line} - {message}")
        else:
            self.errors.append(f"{self.spec_path} - {message}")
    
    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        self._validate_root_fields()
        self._validate_uplink()
        self._validate_downlink()
        return len(self.errors) == 0
    
    def _validate_root_fields(self):
        """Validate root-level required fields."""
        # Check deviceType
        if 'deviceType' not in self.spec:
            self.add_error("Missing required field: deviceType")
        elif not isinstance(self.spec['deviceType'], str):
            self.add_error("deviceType must be a string")
        
        # Check version
        if 'version' not in self.spec:
            self.add_error("Missing required field: version")
        elif not isinstance(self.spec['version'], str):
            self.add_error("version must be a string")
    
    def _validate_field(self, field: dict, context: str, index: int) -> bool:
        """Validate a single field (uplink or downlink entry)."""
        valid = True
        prefix = f"{context}[{index}]"
        
        # Check required fields
        if 'id' not in field:
            self.add_error(f"{prefix}: Missing required field: id")
            valid = False
        
        if 'name' not in field:
            self.add_error(f"{prefix}: Missing required field: name")
            valid = False
        
        if 'format' not in field:
            self.add_error(f"{prefix}: Missing required field: format")
            valid = False
        
        if not valid:
            return False
        
        # Validate id
        field_id = field['id']
        if isinstance(field_id, int):
            # Convert int to hex string for validation
            if field_id < 0 or field_id > 255:
                self.add_error(f"{prefix}: ID out of range: {field_id} (must be 0x01 - 0xFF)")
                valid = False
            elif field_id == 0:
                self.add_error(f"{prefix}: ID cannot be 0x00")
                valid = False
        elif isinstance(field_id, str):
            if not re.match(r'^0x[0-9a-fA-F]{2}$', field_id):
                self.add_error(f"{prefix}: Invalid ID format '{field_id}' (must be 0x01 - 0xFF)")
                valid = False
            else:
                id_val = int(field_id, 16)
                if id_val == 0:
                    self.add_error(f"{prefix}: ID cannot be 0x00")
                    valid = False
        else:
            self.add_error(f"{prefix}: ID must be a hex string (e.g., '0x01') or integer")
            valid = False
        
        # Validate name
        name = field['name']
        if not isinstance(name, str):
            self.add_error(f"{prefix}: name must be a string")
            valid = False
        elif not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            self.add_error(f"{prefix}: Invalid name '{name}': must be a valid C identifier")
            valid = False
        elif name in C_KEYWORDS:
            self.add_error(f"{prefix}: Invalid name '{name}': cannot be a C keyword")
            valid = False
        
        # Validate format
        fmt = field['format']
        if fmt not in VALID_FORMATS:
            self.add_error(f"{prefix}: Invalid format '{fmt}': expected one of {', '.join(sorted(VALID_FORMATS))}")
            valid = False
        
        return valid
    
    def _validate_uplink(self):
        """Validate uplink fields."""
        uplink = self.spec.get('uplink', [])
        if not isinstance(uplink, list):
            self.add_error("uplink must be a list")
            return
        
        ids = set()
        for i, field in enumerate(uplink):
            if not isinstance(field, dict):
                self.add_error(f"uplink[{i}]: must be an object")
                continue
            
            if self._validate_field(field, 'uplink', i):
                # Check ID uniqueness
                field_id = field['id']
                id_key = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                if id_key in ids:
                    self.add_error(f"Duplicate uplink id: {id_key}")
                ids.add(id_key)
    
    def _validate_downlink(self):
        """Validate downlink fields."""
        downlink = self.spec.get('downlink', [])
        if not isinstance(downlink, list):
            self.add_error("downlink must be a list")
            return
        
        ids = set()
        for i, field in enumerate(downlink):
            if not isinstance(field, dict):
                self.add_error(f"downlink[{i}]: must be an object")
                continue
            
            if self._validate_field(field, 'downlink', i):
                # Check ID uniqueness
                field_id = field['id']
                id_key = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                if id_key in ids:
                    self.add_error(f"Duplicate downlink id: {id_key}")
                ids.add(id_key)


class CHeaderGenerator:
    """Generator for C Header files."""
    
    def generate(self, spec: dict, filename: str) -> str:
        """Generate C header content."""
        device_type = spec.get('deviceType', 'UNKNOWN')
        full_name = spec.get('fullName', device_type)
        description = spec.get('description', '')
        version = spec.get('version', '1.0.0')
        uplink = spec.get('uplink', [])
        downlink = spec.get('downlink', [])
        
        # Upper case device type for macros
        dt_upper = device_type.upper()
        
        lines = [
            f"/**",
            f" * @file {filename}",
            f" * @brief Auto-generated by tslink_cli.py",
            f" */",
            f"",
            f"#ifndef TSLINK_{dt_upper}_H",
            f"#define TSLINK_{dt_upper}_H",
            f"",
            f"#define TSLINK_{dt_upper}_DEVICE_TYPE \"{device_type}\"",
        ]
        
        if full_name != device_type:
            lines.append(f"#define TSLINK_{dt_upper}_FULL_NAME \"{full_name}\"")
        
        if description:
            escaped_desc = description.replace('"', '\\"')
            lines.append(f"#define TSLINK_{dt_upper}_DESCRIPTION \"{escaped_desc}\"")
        
        lines.append(f"#define TSLINK_{dt_upper}_VERSION \"{version}\"")
        lines.append("")
        
        # Uplink IDs
        if uplink:
            lines.append("// Uplink IDs")
            for field in uplink:
                name = field['name'].upper()
                field_id = field['id']
                id_val = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                lines.append(f"#define TSLINK_{dt_upper}_UPLINK_{name} {id_val}")
            lines.append("")
        
        # Downlink IDs
        if downlink:
            lines.append("// Downlink IDs")
            for field in downlink:
                name = field['name'].upper()
                field_id = field['id']
                id_val = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                lines.append(f"#define TSLINK_{dt_upper}_DOWNLINK_{name} {id_val}")
            lines.append("")
        
        lines.append("#endif")
        
        return '\n'.join(lines)


class JSONGenerator:
    """Generator for JSON files."""
    
    def generate(self, spec: dict) -> str:
        """Generate JSON content."""
        # Normalize IDs to hex strings
        output = {
            'deviceType': spec.get('deviceType', ''),
            'fullName': spec.get('fullName', spec.get('deviceType', '')),
            'description': spec.get('description', ''),
            'version': spec.get('version', ''),
        }
        
        # Process uplink
        uplink = spec.get('uplink', [])
        output['uplink'] = []
        for field in uplink:
            field_id = field['id']
            normalized = {
                'id': field_id if isinstance(field_id, str) else f"0x{field_id:02x}",
                'name': field['name'],
                'format': field['format'],
                'description': field.get('description', ''),
            }
            if 'unit' in field:
                normalized['unit'] = field['unit']
            output['uplink'].append(normalized)
        
        # Process downlink
        downlink = spec.get('downlink', [])
        output['downlink'] = []
        for field in downlink:
            field_id = field['id']
            normalized = {
                'id': field_id if isinstance(field_id, str) else f"0x{field_id:02x}",
                'name': field['name'],
                'format': field['format'],
                'description': field.get('description', ''),
            }
            if 'unit' in field:
                normalized['unit'] = field['unit']
            output['downlink'].append(normalized)
        
        return json.dumps(output, indent=2, ensure_ascii=False)


class TSGenerator:
    """Generator for TypeScript spec files."""
    
    def generate(self, specs: dict) -> str:
        """Generate TypeScript content with all specs."""
        lines = [
            "import { Spec, SpecField } from './types';",
            "",
            "export const specs: Record<string, Spec> = {",
        ]
        
        for device_type, spec in specs.items():
            lines.append(f'  "{device_type}": {{')
            lines.append(f'    deviceType: "{spec.get("deviceType", "")}",')
            
            full_name = spec.get('fullName', '')
            if full_name:
                lines.append(f'    fullName: "{full_name}",')
            
            description = spec.get('description', '')
            if description:
                lines.append(f'    description: "{description}",')
            
            lines.append(f'    version: "{spec.get("version", "")}",')
            
            # Uplink
            uplink = spec.get('uplink', [])
            lines.append('    uplink: [')
            for field in uplink:
                field_id = field['id']
                id_val = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                field_parts = [f'id: "{id_val}"', f'name: "{field["name"]}"', f'format: "{field["format"]}"']
                if field.get('description'):
                    field_parts.append(f'description: "{field["description"]}"')
                if field.get('unit'):
                    field_parts.append(f'unit: "{field["unit"]}"')
                lines.append('      { ' + ', '.join(field_parts) + ' },')
            lines.append('    ],')
            
            # Downlink
            downlink = spec.get('downlink', [])
            lines.append('    downlink: [')
            for field in downlink:
                field_id = field['id']
                id_val = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                field_parts = [f'id: "{id_val}"', f'name: "{field["name"]}"', f'format: "{field["format"]}"']
                if field.get('description'):
                    field_parts.append(f'description: "{field["description"]}"')
                if field.get('unit'):
                    field_parts.append(f'unit: "{field["unit"]}"')
                lines.append('      { ' + ', '.join(field_parts) + ' },')
            lines.append('    ],')
            
            lines.append('  },')
        
        lines.append('};')
        
        return '\n'.join(lines)


class MarkdownGenerator:
    """Generator for Markdown documentation."""
    
    def generate(self, spec: dict) -> str:
        """Generate Markdown content."""
        device_type = spec.get('deviceType', 'UNKNOWN')
        full_name = spec.get('fullName', device_type)
        description = spec.get('description', '')
        version = spec.get('version', '')
        uplink = spec.get('uplink', [])
        downlink = spec.get('downlink', [])
        
        lines = [
            f"# Device: {full_name}",
            "",
            f"**Type**: `{device_type}`",
            "",
            f"**Version**: {version}",
            "",
        ]
        
        if description:
            lines.extend([f"**Description**: {description}", ""])
        
        # Uplink section
        if uplink:
            lines.extend(["## Uplink", ""])
            lines.append("| ID | Name | Format | Unit | Description |")
            lines.append("|----|------|--------|------|-------------|")
            for field in uplink:
                field_id = field['id']
                id_val = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                name = field['name']
                fmt = field['format']
                unit = field.get('unit', '-')
                desc = field.get('description', '-')
                lines.append(f"| {id_val} | {name} | {fmt} | {unit} | {desc} |")
            lines.append("")
        
        # Downlink section
        if downlink:
            lines.extend(["## Downlink", ""])
            lines.append("| ID | Name | Format | Description |")
            lines.append("|----|------|--------|-------------|")
            for field in downlink:
                field_id = field['id']
                id_val = field_id if isinstance(field_id, str) else f"0x{field_id:02x}"
                name = field['name']
                fmt = field['format']
                desc = field.get('description', '-')
                lines.append(f"| {id_val} | {name} | {fmt} | {desc} |")
            lines.append("")
        
        return '\n'.join(lines)


def validate_spec(input_path: Path) -> Tuple[bool, dict]:
    """Validate YAML spec file. Returns (is_valid, spec_data)."""
    # Check file exists
    if not input_path.exists():
        print_error(f"File not found: {input_path}")
        return False, None
    
    # Parse YAML
    try:
        content = input_path.read_text(encoding='utf-8')
        spec = yaml.safe_load(content)
    except yaml.YAMLError as e:
        print_error(f"YAML syntax error: {e}")
        return False, None
    except Exception as e:
        print_error(f"Failed to read file: {e}")
        return False, None
    
    # Validate spec structure
    if not isinstance(spec, dict):
        print_error("YAML root must be an object")
        return False, None
    
    validator = SpecValidator(input_path, spec)
    if not validator.validate():
        for error in validator.errors:
            print_error(error)
        return False, None
    
    return True, spec


def validate_specs_from_dir(input_dir: Path) -> Tuple[bool, dict]:
    """Validate all YAML spec files in directory. Returns (is_valid, specs_dict)."""
    if not input_dir.exists():
        print_error(f"Directory not found: {input_dir}")
        return False, None
    
    if not input_dir.is_dir():
        print_error(f"Input path is not a directory: {input_dir}")
        return False, None
    
    yaml_files = list(input_dir.glob('*.yaml'))
    if not yaml_files:
        print_error(f"No YAML files found in: {input_dir}")
        return False, None
    
    specs = {}
    all_valid = True
    
    for yaml_file in sorted(yaml_files):
        is_valid, spec = validate_spec(yaml_file)
        if not is_valid:
            all_valid = False
            continue
        
        device_type = spec.get('deviceType')
        if device_type:
            specs[device_type] = spec
            print_success(f"Valid: {yaml_file}")
        else:
            print_error(f"{yaml_file}: Missing deviceType")
            all_valid = False
    
    if not all_valid:
        return False, None
    
    return True, specs


def generate_output(spec: dict, output_type: str, input_path: Path, output_dir: Path) -> int:
    """Generate output file. Returns exit code."""
    # Determine output filename
    base_name = input_path.stem
    generators = {
        'c': (CHeaderGenerator(), f"{base_name}.h"),
        'json': (JSONGenerator(), f"{base_name}.json"),
        'markdown': (MarkdownGenerator(), f"{base_name}.md"),
    }
    
    if output_type not in generators:
        print_error(f"Invalid output type: {output_type} (must be c, json, markdown, or ts)")
        return EXIT_PARAMETER_ERROR
    
    generator, filename = generators[output_type]
    
    # Ensure output directory exists
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print_error(f"Failed to create output directory: {e}")
        return EXIT_IO_ERROR
    
    # Generate content
    try:
        if output_type == 'c':
            content = generator.generate(spec, filename)
        else:
            content = generator.generate(spec)
    except Exception as e:
        print_error(f"Failed to generate output: {e}")
        return EXIT_IO_ERROR
    
    # Write output file
    output_path = output_dir / filename
    try:
        output_path.write_text(content, encoding='utf-8')
    except Exception as e:
        print_error(f"Failed to write output file: {e}")
        return EXIT_IO_ERROR
    
    print_success(f"Generated: {output_path}")
    return EXIT_SUCCESS


def generate_ts_output(specs: dict, output_path: Path) -> int:
    """Generate TypeScript output file. Returns exit code."""
    generator = TSGenerator()
    
    try:
        content = generator.generate(specs)
    except Exception as e:
        print_error(f"Failed to generate output: {e}")
        return EXIT_IO_ERROR
    
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
    except Exception as e:
        print_error(f"Failed to write output file: {e}")
        return EXIT_IO_ERROR
    
    print_success(f"Generated: {output_path}")
    return EXIT_SUCCESS


def generate_router_output(specs: dict, output_path: Path, pages_json_path: str, devices_dir: str) -> int:
    """
    生成路由映射表并更新 pages.json

    参数：
        specs: 从 validate_specs_from_dir 获取的 specs 字典
        output_path: 路由映射表输出路径
        pages_json_path: pages.json 文件路径
        devices_dir: devices 目录路径
    """
    pages_json_file = Path(pages_json_path)
    devices_path = Path(devices_dir)

    # 1. 扫描已实现的专属页面
    implemented_pages = set()
    if devices_path.exists():
        for vue_file in devices_path.glob('*.vue'):
            device_type = vue_file.stem
            implemented_pages.add(device_type)

    # 2. 生成路由映射表
    route_map = {}
    for device_type in specs.keys():
        if device_type in implemented_pages:
            route_map[device_type] = f'pages/devices/{device_type}'
        else:
            route_map[device_type] = 'pages/common/generic-device'

    # 3. 写入路由映射表
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(route_map, indent=2, ensure_ascii=False), encoding='utf-8')
    print_success(f"Generated route map: {output_path}")

    # 4. 更新 pages.json
    _update_pages_json(pages_json_file, route_map, specs)
    print_success(f"Updated pages.json: {pages_json_file}")

    return EXIT_SUCCESS


def _update_pages_json(pages_json_path: Path, route_map: dict, specs: dict):
    """
    更新 pages.json，静态注册所有设备页面

    建设过程：
    1. 从空列表开始
    2. 添加所有非 devices 目录下的页面
    3. 添加所有设备专属页面（来自 route_map）
    """
    # 读取现有 pages.json
    with open(pages_json_path, 'r', encoding='utf-8') as f:
        pages_config = json.load(f)

    # 1. 从空列表开始，添加所有非 devices 目录下的页面
    new_pages = []
    for page in pages_config.get('pages', []):
        if not page['path'].startswith('pages/devices/'):
            new_pages.append(page)

    # 2. 收集设备专属页面（去重）
    device_pages = set()
    for page_path in route_map.values():
        if page_path.startswith('pages/devices/'):
            device_pages.add(page_path)

    # 3. 添加设备专属页面配置
    for page_path in sorted(device_pages):
        device_type = page_path.split('/')[-1]
        spec = specs.get(device_type, {})
        # 使用 fullName 作为导航栏标题，如果没有则使用 deviceType
        title = spec.get('fullName', device_type)
        new_pages.append({
            'path': page_path,
            'style': {
                'navigationBarTitleText': title
            }
        })

    # 更新 pages 配置
    pages_config['pages'] = new_pages

    # 写回
    with open(pages_json_path, 'w', encoding='utf-8') as f:
        json.dump(pages_config, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description='TS-Link CLI Tool - Spec converter and validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate Spec
  python tslink_cli.py -i HeartRate.yaml

  # Generate C Header
  python tslink_cli.py -i HeartRate.yaml -t c -o ./firmware/

  # Generate JSON
  python tslink_cli.py -i HeartRate.yaml -t json -o ./app/

  # Generate Markdown
  python tslink_cli.py -i HeartRate.yaml -t markdown -o ./docs/

  # Generate TypeScript (reads all specs from directory)
  python tslink_cli.py -t ts -i ./specs/ -o specs.ts

  # Generate Router Map and update pages.json
  python tslink_cli.py -t router -i ./specs -o src/router_map.json
        """
    )
    
    parser.add_argument('-i', '--input', required=True, 
                        help='Input YAML file path (required)')
    parser.add_argument('-t', '--type', choices=['c', 'json', 'markdown', 'ts', 'router'],
                        help='Output type: c, json, markdown, ts, or router (required for generation)')
    parser.add_argument('-o', '--output', default='.',
                        help='Output directory or file (default: current directory)')
    parser.add_argument('--pages-json',
                        default='./pages.json',
                        help='Path to pages.json (for router type)')
    parser.add_argument('--devices-dir',
                        default='./pages/devices',
                        help='Path to devices directory (for router type)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Handle ts mode specially (reads directory, outputs single file)
    if args.type == 'ts':
        is_valid, specs = validate_specs_from_dir(input_path)
        if not is_valid:
            return EXIT_VALIDATION_ERROR
        return generate_ts_output(specs, output_path)

    # Handle router mode specially (generates route map and updates pages.json)
    if args.type == 'router':
        is_valid, specs = validate_specs_from_dir(input_path)
        if not is_valid:
            return EXIT_VALIDATION_ERROR
        return generate_router_output(specs, output_path, args.pages_json, args.devices_dir)
    
    # Validate spec
    is_valid, spec = validate_spec(input_path)
    if not is_valid:
        return EXIT_VALIDATION_ERROR
    
    print_success(f"Valid: {input_path}")
    
    # If no output type specified, just validate
    if not args.type:
        return EXIT_SUCCESS
    
    # Generate output
    output_dir = output_path if output_path.is_dir() else output_path.parent
    return generate_output(spec, args.type, input_path, output_dir)


if __name__ == '__main__':
    sys.exit(main())
