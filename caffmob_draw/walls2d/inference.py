"""Alinhamento da mira do editor de paredes (feature 009, T012; RN-02, D-01). Python puro.

As referências são os vértices do plano e o ponto inicial do desenho. Duas listas ordenadas (por X e por Y) e
`bisect` dão a referência mais próxima em cada eixo em O(log n) por movimento do mouse. A tolerância chega em metros
(`8 px / escala da vista`), então a trava vale o mesmo na tela em qualquer zoom.
"""

from bisect import bisect_left


class Index:
    def __init__(self, points):
        pts = [(float(p[0]), float(p[1])) for p in points]
        self.by_x = sorted(pts)
        self.xs = [p[0] for p in self.by_x]
        self.by_y = sorted(pts, key=lambda p: (p[1], p[0]))
        self.ys = [p[1] for p in self.by_y]

    @staticmethod
    def _nearest(keys, items, value, tol, axis, exclude):
        best = None
        i = bisect_left(keys, value - tol)
        while i < len(keys) and keys[i] <= value + tol:
            point = items[i]
            if point not in exclude:
                dist = abs(point[axis] - value)
                if best is None or dist < best[0]:
                    best = (dist, point)
            i += 1
        return best[1] if best else None

    def query(self, cursor, tol, exclude=()):
        """(x travado, referência X, y travado, referência Y); None no eixo que não trava."""
        exclude = {(float(p[0]), float(p[1])) for p in exclude}
        ref_x = self._nearest(self.xs, self.by_x, cursor[0], tol, 0, exclude)
        ref_y = self._nearest(self.ys, self.by_y, cursor[1], tol, 1, exclude)
        return (ref_x[0] if ref_x else None, ref_x, ref_y[1] if ref_y else None, ref_y)


def plan_points(plan, extra=()):
    """Vértices de todas as cadeias do plano (`walls2d.model`), mais pontos extras (ex.: o início do desenho)."""
    points = [tuple(node) for chain in plan.chains for node in chain.nodes]
    return points + [tuple(p) for p in extra]
