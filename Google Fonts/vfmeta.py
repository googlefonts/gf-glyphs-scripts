#MenuTitle: Set VF metadata
"""Set a font's VF metadata.

Limitations:
Script can only set width and weight


Implementation:
- Determines which axises exist in the font
- Set each master's axis locations based on values from matching instances
"""

font = Glyphs.font

masters = font.masters
instances = font.instances

# Set font.customParameters['Axes']
m_weights = set()
m_widths = set()

i_weights = set()
i_widths = set()

for master in masters:
    m_weights.add(master.weightValue)
    m_widths.add(master.widthValue)

for instance in instances:
    i_weights.add(instance.weightValue)
    i_widths.add(instance.widthValue)

needs_weight_axis = True if len(m_weights) >= 2 and len(i_weights) >= 3 else False
needs_width_axis = True if len(m_widths) >= 2 and len(i_widths) >= 3 else False

if needs_weight_axis or needs_width_axis:
    font.customParameters['Axes'] = []
    if needs_weight_axis:
        font.customParameters['Axes'].append({'Name': 'Weight', 'Tag': 'wght'})
    if needs_width_axis:
        font.customParameters['Axes'].append({'Name': 'Width', 'Tag': 'wdth'})
else:
    raise Exception('Font is not VF compatible! Font must have at least 2 masters '
                    'and 3 instances in a weight or width design space.')


# Gather axis location info for each master using values from instances
master_axis_info = {}
master_names = {}
for master in masters:
    if needs_weight_axis and needs_width_axis:
        k = (master.weightValue, master.widthValue)
    elif needs_weight_axis and not needs_width_axis:
        k = (master.weightValue)
    elif needs_width_axis and not needs_weight_axis:
        k = (master.widthValue)
    master_axis_info[k] = None
    master_names[k] = master.name

for instance in instances:
    if needs_weight_axis and needs_width_axis:
        k = (instance.weightValue, instance.widthValue)
    elif needs_weight_axis and not needs_width_axis:
        k = (instance.weightValue)
    elif needs_width_axis and not needs_weight_axis:
        k = (instance.widthValue)

    if k in master_axis_info:
        if needs_weight_axis and needs_width_axis:
            v = [
                {'Axis': 'Weight', 'Location': instance.weightClassValue()},
                {'Axis': 'Width', 'Location': instance.widthClassValue()}
            ]
        elif needs_weight_axis and not needs_width_axis:
            v = [
                {'Axis': 'Weight', 'Location': instance.weightClassValue()},
            ]
        elif needs_width_axis and not needs_weight_axis:
            v = [
                {'Axis': 'Width', 'Location': instance.widthClassValue()}
            ]
        master_axis_info[k] = v


if None in master_axis_info.values():
    unmatching_masters = [v for k, v in master_names.items() if not master_axis_info[k]]
    raise Exception(
        ("Cannot produce VF metadata. Each master must have an instance which "
         "references its weightClass or widthClass values. No matching value were "
         "found for masters [{}]".format(unmatching_masters))
        )

# Set each master's Axis Locations parameter
for master in masters:
    if needs_weight_axis and needs_width_axis:
        k = (master.weightValue, master.widthValue)
    elif needs_weight_axis and not needs_width_axis:
        k = (master.weightValue)
    elif needs_width_axis and not needs_weight_axis:
        k = (master.widthValue)
    master.customParameters['Axis Location'] = master_axis_info[k]
Glyphs.showMacroWindow()
print "Done setting font's VF metadata"
