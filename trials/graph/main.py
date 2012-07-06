import copy


#
#
#
#

class VertexError(Exception):
    pass

class Vertex(object):
    """A vertex part of a "double vertex"
    """
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.edges = []
        self.partner = None # the "partner" vertex

    def addEdge(self, vertex):
        if vertex not in self.edges:
            print "add edge {}-{}".format(self.name, vertex.name)
            self.edges.append(vertex)

    def connected(self):
        """returns all connected vertices
        """
        return self.edges

    def connectedFromPartner(self):
        """returns all connected vertices of our "partner" double vertex
        """
        pass

class Graph(object):
    """
    Graph class that supports double vertices for use in railway network
    computation, like described by Markus Montigel 1992
    """
    def __init__(self):
        self.vertices = {}

    def addVertex(self, vertex):
        if vertex in self.vertices:
            raise VertexError("Vertex {} already in Graph".format(vertex))

        self.vertices[vertex.name] = vertex
        vertex.graph = self
        return vertex

    def addEdge(self, vertex_a, vertex_b):
        vertex_a.addEdge(vertex_b)
        vertex_b.addEdge(vertex_a)

    def addVerticesFrom(self, subgraph):
        for vertex in subgraph.vertices.itervalues():
            self.addVertex(vertex)

    def vertexByName(self, name):
        if name in self.vertices:
            return self.vertices[name]
        else:
            raise IndexError

    def addElementGraph(self, element):
        """Add all vertices of the track element into
        this graph
        """
        self.addVerticesFrom(element.graph)

    def connectVertices(self, vertex_a, vertex_b):
        """Connect two vertices a and b to be a double vertex
        """
        if vertex_a.name not in self.vertices or vertex_b.name not in self.vertices:
            raise VertexError("Warning: At least one of the vertices {} and {} is not in the graph".format(vertex_a, vertex_b))
        if vertex_a.partner is not None or vertex_b.partner is not None:
            raise VertexError("Warning: At least one of the vertices {} and {} is already a double vertex".format(vertex_a, vertex_b))

        vertex_a.partner = vertex_b
        vertex_b.partner = vertex_a

    def doubleAllSingleVertices(self):
        """
        Find all vertices that are not mapped to a corresponding sibling, create
        an artifical sibling vertices an tie them together

        Note: Call after all track connecting work is done, because after this
        method has been called, all vertices will be double and no further connections
        can be made.
        """
        for vertex in self.vertices.values():
            if not vertex.partner:
                self.connectVertices(vertex, self.addVertex(Vertex("{}_*".format(vertex.name))))

    def copy(self):
        """ Returns a deep copy of the graph
        """
        G = copy.deepcopy(self)

        return G

    def findPath(self, startVertex, endVertex):
        def findPathR(p, v_end):
            v_last = p[-1]
            print "------------------"
            print v_last.name
            if v_last.attributes["mark"] == "NotOK" \
                            or v_last.partner.attributes["mark"] != "Unknown":
                return
            if v_last==v_end:
                v_last.attributes["mark"] = "OK"
                solutions.append(p)
                print "found solution: {}".format(map(lambda x: x.name,p))
                return
            if v_last.attributes["mark"] == "Unknown":
                v_last.attributes["mark"] = "NotOK"
                found_path = False
                print "connected to the partner {} of {} are:".format(v_last.partner.name, v_last.name)
                for v_connected in v_last.partner.connected():
                    print v_connected.name
                    findPathR(p + [v_connected], v_end)
                    if v_connected.attributes["mark"] == "OK":
                        found_path = True
                if found_path:
                    v_last.attributes["mark"] = "OK"
            else:
                for v_connected in v_last.partner.connected():
                    print v_connected.name
                    findPathR(p + [v_connected], v_end)


        G = self.copy()

        for vertex in G.vertices.itervalues():
            vertex.attributes["mark"] = "Unknown"

        solutions = []
        findPathR([G.vertexByName(startVertex)], G.vertexByName(endVertex))
        return solutions

