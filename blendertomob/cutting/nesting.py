class NestingPart:
    def __init__(self, id, name, width, height, quantity, grain_direction='NONE', module_ref=""):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.quantity = quantity
        self.grain_direction = grain_direction # 'NONE', 'VERTICAL', 'HORIZONTAL'
        self.module_ref = module_ref

class NestingSheet:
    def __init__(self, id, width, height, refilo_top=10, refilo_bottom=10, refilo_left=10, refilo_right=10):
        self.id = id
        self.width = width
        self.height = height
        # Refilo (margins)
        self.refilo_top = refilo_top
        self.refilo_bottom = refilo_bottom
        self.refilo_left = refilo_left
        self.refilo_right = refilo_right
        
        # Calculate usable area
        self.usable_width = width - (refilo_left + refilo_right)
        self.usable_height = height - (refilo_top + refilo_bottom)

def optimize_nesting(parts, sheet_width=2750.0, sheet_height=1830.0, refilo=10.0, kerf=4.0):
    """
    Performs a 2D guillotine/shelf-based bin-packing (nesting) optimization.
    
    Args:
        parts: List of NestingPart objects.
        sheet_width: Nominal sheet width (default 2750mm).
        sheet_height: Nominal sheet height (default 1830mm).
        refilo: Margin subtracted from all 4 borders of a new sheet (default 10mm).
        kerf: Blade cut width (default 4mm).
        
    Returns:
        A dictionary containing:
            - sheets: List of sheets used, each with a list of placed parts with coordinates.
            - unplaced: List of parts that could not be placed due to size.
            - stats: Summary metrics (utilization percentage, count of sheets, etc.)
    """
    # Usable sheet dimensions
    u_w = sheet_width - (refilo * 2)
    u_h = sheet_height - (refilo * 2)
    
    # Flatten parts by quantity
    flat_parts = []
    unplaced = []
    
    for p in parts:
        # Check if part fits on sheet even when rotated
        w_fit = p.width <= u_w and p.height <= u_h
        h_fit = p.height <= u_w and p.width <= u_h
        
        if not (w_fit or h_fit):
            unplaced.append({
                "id": p.id,
                "name": p.name,
                "width": p.width,
                "height": p.height,
                "reason": "Exceeds usable sheet size"
            })
            continue
            
        for i in range(p.quantity):
            flat_parts.append({
                "id": f"{p.id}_{i}",
                "part_id": p.id,
                "name": p.name,
                "width": p.width,
                "height": p.height,
                "grain_direction": p.grain_direction,
                "module_ref": p.module_ref
            })
            
    # Sort flat parts by area descending to optimize packing
    flat_parts.sort(key=lambda x: x["width"] * x["height"], reverse=True)
    
    sheets_used = []
    
    # Simple Shelf / Next-Fit-Decreasing heuristic modified for Guillotine Cuts
    # Each sheet contains shelves (rows).
    # Inside a row, parts are packed side-by-side horizontally.
    for part in flat_parts:
        placed = False
        
        # Try to place in existing sheets
        for sheet in sheets_used:
            # Try to place on an existing shelf in this sheet
            for shelf in sheet["shelves"]:
                # Check if part fits in shelf
                # We need to consider rotation based on grain direction restrictions
                fits, rot = can_fit_in_shelf(part, shelf, u_w, sheet["remaining_height"], kerf)
                if fits:
                    w = part["height"] if rot else part["width"]
                    h = part["width"] if rot else part["height"]
                    
                    x = shelf["current_x"]
                    y = shelf["y"]
                    
                    shelf["parts"].append({
                        "id": part["id"],
                        "part_id": part["part_id"],
                        "name": part["name"],
                        "x": x + refilo, # Offset by left refilo margin
                        "y": y + refilo, # Offset by bottom refilo margin
                        "width": w,
                        "height": h,
                        "rotated": rot,
                        "module_ref": part["module_ref"]
                    })
                    
                    shelf["current_x"] += w + kerf
                    # Update shelf height if this part is taller than the current shelf height
                    if h > shelf["height"]:
                        # Adjust remaining height in the sheet
                        sheet["remaining_height"] -= (h - shelf["height"])
                        shelf["height"] = h
                        
                    placed = True
                    break
            
            if placed:
                break
                
            # If not placed on existing shelves, try to create a new shelf on this sheet
            # Check if there is enough vertical space
            # We check both orientations (rotated and normal)
            fits, rot, req_h = can_create_shelf_in_sheet(part, sheet, u_w, u_h)
            if fits:
                w = part["height"] if rot else part["width"]
                h = part["width"] if rot else part["height"]
                
                new_shelf = {
                    "y": u_h - sheet["remaining_height"],
                    "height": h,
                    "current_x": w + kerf,
                    "parts": [{
                        "id": part["id"],
                        "part_id": part["part_id"],
                        "name": part["name"],
                        "x": refilo,
                        "y": (u_h - sheet["remaining_height"]) + refilo,
                        "width": w,
                        "height": h,
                        "rotated": rot,
                        "module_ref": part["module_ref"]
                    }]
                }
                sheet["shelves"].append(new_shelf)
                sheet["remaining_height"] -= h + kerf
                placed = True
                break
                
        if not placed:
            # Create a new sheet
            new_sheet_id = len(sheets_used) + 1
            
            # Find best orientation for new sheet
            # Default orientation
            fits, rot, req_h = can_create_shelf_in_dimensions(part, u_w, u_h)
            if fits:
                w = part["height"] if rot else part["width"]
                h = part["width"] if rot else part["height"]
                
                new_sheet = {
                    "id": new_sheet_id,
                    "width": sheet_width,
                    "height": sheet_height,
                    "remaining_height": u_h - (h + kerf),
                    "shelves": [{
                        "y": 0.0,
                        "height": h,
                        "current_x": w + kerf,
                        "parts": [{
                            "id": part["id"],
                            "part_id": part["part_id"],
                            "name": part["name"],
                            "x": refilo,
                            "y": refilo,
                            "width": w,
                            "height": h,
                            "rotated": rot,
                            "module_ref": part["module_ref"]
                        }]
                    }]
                }
                sheets_used.append(new_sheet)
            else:
                # Should not happen since we checked maximum size beforehand,
                # but if it does, put in unplaced.
                unplaced.append({
                    "id": part["id"],
                    "name": part["name"],
                    "width": part["width"],
                    "height": part["height"],
                    "reason": "Could not initialize new sheet"
                })
                
    # Calculate stats
    total_sheet_area = len(sheets_used) * sheet_width * sheet_height
    total_placed_area = 0.0
    
    for s in sheets_used:
        for shelf in s["shelves"]:
            for p in shelf["parts"]:
                total_placed_area += p["width"] * p["height"]
                
    utilization = (total_placed_area / total_sheet_area * 100.0) if total_sheet_area > 0 else 0.0
    
    return {
        "sheets": sheets_used,
        "unplaced": unplaced,
        "stats": {
            "sheets_count": len(sheets_used),
            "total_placed_parts": sum(len(sh["parts"]) for s in sheets_used for sh in s["shelves"]),
            "unplaced_count": len(unplaced),
            "utilization_percentage": round(utilization, 2),
            "total_placed_area_m2": round(total_placed_area / 1000000.0, 3)
        }
    }

