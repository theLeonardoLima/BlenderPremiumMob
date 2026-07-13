"""Apply molding packages to a room.

apply_scene_packages(scene) is the single entry point: it clears every
package sweep in the scene and rebuilds from the scene's three package
props. The scene-prop update callbacks and the refresh operator both
route through it, so the dropdowns are the whole UI.
"""

import bpy
import mathutils

from . import adapters, engine, packages

MOLDING_TAG = 'IS_HB_MOLDING_SWEEP'
MOLDING_TYPE = 'HB_MOLDING_TYPE'
MOLDING_MEMBERS = 'HB_MOLDING_MEMBERS'

# (prop name, molding type, grouping alignment)
_TYPES = (
    ('molding_crown_package', 'CROWN', 'top'),
    ('molding_base_package', 'BASE', 'bottom'),
    ('molding_light_rail_package', 'LIGHT_RAIL', 'bottom'),
)


def clear_scene_molding(scene, molding_type=None):
    """Remove package sweeps (and their hidden profiles) from the
    scene, optionally scoped to one molding type."""
    doomed = []
    for obj in list(scene.objects):
        if not obj.get(MOLDING_TAG):
            continue
        if molding_type and obj.get(MOLDING_TYPE) != molding_type:
            continue
        bevel = obj.data.bevel_object if obj.type == 'CURVE' else None
        doomed.append(obj)
        if bevel is not None and bevel.get('IS_HB_MOLDING_PROFILE'):
            doomed.append(bevel)
    for obj in doomed:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data is not None and data.users == 0:
            bpy.data.curves.remove(data)


def _sweep_z(molding_type, first, dy, facts, opts):
    """Sweep Z in the first member's local frame.

    Crown mounts a REVEAL above the door top when the cabinet exposes
    one (face frame: height - top rail + door overlay + reveal, the
    same datum the crown detail drawing uses); cabinets without a
    face-frame mount (frameless) keep the top line. The furniture CAP
    always caps the top line. Base sits on the floor; light rail hangs
    at the bottom line (upper roots originate at their bottom)."""
    if molding_type == 'CROWN':
        _, _, height = engine.cage_dims(first)
        mount = (facts.get(id(first)) or {}).get('crown_mount')
        if mount:
            return (height - mount['rail_width'] + mount['door_overlay']
                    + opts['crown_reveal'] + dy)
        return height + dy
    if molding_type == 'CAP':
        _, _, height = engine.cage_dims(first)
        return height + dy
    return dy


def _spawn_sweep(scene, molding_type, chain, segments, profile_ref,
                 fallback_key, dy, facts, opts):
    """Create one sweep object: hidden profile + curve through the
    world-space segments, localized to (and parented on) chain[0]."""
    first = chain[0]
    profile = packages.make_profile_object(
        profile_ref, fallback_key,
        f"Molding_Profile_{fallback_key}", scene.collection)
    if profile is None:
        return None
    curve = bpy.data.curves.new("MoldingSweep", type='CURVE')
    curve.dimensions = '2D'
    curve.bevel_mode = 'OBJECT'
    curve.bevel_object = profile
    curve.use_fill_caps = True
    sweep = bpy.data.objects.new("MoldingSweep", curve)
    scene.collection.objects.link(sweep)
    sweep[MOLDING_TAG] = True
    sweep[MOLDING_TYPE] = molding_type
    sweep[MOLDING_MEMBERS] = ",".join(c.name for c in chain)
    sweep.parent = first
    sweep.location.z = _sweep_z(molding_type, first, dy, facts, opts)
    profile.parent = sweep

    first_inv = first.matrix_world.inverted()
    wrote = 0
    for pts, cyclic in segments:
        local = []
        for p in pts:
            lp = first_inv @ mathutils.Vector((p.x, p.y, 0.0))
            if not local or (abs(lp.x - local[-1][0]) > 1e-4
                             or abs(lp.y - local[-1][1]) > 1e-4):
                local.append((lp.x, lp.y, 0.0))
        if (cyclic and len(local) > 2
                and abs(local[0][0] - local[-1][0]) < 1e-4
                and abs(local[0][1] - local[-1][1]) < 1e-4):
            local.pop()
        if len(local) < (3 if cyclic else 2):
            continue
        spline = curve.splines.new('BEZIER')
        spline.use_smooth = False
        spline.bezier_points.add(count=len(local) - 1)
        for bp, co in zip(spline.bezier_points, local):
            bp.co = co
            bp.handle_left_type = 'VECTOR'
            bp.handle_right_type = 'VECTOR'
        spline.use_cyclic_u = cyclic
        wrote += 1
    if wrote == 0:
        bpy.data.objects.remove(sweep, do_unlink=True)
        bpy.data.objects.remove(profile, do_unlink=True)
        return None
    return sweep


