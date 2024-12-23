import os
import argparse
import xml.etree.ElementTree as ET

# Default tag configurations with support for optional attributes and defaults
TAG_CONFIG = {
    "Canvas": {
        "attributes": ["name", "target"],
        "defaults": {}
    },
    "Align": {
        "attributes": ["type", "width", "height"],
        "defaults": {"type" : "centre"}
    },
    "Layout": {
        "attributes": ["region", "alignment", "debug"],
        "defaults": {
            "region": "__centre_region",
            "alignment": "DEFAULT",
            "debug": "false"
        }
    },
    "LayoutItem": {
        "attributes": ["style", "height", "width", "dock"],
        "defaults": { "dock" : "false"}
    },
    "Dock": {
        "attributes": ["side", "width", "height", "margin"],
        "defaults": {"margin": "0"}
    },
}

# Helper to retrieve attribute value with default fallback
def get_attribute(tag, attrib_name, attrib_dict):
    config = TAG_CONFIG.get(tag, {})
    defaults = config.get("defaults", {})
    return attrib_dict.get(attrib_name, defaults.get(attrib_name, None))

def generate_align_call(type_, indent, canvas, width, height):
    align_mapping = {
        "centre": "arm_2d_align_centre",
        "center": "arm_2d_align_centre",
        "top-left": "arm_2d_align_top_left",
        "top-right": "arm_2d_align_top_right",
        "bottom-left": "arm_2d_align_bottom_left",
        "bottom-right": "arm_2d_align_bottom_right",
        "middle-left": "arm_2d_align_mid_left",
        "middle-right": "arm_2d_align_mid_right",
        "top-center": "arm_2d_align_top_centre",
        "bottom-center": "arm_2d_align_bottom_centre",
    }

    if type_ not in align_mapping:
        raise ValueError(f"Unsupported alignment type: {type_}")

    return f"{indent}{align_mapping[type_]}({canvas}, {width}, {height}) {{"

def generate_dock_call(side, indent, canvas, width, height, margin):
    dock_mapping = {
        "top": "arm_2d_dock_top",
        "bottom": "arm_2d_dock_bottom",
        "left": "arm_2d_dock_left",
        "right": "arm_2d_dock_right",
        "general": "arm_2d_dock",
    }

    if side == "general":
        return f"{indent}{dock_mapping[side]}({canvas}, {width}, {height}, {margin}) {{"

    if side not in dock_mapping:
        raise ValueError(f"Unsupported dock side: {side}")

    if width and height:
        return f"{indent}{dock_mapping[side]}({canvas}, {width}, {height}, {margin}) {{"
    elif width:
        return f"{indent}{dock_mapping[side]}({canvas}, {width}, {margin}) {{"
    elif height:
        return f"{indent}{dock_mapping[side]}({canvas}, {height}, {margin}) {{"
    else:
        return f"{indent}{dock_mapping[side]}({canvas}, {margin}) {{"

def generate_vertical_dock_call(indent, canvas, width, margin):
    return f"{indent}arm_2d_dock_vertical({canvas}, {width}, {margin}) {{"

def generate_horizontal_dock_call(indent, canvas, height, margin):
    return f"{indent}arm_2d_dock_horizontal({canvas}, {height}, {margin}) {{"

def generate_layout_call(tag, attributes, indent):
    if tag == "Layout":
        region = get_attribute(tag, "region", attributes)
        alignment = get_attribute(tag, "alignment", attributes)
        debug = get_attribute(tag, "debug", attributes)

        # Assemble arguments based on provided attributes
        args = [region]
        if alignment and alignment != "DEFAULT":
            args.append(alignment.upper())

        if debug.lower() == "true":
            args.append(alignment.upper())
            args.append("true")

        # Convert argument list to a comma-separated string
        arg_string = ", ".join(args)
        return f"{indent}arm_2d_layout({arg_string}) {{"
    return None

def process_item_line_dock(tag, attributes, indent):
    if tag == "DockItem":
        side = get_attribute(tag, "side", attributes)
        width = get_attribute(tag, "width", attributes)
        height = get_attribute(tag, "height", attributes)
        margin = get_attribute(tag, "margin", attributes)

        if side == "horizontal":
            return f"{indent}__item_line_dock_horizontal({width}, {margin}) {{"
        elif side == "vertical":
            return f"{indent}__item_line_dock_vertical({height}, {margin}) {{"
    return None

