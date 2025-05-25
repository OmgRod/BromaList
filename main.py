import os
from pybroma import Root
from jinja2 import Environment, FileSystemLoader

def format_addr(addr):
    if addr is None:
        return None
    # Convert signed int to unsigned 64-bit int
    unsigned_addr = addr & 0xFFFFFFFF
    # Filter out known invalid addresses (-1, -2, 0)
    if unsigned_addr in (0, 0xFFFFFFFF, 0xFFFFFFFE):
        return None
    return f"0x{unsigned_addr:08X}"

root = Root("bindings/bindings/2.207/GeometryDash.bro")

classes = []
print(f"Total classes found: {len(root.classes)}")

for cls in root.classes:
    members = []
    seen_names = set()  # to avoid duplicates

    for field in cls.fields:
        func = field.getAsFunctionBindField()
        if func:
            # Format addresses safely and filter invalid
            addresses = {
                "mac": format_addr(getattr(func.binds, "imac", None)),
                "win": format_addr(getattr(func.binds, "win", None)),
                "ios": format_addr(getattr(func.binds, "ios", None)),
            }

            # Skip if all addresses are None (no valid binding)
            if all(addr is None for addr in addresses.values()):
                continue

            name = func.prototype.name if hasattr(func.prototype, "name") else "UNKNOWN"
            if name in seen_names:
                continue
            seen_names.add(name)

            members.append({
                "name": name,
                "args": {k: str(v.name) for k, v in func.prototype.args.items()} if hasattr(func.prototype, "args") else {},
                "addresses": addresses,
                "type": "Function",
            })

        else:
            # Try to get the field name properly
            name = getattr(field, "name", None)
            if not name:
                name = getattr(field, "getName", lambda: None)()
            if not name:
                name = getattr(field, "id", "UNKNOWN")

            if name in seen_names:
                continue
            seen_names.add(name)

            members.append({
                "name": name,
                "type": str(field.__class__.__name__),
                "addresses": None,
            })

    classes.append({
        "name": cls.name,
        "inherits": getattr(cls, "superclasses", []),
        "members": members,
    })

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("index.html.jinja")

output = template.render(classes=classes)

os.makedirs("dist", exist_ok=True)
with open("dist/index.html", "w", encoding="utf-8") as f:
    f.write(output)

print("Static site generated at ./dist/index.html")
