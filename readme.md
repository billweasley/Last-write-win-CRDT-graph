# Conflict-Free Replicated Data Types (CRDT) - A state-based implementation for Last Write Win (LWW) Graph and Set

Conflict-Free Replicated Data Types (CRDTs) are data structures that power real-time collaborative applications in
distributed systems. CRDTs can be replicated across systems, they can be updated independently and concurrently
without coordination between the replicas, and it is always mathematically possible to resolve inconsistencies that
might result.

## Relevant Readings
- [Wikipedia](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
- [CRDT notes on Github](https://github.com/pfrazee/crdt_notes)
- [The classic INRIA paper who proposed the concept](https://hal.inria.fr/inria-00555588/PDF/techreport.pdf)
- [A good implementation of CRDT LWW set](https://github.com/jamztang/CRDT)
- [Another good implementation of operation based CRDT LWW graph](https://github.com/agravier/crdt-study)

## Main concepts
### CRDT Property / Requirements for operations:
- Associativity (a op b) op c = a op (b op c)
- Commutativity a op b = b op a
- Idempotence a op a = a

### CRDT Types
- Operation based
- State based

This repository tries to implement a state-based one.

### Design Consideration:
- Graph is not that well-formed in the concepts of CRDT - 
  There is no standard proposed algorithm in the paper for a state-based Last-write-win
  graph algorithm. The most useful information is the state-based LWW set and operation based 2P2P graph.  
  
- Mathematically, G = (V, E) where V is the vertex set and E is the edge set. An edge e = V x V, which means
its source and destination vertex for the edge. From the graph definition, 
  we know that edges relays on the definition of vertex and hence any updates on vertex will lead cascading updates on 
  edge.
  
- When a vertex is deleted, naturally all edges involves the vertex should also be removed. 
  The "removal" here is not clearly defined. It could have the following situations:
  - These edges are removed and later on if one wants any of them, it needs to be added individually.
  - Reject the "removal" if any edges associated in the global view of the graph 
    i.e. requiring the vertex has a pre-condition of total degree of 0 to be removed. 
    This is impossible to do without global sync.
  - These edges are marked as invalid, and they will appear again once the corresponding vertex is re-added.
    This is not that intuitive. 
    
- The first option will be intuitive and achievable mentioned in last point, so this library go for that option.
However, things will go to complicated when it associated with cascading updates from vertex to edge. Let's consider
  a situation here. But before that, we need define some notations.
  In Lww set,
  we need an addition set, and a removal set for keep track records of last timestamp of addition and removal for 
  each element. In graph, we have vertex and edge, so we can have addition set V+ and removal set V_ for vertex.
   We also E+ for edge addition, and E_ for edge removal. We use t to represents time here (e.g. t_0, t_1 etc...)
  - Consider the following situation,  
    - t0: 
         - add_vertex(a)   V+: {a: 0}, V- : {}, E+: {}, E-: {}
         - add_vertex(b)   V+：{a: 0, b: 0}, V- : {}, E+: {}, E-: {}
    - t1: add_edge((a, b)) V+：{a: 0, b: 0}, V- : {}, E+: {(a, b): 1}, E-: {}
    - t2: remove_vertex(a) and hence we need to do remove_edge((a, b)) in a cascading way V+：{a: 0, b: 0}, V- : {a: 2}, E+: {(a, b): 1}, E-: {(a, b), 2}
    - t3: add_vertex(a) the vertex a add back again so V+：{a: 3, b: 0}, V- : {a: 2}, E+: {(a, b): 1}, E-: {(a, b), 2}
    - t4: add_edge((a, b)) the edge a add back again so V+：{a: 3, b: 0}, V- : {a: 2}, E+: {(a, b): 4}, E-: {(a, b), 2}
  - However, it might happen where it gets a call on add_edge((a, b), timestamp = 4) first and then is called with add_vertex(a, timestamp = 3) afterwards 
    because a remote copy might add this vertex back before the edge addition, which the local copy does not know about it before a merge happens. 
    In this case, you will find the condition of edge addition for (a, b) will be not be satisfied because the vertex a is just not in the local copy when 
    the operation is made.
  - To solve this, we need tombstone mechanism. We can add the edge (i.e. update marks in E+ and E-), but we can hide this edge until it satisfy 
    the condition both its vertices are existing in the vertex set and bot the vertices are added to set before edge.

- The above cases are about vertex and edge conflicts. For the same type of objects that added and deleted in same time,  
  we need some preference (e.g. if we get add(a, timestamp=8) and remove(a, timestamp=8)). In this implementation, removal has
  a higher preference - i.e. a simultaneously add and remove for same object will lead a removal of this object. This can be changed
  easily by changing the 'elements' methods in LwwSet, LwwVertexSet and LwwEdgeSet.

- The other decisions includes it only implements directed graph 
  (for undirected graph, it will be also a bi-directed so one can always implement this using add/remove edges for both side at same time using directed graph);
  and it also forbids self-connections (which will be buggy when one talk about path between 2 vertices if we allow it).
  
- The library is self-contained and with a self-implemented Lww-set to support it.

- Further optimisation:
  - Slow get neighbors for a vertex, the current solution is to iterate every edge. I am not sure if it can be done using
    adjacency list - not sure how could I implement a CRDT dict.

## RUN test
Developed with Python 3.8

```bash
cd Lww-state-graph
#for Lww Graph test
python -m unittest test.LwwGraphBasicTest
#for Lww Set test
python -m unittest test.LwwSetTest
```

## Install and Run
```python
from lww_graph.lww_graph.LwwDiGraph import LwwDiGraph
from lww_graph.lww_graph.edge.LwwTimedEdge import LwwTimedEdge
from lww_graph.lww_graph.vertex.LwwTimedVertex import LwwTimedVertex

        """
    The graph looks like the following, * represents an arrow.
                ----
              |     |
              *     |
         1 -* 2 - * 4 - * 5 -* 6
         |    *     |          *
         |    |     |          |
         | -* 3     -----------

        """

graph = LwwDiGraph() \
    .add_vertex(LwwTimedVertex(1, timestamp=1)) \
    .add_vertex(LwwTimedVertex(2, timestamp=1)) \
    .add_vertex(LwwTimedVertex(3, timestamp=1)) \
    .add_vertex(LwwTimedVertex(4, timestamp=1)) \
    .add_vertex(LwwTimedVertex(5, timestamp=1)) \
    .add_vertex(LwwTimedVertex(6, timestamp=1)) \
    .add_edge(LwwTimedEdge((1, 2), timestamp=3)) \
    .add_edge(LwwTimedEdge((1, 3), timestamp=3)) \
    .add_edge(LwwTimedEdge((3, 2), timestamp=3)) \
    .add_edge(LwwTimedEdge((2, 4), timestamp=3)) \
    .add_edge(LwwTimedEdge((4, 2), timestamp=3)) \
    .add_edge(LwwTimedEdge((4, 5), timestamp=3)) \
    .add_edge(LwwTimedEdge((5, 6), timestamp=3)) \
    .add_edge(LwwTimedEdge((4, 6), timestamp=3))

graph.list_all_path(1, 6)
>> [[1, 3, 2, 4, 6], [1, 3, 2, 4, 5, 6], [1, 2, 4, 6], [1, 2, 4, 5, 6]]
graph.edge_count()
>> 8
graph.vertex_count()
>> 6
graph.connected_vertices(1)
>> [3, 2]

```
    
    

  



