def check_unconnected_member_nodes(unconnected_member_node_buffer, boundary_nodes):
    """
    Given a buffer of unconnected member node lists and a list of boundary nodes, attempts to connect the member nodes
    to the boundary nodes.

    Parameters:
    - unconnected_member_node_buffer (list): A list of unconnected member node lists.
    - boundary_nodes (list): A list of boundary nodes.

    Returns:
    - boundary_nodes (list): A list of boundary nodes.

    This function iterates through the unconnected_member_node_buffer and attempts to connect each member node list to
    the boundary_nodes list. If the first node in the member node list matches the last node in the boundary_nodes list,
    the member node list is appended to the boundary_nodes list. If the first node in the member node list matches the
    first node in the boundary_nodes list, the member node list is reversed and appended to the boundary_nodes list.
    If the last node in the member node list matches the first node in the boundary_nodes list, the member node list is
    added to the beginning of the boundary_nodes list. If the last node in the member node list matches the last node in
    the boundary_nodes list, the member node list is reversed and appended to the boundary_nodes list.

    If a connection is made, the member node list is removed from the buffer.

    """
    del_idx = None
    for position_in_buffer, member_node_list in enumerate(unconnected_member_node_buffer):
        if member_node_list[0] == boundary_nodes[-1]:
            boundary_nodes.extend(member_node_list)
            break
        elif member_node_list[0] == boundary_nodes[0]:
            boundary_nodes = list(reversed(member_node_list)) + boundary_nodes
            break
        elif member_node_list[-1] == boundary_nodes[0]:
            boundary_nodes = member_node_list + boundary_nodes
            break
        elif member_node_list[-1] == boundary_nodes[-1]:
            boundary_nodes.extend(list(reversed(member_node_list)))
            break

    del_idx = position_in_buffer
    if del_idx != None:
        del unconnected_member_node_buffer[del_idx]
    return boundary_nodes

def get_boundary_nodes_from_members(nodes_per_member_dict, admin_area_members):
    """
    Given a dictionary of nodes per member and a list of admin area members, returns a list of boundary nodes.

    Parameters:
    - nodes_per_member_dict (dict): A dictionary containing nodes per member.
    - admin_area_members (list): A list of admin area members.

    Returns:
    - boundary_nodes (list): A list of boundary nodes.

    This function iterates through the list of admin area members and checks if the first node of the member node list is
    the same as the last node from the current boundary node list. If it is, the member node list is appended to the
    boundary_nodes list. If not, the last node of the member node list is checked. If it matches the first node in the
    boundary_nodes list, the member node list is added to the beginning of the boundary_nodes list. If neither condition
    is met, the member node list is added to a buffer for later processing.

    If the buffer is not empty, the function repeatedly attempts to append the nodes in the buffer to the boundary_nodes
    list until either the buffer is empty or the timeout counter reaches zero.

    """
    boundary_nodes = []
    unconnected_member_nodes_buffer = []
    for member in admin_area_members:
        member_nodes_list = nodes_per_member_dict[member]
        # the nodes from the first member can be added to the boundary without checks
        if not boundary_nodes:
            boundary_nodes.extend(member_nodes_list)
            continue
        boundary_nodes = check_unconnected_member_nodes(unconnected_member_nodes_buffer, boundary_nodes)
        # check if first node of the member node list is the same as the last node from the current boundary node list
        if member_nodes_list[0] == boundary_nodes[-1]:
            boundary_nodes.extend(member_nodes_list)
        # check if last node of the member node list is the same as the last node from the current boundary node list
        elif member_nodes_list[-1] == boundary_nodes[0]:
            boundary_nodes = member_nodes_list + boundary_nodes
        # sometimes the order of the members in the relation is not correct
        # so the nodes of member need to be to a buffer
        else:
            unconnected_member_nodes_buffer.append(member_nodes_list)
    timeout_counter = len(unconnected_member_nodes_buffer)
    while timeout_counter != 0 and unconnected_member_nodes_buffer:
        check_unconnected_member_nodes(unconnected_member_nodes_buffer, boundary_nodes)
        timeout_counter -= 1
    return boundary_nodes