def _apply_type(scene, molding_type, align, stack, opts):
    targets = adapters.collect_targets(scene, molding_type)
    if not targets:
        return 0
    members = list(targets)
    if molding_type == 'BASE':
        members += [b for b in adapters.collect_bridges(scene)
                    if b not in members]
    facts = adapters.build_facts(scene, members)

    made = 0
    for component in engine.connected_components(members, align=align):
        if not any(m in targets for m in component):
            continue
        chain = engine.order_chain(component, align=align)
        for profile_ref, fallback_key, dx, dy in stack:
            # Room-adjustable stack entries (a crown riding a spacer)
            # resolve their vertical offset from the scene prop.
            if dy == 'STACK_OFFSET':
                dy = opts['stack_offset']
            # Room profile overrides swap the preset's profile for
            # another one from the same pack category.
            category = profile_ref.replace("\\", "/").split("/")[0]
            override = opts['overrides'].get(category)
            if override:
                profile_ref = f"{category}/{override}"
            if molding_type == 'BASE':
                segments = engine.kick_sweep_segments(
                    chain, facts, dx, opts['include_recessed'])
                sweep_chain = chain
            else:
                result = engine.chain_sweep_points(chain, facts, dx, dx)
                if result is None:
                    continue
                pts, sweep_chain = result
                segments = [(pts, False)]
            if not segments:
                continue
            if _spawn_sweep(scene, molding_type, sweep_chain, segments,
                            profile_ref, fallback_key, dy, facts,
                            opts) is not None:
                made += 1
    return made


def apply_scene_packages(scene):
    """Rebuild every molding-package sweep in the scene from its three
    package props. Safe to call from prop update callbacks."""
    hb = getattr(scene, 'home_builder', None)
    if hb is None:
        return 0
    if scene.get('IS_LAYOUT_VIEW') or scene.get('IS_DETAIL_VIEW'):
        return 0
    clear_scene_molding(scene)

    def _override(prop_name):
        value = getattr(hb, prop_name, 'DEFAULT')
        return None if value in ('DEFAULT', '') else value

    opts = {
        'include_recessed': getattr(hb, 'molding_base_include_recessed',
                                    False),
        'crown_reveal': getattr(hb, 'molding_crown_reveal', 0.0),
        'stack_offset': getattr(hb, 'molding_crown_stack_offset', 0.0),
        'overrides': {
            'Crown Molding': _override('molding_crown_profile'),
            'Spacer': _override('molding_spacer_profile'),
            'Furniture Caps': _override('molding_cap_profile'),
        },
    }

    made = 0
    for prop_name, molding_type, align in _TYPES:
        ident = getattr(hb, prop_name, 'NONE')
        if ident == 'NONE':
            continue
        stack = packages.package_stack(molding_type, ident)
        if not stack:
            continue
        made += _apply_type(scene, molding_type, align, stack, opts)

    # The furniture cap is an independent toggle: it caps the top line
    # over whichever crown package (or none) sits at the reveal.
    if getattr(hb, 'molding_crown_furniture_cap', False):
        made += _apply_type(scene, 'CAP', 'top',
                            packages.FURNITURE_CAP_STACK, opts)
    return made


def on_package_changed(self, context):
    """Scene-prop update callback: re-apply immediately so the dropdown
    IS the interaction. Errors are contained so a bad room can't wedge
    the property system."""
    try:
        apply_scene_packages(self.id_data)
    except Exception as ex:  # pragma: no cover - defensive
        print(f"Home Builder molding: apply failed: {ex}")


class home_builder_OT_refresh_room_molding(bpy.types.Operator):
    """Rebuild this room's molding packages after cabinets change"""
    bl_idname = "home_builder.refresh_room_molding"
    bl_label = "Refresh Room Molding"
    bl_options = {'UNDO'}

    def execute(self, context):
        made = apply_scene_packages(context.scene)
        self.report({'INFO'}, f"Rebuilt {made} molding run(s)")
        return {'FINISHED'}


classes = (
    home_builder_OT_refresh_room_molding,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