def can_fit_in_shelf(part, shelf, usable_width, remaining_height, kerf):
    """Checks if a part can fit in an existing shelf (considering rotation rules and sheet height)."""
    p_w = part["width"]
    p_h = part["height"]
    g_d = part["grain_direction"]
    
    # Check regular orientation
    if g_d != 'HORIZONTAL': # Vertical or None can go normal
        if shelf["current_x"] + p_w <= usable_width:
            # Check if shelf growth exceeds sheet remaining height
            h_diff = max(0.0, p_h - shelf["height"])
            if h_diff <= remaining_height:
                return True, False
            
    # Check rotated orientation
    if g_d != 'VERTICAL': # Horizontal or None can be rotated
        if shelf["current_x"] + p_h <= usable_width:
            # Check if shelf growth exceeds sheet remaining height
            h_diff = max(0.0, p_w - shelf["height"])
            if h_diff <= remaining_height:
                return True, True
            
    return False, False

def can_create_shelf_in_sheet(part, sheet, usable_width, usable_height):
    """Checks if a part can fit by creating a new shelf in a sheet."""
    p_w = part["width"]
    p_h = part["height"]
    g_d = part["grain_direction"]
    rem_h = sheet["remaining_height"]
    
    # Normal orientation
    if g_d != 'HORIZONTAL':
        if p_w <= usable_width and p_h <= rem_h:
            return True, False, p_h
            
    # Rotated orientation
    if g_d != 'VERTICAL':
        if p_h <= usable_width and p_w <= rem_h:
            return True, True, p_w
            
    return False, False, 0.0

def can_create_shelf_in_dimensions(part, usable_width, usable_height):
    """Checks if a part fits in raw usable sheet dimensions."""
    p_w = part["width"]
    p_h = part["height"]
    g_d = part["grain_direction"]
    
    # Normal orientation
    if g_d != 'HORIZONTAL':
        if p_w <= usable_width and p_h <= usable_height:
            return True, False, p_h
            
    # Rotated orientation
    if g_d != 'VERTICAL':
        if p_h <= usable_width and p_w <= usable_height:
            return True, True, p_w
            
    return False, False, 0.0
