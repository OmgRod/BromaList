import json
import os
from jinja2 import Environment, FileSystemLoader
from src import codegen

def format_addr(addr):
    if addr is None:
        return None
    if isinstance(addr, int):
        return f"0x{addr:X}"
    if isinstance(addr, str):
        try:
            if addr.startswith("0x") or addr.startswith("0X"):
                return addr.lower()
            else:
                intval = int(addr)
                return f"0x{intval:X}"
        except Exception:
            return None
    return None

def normalize_inherits(inherits):
    if not inherits:
        return []
    if isinstance(inherits, str):
        return [inherits]
    if isinstance(inherits, list):
        result = []
        for item in inherits:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict) and "name" in item:
                result.append(item["name"])
        return result
    return []

def main():
    with open("bindings/bindings/2.2074/Geode/CodegenData.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    classes = []

    for cls in data.get("classes", []):
        members = []
        seen_names = set()

        for func in cls.get("functions", []):
            bindings = func.get("bindings", {})
            addresses = {
                "win": format_addr(bindings.get("win")),
                "mac": format_addr(bindings.get("imac")),
                "m1": format_addr(bindings.get("m1")),
                "ios": format_addr(bindings.get("ios")),
                "android32": format_addr(bindings.get("android32")),
                "android64": format_addr(bindings.get("android64")),
            }

            if all(addr is None for addr in addresses.values()):
                continue

            name = func.get("name", "UNKNOWN")
            if name in seen_names:
                continue
            seen_names.add(name)

            args = []
            for arg in func.get("args", []):
                if isinstance(arg, dict):
                    arg_name = arg.get("name", None)
                    args.append(arg_name if arg_name else "arg")
                else:
                    args.append(str(arg))

            inline_info = {}
            for platform, bind_val in bindings.items():
                if isinstance(bind_val, str) and bind_val.lower() == "inline":
                    inline_info[platform] = True
                else:
                    inline_info[platform] = False

            members.append({
                "name": name,
                "args": args,
                "addresses": addresses,
                "inline": inline_info,
                "type": "Function",
            })

        for field in cls.get("fields", []):
            name = field.get("name")
            if not name or name in seen_names:
                continue
            seen_names.add(name)

            bindings = field.get("bindings", {})
            addresses = {
                "win": format_addr(bindings.get("win")),
                "mac": format_addr(bindings.get("imac")),
                "m1": format_addr(bindings.get("m1")),
                "ios": format_addr(bindings.get("ios")),
                "android32": format_addr(bindings.get("android32")),
                "android64": format_addr(bindings.get("android64")),
            }
            if all(addr is None for addr in addresses.values()):
                addresses = None

            members.append({
                "name": name,
                "type": "Field",
                "args": [],
                "addresses": addresses,
                "inline": None,
            })

        classes.append({
            "name": cls.get("name"),
            "inherits": normalize_inherits(cls.get("inherits", [])),
            "members": members,
        })

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("index.html.jinja")

    output = template.render(classes=classes)

    os.makedirs("dist", exist_ok=True)
    with open("dist/index.html", "w", encoding="utf-8") as f:
        f.write(output)

    print("Static site generated at ./dist/index.html")

if __name__ == "__main__":
    codegen.codegen()
    main()
