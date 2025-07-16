from pyvis.network import Network

__all__ = ['diff_sys_graph',
           'dydx_graph',
           'dydt3_graph']
def diff_sys_graph():
    dsg_nodes = ['dt','x','t1','t2','t3','y','r']
    dsg_edges = [
        ['x','t2'],['t2','t3'],['t3','y'],['x','y'],['r','x'],
        ['t1','x'],['dt','x']
    ]
    dsg = Network(notebook=True, directed=True)
    dsg.inherit_edge_colors(False)
    dsg.add_nodes(dsg_nodes,shape=['box' for i in range(len(dsg_nodes))])
    for e in dsg_edges: dsg.add_edge(*e,color='black')
            
    dsg.toggle_physics(True)
    return dsg

def dydx_graph():
    dsg_nodes = ['x','t2','t3','y','calc_t2','calc_t3','calc_y']
    dsg_edges = [
        ['x','calc_t2',],['calc_t2','t2'],['t2','calc_t3'],
        ['calc_t3','t3'],['t3','calc_y'],['calc_y','y','black'],
        ['x','calc_y','blue'],
    ]
    dsg = Network(notebook=True, directed=True)
    dsg.inherit_edge_colors(False)
    dsg.add_nodes(dsg_nodes,shape=['box' for i in range(len(dsg_nodes))])
    for e in dsg_edges:
        if len(e)==3:
            dsg.add_edge(*e[:2],color=e[-1])
        else:
            dsg.add_edge(*e,color='red')
            
    dsg.toggle_physics(True)
    return dsg

def dydx_graph():
    dsg_nodes = ['x','t2','t3','y','calc_t2','calc_t3','calc_y']
    dsg_edges = [
        ['x','calc_t2',],['calc_t2','t2'],['t2','calc_t3'],
        ['calc_t3','t3'],['t3','calc_y'],['calc_y','y','black'],
        ['x','calc_y','blue'],
    ]
    dsg = Network(notebook=True, directed=True)
    dsg.inherit_edge_colors(False)
    dsg.add_nodes(dsg_nodes,shape=['box' for i in range(len(dsg_nodes))])
    for e in dsg_edges:
        if len(e)==3:
            dsg.add_edge(*e[:2],color=e[-1])
        else:
            dsg.add_edge(*e,color='red')
            
    dsg.toggle_physics(True)
    return dsg

def dydt3_graph():
    dsg_nodes = ['x','t2','t3','y','calc_t2','calc_t3','calc_y']
    dsg_edges = [
        ['x','calc_t2',],['calc_t2','t2'],['t2','calc_t3'],
        ['calc_t3','t3'],['t3','calc_y','green'],['calc_y','y','black'],
        ['x','calc_y','blue'],
    ]
    dsg = Network(notebook=True, directed=True)
    dsg.inherit_edge_colors(False)
    dsg.add_nodes(dsg_nodes,shape=['box' for i in range(len(dsg_nodes))])
    for e in dsg_edges:
        if len(e)==3:
            dsg.add_edge(*e[:2],color=e[-1])
        else:
            dsg.add_edge(e[1],e[0],color='red',dashes=True)
            
    dsg.toggle_physics(True)
    return dsg