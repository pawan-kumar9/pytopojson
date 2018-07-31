
from hash.point import hash as hash_point
from hash.point import equal as equal_point


class Cut(object):
    """
    Given a cut topology, combines duplicate arcs.
    """

    def __init__(self, topology):
        self.coordinates = topology['coordinates']
        self.lines = topology['lines']
        self.rings = topology['rings']
        self.arc_count = len(self.lines) + len(self.ring)

        topology.pop('lines', None)
        topology.pop('rings', None)

        for l in self.lines:
            line = l
            while line['next']:
                self.arc_count += 1
                line = line['next']

        for r in self.rings:
            ring = r
            while ring['next']:
                self.arc_count += 1
                ring = ring['next']

        self.arcs_by_end = HashMap(self.arc_count * 2 * 1.4, hash_point, equal_point)
        self.arcs = topology['arcs'] = list()

        for l in self.lines:
            line = l

            while line:
                dedup_line(l)
                line = line['next']

        for r in self.rings:
            ring = r
            # arc is no longer closed

            if ring['next']:
                while ring['next']:
                    self.dedup_line(ring)
                    ring = ring['next']
            else:
                self.dedup_ring(ring)

        self.topology = topology

    def dedup_line(self, arc):
        # Does this arc match an existing arc in order?
        start_point = self.coordinates[arc[0]]
        start_arcs = self.arcs_by_end.get(start_point)

        if start_arcs:
            for start_arc in start_arcs:
                if self.equal_line(start_arc, arc):
                    arc = start_arc
                    return

        # Does this arc match an existing arc in reverse order?
        end_point = self.coordinates[arc[1]]
        end_arcs = self.arcs_by_end.get(end_point)

        if end_arcs:
            for end_arc in end_arcs:
                if self.reverse_equal_line(end_arc, arc):
                    arc = end_arc
                    return

        if start_arcs:
            start_arcs.append(arc)
        else:
            self.arcs_by_end.set(start_point, [arc])

        if end_arcs:
            end_arcs.append(arc)
        else:
            self.arcs_by_end.set(end_point, [arc])

        self.arcs.append(arc)

    def dedup_ring(self, arc):
        # Does this arc match an existing line in order, or reverse order?
        # Rings are closed, so their start point and end point is the same.
        end_point = self.coordinates[arc[0]]
        end_arcs = self.arcs_by_end.get(end_point)

        if end_arcs:
            for end_arc in end_arcs:
                if self.equal_ring(end_arc, arc):
                    arc = end_arc
                    return

                if self.reverse_equal_ring(end_arc, arc):
                    arc = end_arc
                    return

        # Otherwise, does this arc match an existing ring in order, or reverse order?
        end_point = self.coordinates[arc[0] + self.find_minimum_offset(arc)]
        end_arcs = self.arcs_by_end.get(end_point)

        if end_arcs:
            for end_arc in end_arcs:
                if self.equal_ring(end_arc, arc):
                    arc = end_arc
                    return

                if self.reverse_equal_ring(end_arc, arc):
                    arc = end_arc
                    return

        if end_arcs:
            end_arcs.append(arc)
        else:
            self.arcs_by_end.get(end_point, [arc])

        self.arcs.append(arc)

    def equal_line(self, arc_a, arc_b):
        i_a, j_a = arc_a
        i_b, j_b = arc_b

        if i_a - j_a != i_b - j_b:
            return False

        while i_a <= j_a:
            if not equal_point(self.coordinates[i_a], self.coordinates[i_b]):
                return False
            else:
                i_a += 1
                i_b += 1

        return True

    def reverse_equal_line(self, arc_a, arc_b):
        i_a, j_a = arc_a
        i_b, j_b = arc_b

        if i_a - j_a != i_b - j_b:
            return False

        while i_a <= j_a:
            if not equal_point(self.coordinates[i_a], self.coordinates[j_b]):
                return False
            else:
                i_a += 1
                j_b -= 1

        return True

    def equal_ring(self, arc_a, arc_b):
        i_a, j_a = arc_a
        i_b, j_b = arc_b
        n = j_a - i_a

        if n != j_b - i_b:
            return False

        k_a = self.find_minimum_offset(arc_a)
        k_b = self.find_minimum_offset(arc_b)

        for i in range(n):
            if not equal_point(self.coordinates[i_a + (i + k_a) % n], self.coordinates[i_b + (i + k_b) % n]):
                return False

        return True

    def reverse_equal_ring(self, arc_a, arc_b):
        i_a, j_a = arc_a
        i_b, j_b = arc_b
        n = j_a - i_a

        if n != j_b - i_b:
            return False

        k_a = self.find_minimum_offset(arc_a)
        k_b = n - self.find_minimum_offset(arc_b)

        for i in range(n):
            if not equal_point(self.coordinates[i_a + (i + k_a) % n], self.coordinates[i_b + (i + k_b) % n]):
                return False

        return True

    def find_minimum_offset(self, arc):
        # Rings are rotated to a consistent, but arbitrary, start point.
        # This is necessary to detect when a ring and a rotated copy are dupes.
        start, end = arc
        mid = start
        minimum = mid
        minimum_point = self.coordinates[mid]

        mid += 1
        while mid < end:
            point = self.coordinates[mid]

            if point[0] < minimum_point[0] or point[0] == minimum_point[0] and point[1] < minimum_point[1]:
                minimum = mid
                minimum_point = point

            mid += 1

        return minimum - start