def xml_to_c(xml_path, c_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    c_code = []
    canvas_name = "__canvas"  # Default canvas name

    def process_tag(tag, attributes, indent_level):
        nonlocal canvas_name
        indent = "    " * indent_level
        if tag == "Canvas":
            name = get_attribute(tag, "name", attributes)
            target = get_attribute(tag, "target", attributes)
            canvas_name = name
            c_code.append(f"{indent}arm_2d_canvas({target}, {name}) {{")
        elif tag == "Align":
            type_ = get_attribute(tag, "type", attributes)
            width = get_attribute(tag, "width", attributes)
            height = get_attribute(tag, "height", attributes)
            c_code.append(generate_align_call(type_, indent, canvas_name, width, height))
        elif tag == "Layout":
            layout_call = generate_layout_call(tag, attributes, indent)
            c_code.append(layout_call)
        elif tag == "LayoutItem":
            style = get_attribute(tag, "style", attributes)
            height = get_attribute(tag, "height", attributes)
            width = get_attribute(tag, "width", attributes)
            dock = get_attribute(tag, "dock", attributes)
            if dock.lower() == "true":
                if style == "line horizontal":
                    c_code.append(f"{indent}__item_line_dock_horizontal({width}) {{")
                if style == "line vertical":
                    c_code.append(f"{indent}__item_line_dock_vertical({height}) {{")
            else:
                if style == "line horizontal":
                    c_code.append(f"{indent}__item_line_horizontal({height}, {width}) {{")
                if style == "line vertical":
                    c_code.append(f"{indent}__item_line_vertical({height}, {width}) {{")
                if style == "horizontal":
                    c_code.append(f"{indent}__item_horizontal({height}, {width}) {{")
                if style == "vertical":
                    c_code.append(f"{indent}__item_vertical({height}, {width}) {{")
        elif tag == "Dock":
            side = get_attribute(tag, "side", attributes)
            width = get_attribute(tag, "width", attributes)
            height = get_attribute(tag, "height", attributes)
            margin = get_attribute(tag, "margin", attributes)
            if side == "top":
                c_code.append(f"{indent}arm_2d_dock_top({canvas_name}, {width}, {margin}) {{")
            elif side == "bottom":
                c_code.append(f"{indent}arm_2d_dock_bottom({canvas_name}, {width}, {margin}) {{")
            elif side == "left":
                c_code.append(f"{indent}arm_2d_dock_left({canvas_name}, {height}, {margin}) {{")
            elif side == "right":
                c_code.append(f"{indent}arm_2d_dock_right({canvas_name}, {height}, {margin}) {{")
            elif side == "general":
                c_code.append(f"{indent}arm_2d_dock({canvas_name}, {width}, {height}, {margin}) {{")
            elif side == "vertical":
                width = get_attribute(tag, "width", attributes)
                margin = get_attribute(tag, "margin", attributes)
                c_code.append(f"{indent}arm_2d_dock_vertical({canvas_name}, {width}, {margin}) {{")
            elif side == "horizontal":
                height = get_attribute(tag, "height", attributes)
                margin = get_attribute(tag, "margin", attributes)
                c_code.append(f"{indent}arm_2d_dock_horizontal({canvas_name}, {height}, {margin}) {{")

    def traverse(node, indent_level=0):
        process_tag(node.tag, node.attrib, indent_level)
        has_children = len(list(node)) > 0
        if has_children:
            for child in node:
                traverse(child, indent_level + 1)
        if node.tag in TAG_CONFIG:
            indent = "    " * (indent_level)
            c_code.append(f"{indent}}}")


    traverse(root)

    with open(c_path, "w") as f:
        f.write("\n".join(c_code))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert XML to Arm-2D C code (v0.1.0)")
    parser.add_argument("-i", "--input", required=False, help="Path to the input XML file.")
    parser.add_argument("-o", "--output", required=False, help="Path to the output C file.")

    args = parser.parse_args()
    if args.input == None: 
        parser.print_help();
        exit(1);

    input_path = args.input
    if not os.path.isfile(input_path):
        parser.error(f"Input XML file not found: {input_path}")

    output_path = args.output or os.path.splitext(input_path)[0] + ".c"

    xml_to_c(input_path, output_path)

    print(f"C code generated at {output_path}")