class TrackElement(object):
    def __init__(self, id):
        self.id = id
        self.vertices = {}

        # SUBGRAPH
        self.graph = Graph()

class Track(TrackElement):
    def __init__(self, id):
        TrackElement.__init__(self, id)
        self.vertices['a'] = Vertex("{}_A".format(self.id))
        self.vertices['b'] = Vertex("{}_B".format(self.id))

        # SUBGRAPH
        self.graph.addVertex(self.vertices['a'])
        self.graph.addVertex(self.vertices['b'])
        self.graph.addEdge(self.vertices['a'], self.vertices['b'])

class Switch(TrackElement):
    def __init__(self, id):
        TrackElement.__init__(self, id)
        self.vertices['a'] = Vertex("{}_A".format(self.id))
        self.vertices['b'] = Vertex("{}_B".format(self.id))
        self.vertices['c'] = Vertex("{}_C".format(self.id))

        # SUBGRAPH
        self.graph.addVertex(self.vertices['a'])
        self.graph.addVertex(self.vertices['b'])
        self.graph.addVertex(self.vertices['c'])
        self.graph.addEdge(self.vertices['a'], self.vertices['b'])
        self.graph.addEdge(self.vertices['a'], self.vertices['c'])



def simpleExample():
    #
    #  1_A --- 1_B/3_A --- 3_B/3_B_*
    #                  \
    #                   \
    #                    3_C/2_A --- 2_B/2_B_*
    #
    elements = [Track(1), Track(2), Switch(3)]

    G = Graph()

    for el in elements:
        G.addElementGraph(el)

    # connect the track elements
    G.connectVertices(G.vertexByName("1_B"), G.vertexByName("3_A"))
    G.connectVertices(G.vertexByName("3_C"), G.vertexByName("2_A"))

    # make the remaining single vertices to double vertices (all endpoints of the net)
    G.doubleAllSingleVertices()

    #print G.vertices
    #print G.edges
    #print G.doubleVertices

    G.findPath("1_A_*", "3_B")

def mediumExample():
    #
    #  4_A_*/4_A --- 4_B/1_B --- 1_A/3_A --- 3_B/7_B -------------- 7_A/8_A --- 8_B/8_B_*
    #                          /         \                       /
    #                        /            \                    /
    #                   1_C                3_C             7_C
    #                  5_C                  6_C           2_C
    #                /                       \           /
    #              /                          \         /
    #  5_A_*/5_A --- 5_B/6_B ---------------- 6_A/2_A --- 2_B/2_B_*
    #
    elements = [Switch(1), Switch(2), Switch(3), Track(4), Switch(5), Switch(6), Switch(7), Track(8)]

    G = Graph()

    for el in elements:
        G.addElementGraph(el)

    # connect the track elements
    G.connectVertices(G.vertexByName("4_B"), G.vertexByName("1_B"))
    G.connectVertices(G.vertexByName("1_C"), G.vertexByName("5_C"))
    G.connectVertices(G.vertexByName("1_A"), G.vertexByName("3_A"))
    G.connectVertices(G.vertexByName("5_B"), G.vertexByName("6_B"))
    G.connectVertices(G.vertexByName("3_B"), G.vertexByName("7_B"))
    G.connectVertices(G.vertexByName("3_C"), G.vertexByName("6_C"))
    G.connectVertices(G.vertexByName("6_A"), G.vertexByName("2_A"))
    G.connectVertices(G.vertexByName("2_C"), G.vertexByName("7_C"))
    G.connectVertices(G.vertexByName("7_A"), G.vertexByName("8_A"))


    # make the remaining single vertices to double vertices (all endpoints of the net)
    G.doubleAllSingleVertices()

    print G.findPath("4_A_*", "8_B")
    print G.findPath("4_A_*", "5_B")
    print G.findPath("5_A_*", "5_B")

#simpleExample()
mediumExample()
