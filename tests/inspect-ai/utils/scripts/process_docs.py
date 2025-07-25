import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert XML documentation to structured JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.xml output.json
  %(prog)s --input docs.xml --output result.json
  %(prog)s -i data.xml -o formatted.json
        """,
    )

    parser.add_argument("input_file", nargs="?", help="Input XML file path")

    parser.add_argument("output_file", nargs="?", help="Output JSON file path")

    parser.add_argument(
        "-i",
        "--input",
        dest="input_file_alt",
        help="Input XML file path (alternative to positional argument)",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file_alt",
        help="Output JSON file path (alternative to positional argument)",
    )

    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> tuple[Path, Path]:
    """Validate and process command-line arguments."""
    input_file = args.input_file or args.input_file_alt
    if not input_file:
        print("Error: Input file is required", file=sys.stderr)
        sys.exit(1)

    output_file = args.output_file or args.output_file_alt
    if not output_file:
        print("Error: Output file is required", file=sys.stderr)
        sys.exit(1)

    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    if input_path.suffix.lower() != ".xml":
        print(f"Warning: Input file '{input_path}' does not have .xml extension")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    return input_path, output_path


def parse_parameters_from_text(method_text: str) -> str:
    """
    Parses a block of text for a specific method to find and format its parameters.
    """
    params_match = re.search(
        r"#### Parameters.*?\n((?:\|.*?\n)+)", method_text, re.DOTALL
    )
    if not params_match:
        param_code_match = re.search(
            r"#### Parameters\s*\n\s*<code>(.*?)</code>", method_text, re.DOTALL
        )
        if param_code_match:
            code_content = param_code_match.group(1)
            params = re.findall(
                r'<span class="parameter-name">(.*?)</span>', code_content
            )
            return ", ".join(params)
        return ""

    params_table_text = params_match.group(1)
    lines = params_table_text.strip().split("\n")

    if len(lines) < 3:
        return ""

    param_lines = lines[2:]
    parameters: List[str] = []
    for line in param_lines:
        parts = [p.strip() for p in line.strip().split("|") if p.strip()]
        if len(parts) >= 2:
            name = parts[0].replace("`", "")
            type_str = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", parts[1])
            type_str = type_str.replace("`", "").replace("\n", " ")
            parameters.append(f"{name} ({type_str})")

    return ", ".join(parameters)


def parse_qmd_content(content: str) -> Optional[Dict[str, Any]]:
    """
    Parses the content of a .qmd file to extract controller and method information.
    """
    data: Dict[str, Any] = {}
    lines = content.strip().split("\n")

    controller_match = re.match(r"# ([\w\.]+) {.*}", lines[0])
    if not controller_match:
        return None

    data["controller_name"] = controller_match.group(1)
    methods: List[Dict[str, Any]] = []
    data["methods"] = methods

    try:
        methods_table_start_index = next(
            i for i, line in enumerate(lines) if "## Methods" in line
        )
    except StopIteration:
        return data

    first_method_def_index = len(lines)
    try:
        first_method_def_index = next(
            i
            for i, line in enumerate(lines)
            if line.startswith("### ") and i > methods_table_start_index
        )
    except StopIteration:
        pass

    methods_table_lines = lines[methods_table_start_index + 3 : first_method_def_index]
    for line in methods_table_lines:
        if not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().split("|") if p.strip()]
        if len(parts) < 2:
            continue
        method_name_md, description = parts[0], parts[1]
        method_name_match = re.search(r"\[([\w_]+)\]", method_name_md)
        if not method_name_match:
            continue
        method_name = method_name_match.group(1)

        parameters_str = ""
        method_detail_regex = re.compile(
            r"### " + re.escape(method_name) + r" {.*?}(.*?)(?=\n### |\Z)", re.DOTALL
        )
        method_detail_match = method_detail_regex.search(content)

        if method_detail_match:
            method_text = method_detail_match.group(1)
            parameters_str = parse_parameters_from_text(method_text)

        methods.append(
            {
                "name": method_name,
                "description": description.strip(),
                "parameters": parameters_str,
            }
        )
    return data


def convert_xml_to_json(xml_file_path: Path) -> str:
    """
    Parses an XML file containing multiple .qmd docs and converts it to a
    structured JSON object containing controller and method information.
    """
    try:
        with open(xml_file_path, "r", encoding="utf-8") as f:
            xml_content = f.read()

        def cdata_replacer(match: re.Match[str]) -> str:
            path = match.group(1)
            content = match.group(2)
            content = content.replace("]]>", "]]&gt;")
            return f'<file path="{path}"><![CDATA[{content}]]></file>'

        xml_content_cdata = re.sub(
            r'<file path="(.*?)">(.*?)</file>',
            cdata_replacer,
            xml_content,
            flags=re.DOTALL,
        )

        rooted_xml_content = f"<root>{xml_content_cdata}</root>"

        root = ET.fromstring(rooted_xml_content)

    except (ET.ParseError, FileNotFoundError) as e:
        return json.dumps({"error": str(e)}, indent=2)

    all_controllers_data: List[Dict[str, Any]] = []
    files_element = root.find("files")

    if files_element is None:
        return json.dumps({"error": "No <files> element found in XML"}, indent=2)

    for file_elem in files_element.findall("file"):
        path = file_elem.get("path")
        if path and (
            path.startswith("playwright.controller.") or path == "run.ShinyAppProc.qmd"
        ):
            content = file_elem.text
            if content:
                controller_data = parse_qmd_content(content)
                if controller_data and controller_data.get("methods"):
                    all_controllers_data.append(controller_data)

    all_controllers_data.sort(key=lambda x: x.get("controller_name", ""))

    return json.dumps(all_controllers_data, indent=2)


def main() -> None:
    """Main entry point for the application."""
    args = parse_arguments()

    try:
        input_path, output_path = validate_arguments(args)
    except SystemExit:
        return

    print(f"Starting conversion of '{input_path}' to '{output_path}'")

    try:
        json_output_string = convert_xml_to_json(input_path)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_output_string)

        print(f"Conversion complete. Output saved to '{output_path}'")

    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
