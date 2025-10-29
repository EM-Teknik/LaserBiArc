import math
import sys

# ------------------------
# Global constants
# ------------------------
eps = 0.0001
maxiter = 10

# ------------------------
# Helper vector functions
# ------------------------
def add(v, w):
    return (v[0] + w[0], v[1] + w[1])

def sub(v, w):
    return (v[0] - w[0], v[1] - w[1])

def mul(s, v):
    return (s * v[0], s * v[1])

def div(v, s):
    return (v[0] / s, v[1] / s)

def dot(v, w):
    return v[0]*w[0] + v[1]*w[1]

def quadrance(v):
    return dot(v, v)

def length(v):
    return math.sqrt(quadrance(v))

def normalize(v):
    l = length(v)
    if l == 0:
        return (0,0)
    return (v[0]/l, v[1]/l)

# ------------------------
# if' function (ternary operator)
# ------------------------
def if_(cond, a, b):
    return a if cond else b

# ------------------------
# Point conversion helper (identity in this case)
# ------------------------
def toPoint(p):
    return p

# ------------------------
# Line class and utilities (Graphics.Line)
# ------------------------
class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    # Slope: returns float or math.nan if vertical
    @property
    def _m(self):
        dx = self.p2[0] - self.p1[0]
        dy = self.p2[1] - self.p1[1]
        if abs(dx) < eps:
            return float('nan')
        return dy/dx

def isOnLine(line, p):
    # Check if point p is collinear with line.p1 and line.p2 using cross product
    v = sub(line.p2, line.p1)
    w = sub(p, line.p1)
    cross = v[0]*w[1] - v[1]*w[0]
    return abs(cross) < eps

def fromPoints(p1, p2):
    return Line(p1, p2)

def intersection(l1, l2):
    # Line l1: p1 + t*(p2-p1), l2: q1 + u*(q2-q1)
    p = l1.p1
    r = sub(l1.p2, l1.p1)
    q = l2.p1
    s = sub(l2.p2, l2.p1)
    rxs = r[0]*s[1] - r[1]*s[0]
    if abs(rxs) < eps:
        return (float('nan'), float('nan'))
    t = ((q[0]-p[0])*s[1] - (q[1]-p[1])*s[0]) / rxs
    return add(p, mul(t, r))

# ------------------------
# PathCommand classes (Graphics.Path)
# ------------------------
class PathCommand:
    pass

class LineTo(PathCommand):
    def __init__(self, point):
        self.point = point

class ArcTo(PathCommand):
    def __init__(self, center, endpoint, isClockwise):
        self.center = center
        self.endpoint = endpoint
        self.isClockwise = isClockwise

# ------------------------
# CubicBezier class (Graphics.CubicBezier)
# ------------------------
class CubicBezier:
    def __init__(self, p1, c1, c2, p2):
        self._p1 = p1
        self._c1 = c1
        self._c2 = c2
        self._p2 = p2

    def pointAt(self, t):
        # Cubic Bezier evaluation using de Casteljau algorithm
        u = 1 - t
        p1 = self._p1
        c1 = self._c1
        c2 = self._c2
        p2 = self._p2
        part1 = mul(u**3, p1)
        part2 = mul(3 * u**2 * t, c1)
        part3 = mul(3 * u * t**2, c2)
        part4 = mul(t**3, p2)
        return add(add(part1, part2), add(part3, part4))

    def firstDerivativeAt(self, t):
        u = 1 - t
        p1 = self._p1
        c1 = self._c1
        c2 = self._c2
        p2 = self._p2
        term1 = mul(3 * u**2, sub(c1, p1))
        term2 = mul(6 * u * t, sub(c2, c1))
        term3 = mul(3 * t**2, sub(p2, c2))
        return add(add(term1, term2), term3)

    def secondDerivativeAt(self, t):
        u = 1 - t
        p1 = self._p1
        c1 = self._c1
        c2 = self._c2
        p2 = self._p2
        term1 = mul(6 * u, sub(c2, c1))
        term2 = mul(6 * t, sub(p2, c2))
        return add(term1, term2)

    def splitAt(self, t):
        # de Casteljau splitting
        p0 = self._p1
        p1 = self._c1
        p2 = self._c2
        p3 = self._p2
        q0 = lerp(p0, p1, t)
        q1 = lerp(p1, p2, t)
        q2 = lerp(p2, p3, t)
        r0 = lerp(q0, q1, t)
        r1 = lerp(q1, q2, t)
        s = lerp(r0, r1, t)
        first = CubicBezier(p0, q0, r0, s)
        second = CubicBezier(s, r1, q2, p3)
        return (first, second)

    def inflectionPoints(self):
        # For simplicity, we return an empty list.
        # A full inflection point calculation is complex.
        return []

    def maxArcLength(self):
        # For approximation, return chord length between endpoints.
        return distance(self._p1, self._p2)

    def isClockwise(self):
        # Approximate as orientation given by p1, midpoint and p2.
        mid = self.pointAt(0.5)
        return isClockwise3(self._p1, self._p2, mid)

# Helper: linear interpolation between two points
def lerp(p, q, t):
    return add(mul(1-t, p), mul(t, q))

# ------------------------
# CircularArc class (Graphics.CircularArc)
# ------------------------
class CircularArc:
    def __init__(self, p_start, center, p_end, radius, isClockwise):
        self._p1 = p_start  # starting point
        self._c = center    # center of the circle
        self._p2 = p_end    # endpoint of the arc
        self._r = radius    # radius of the arc
        self._isClockwise = isClockwise

    @property
    def isClockwise(self):
        return self._isClockwise

# ------------------------
# BiArc class (Graphics.BiArc)
# ------------------------
class BiArc:
    def __init__(self, a1, a2):
        self._a1 = a1
        self._a2 = a2
    @property
    def jointAt(self):
        # fixed joint parameter for biarc, as used in the code
        return 0.5

# ------------------------
# Functions to compute a circle given a point, tangent, and another point
# ------------------------
def circle_from_point_tangent_and_point(p, d, q):
    # d is the tangent direction at p. We use the normal to d.
    d_norm = normalize(d)
    n = (-d_norm[1], d_norm[0])
    # Solve for lambda: ||p + lambda*n - q||^2 = lambda^2.
    diff = sub(p, q)
    numerator = quadrance(diff)
    denominator = 2 * dot(diff, n)
    # Avoid division by zero:
    if abs(denominator) < eps:
        lambda_val = 0
    else:
        lambda_val = - numerator / denominator
    center = add(p, mul(lambda_val, n))
    radius = abs(lambda_val)
    return center, radius

# ------------------------
# BA.fromPoints (Graphics.BiArc.fromPoints)
# Given p1, d1, p2, d2, and g, construct a BiArc approximation.
def BA_fromPoints(p1, d1, p2, d2, g):
    # For arc a1: from p1 to g using tangent d1 at p1.
    center1, r1 = circle_from_point_tangent_and_point(p1, d1, g)
    # Direction: determine isClockwise by checking cross product sign.
    v1 = sub(p1, center1)
    v2 = sub(g, p1)
    cw1 = (v1[0]*v2[1] - v1[1]*v2[0]) < 0

    a1 = CircularArc(p1, center1, g, r1, cw1)

    # For arc a2: from p2 to g. Invert tangent (because at endpoint, derivative is undefined)
    d2_inv = mul(-1, d2)
    center2, r2 = circle_from_point_tangent_and_point(p2, d2_inv, g)
    # For a2, the arc goes from g to p2.
    v1b = sub(p2, center2)
    v2b = sub(g, p2)
    cw2 = (v1b[0]*v2b[1] - v1b[1]*v2b[0]) < 0

    a2 = CircularArc(g, center2, p2, r2, cw2)

    return BiArc(a1, a2)

# ------------------------
# CA helpers to access CircularArc properties
# ------------------------
def CA__c(arc):
    return arc._c

def CA__p2(arc):
    return arc._p2

def CA_isClockwise(arc):
    return arc.isClockwise

def CA__r(arc):
    return arc._r

# ------------------------
# BA helpers to access BiArc properties
# ------------------------
def BA_jointAt(biarc):
    return biarc.jointAt

def BA__a1(biarc):
    return biarc._a1

def BA__a2(biarc):
    return biarc._a2

# ------------------------
# isClockwise3: determines if three points are in clockwise order.
# ------------------------
def isClockwise3(p1, p2, p3):
    # Compute the cross product of vector (p2-p1) and (p3-p1)
    cp = (p2[0]-p1[0])*(p3[1]-p1[1]) - (p2[1]-p1[1])*(p3[0]-p1[0])
    return cp < 0

# ------------------------
# pointAt for a BiArc: parameter t in [0,1]
# ------------------------
def pointAt_biarc(biarc, t):
    # For t in [0, jointAt] use arc a1, for t in (jointAt,1] use arc a2.
    joint = BA_jointAt(biarc)
    if t <= joint:
        # Parameterize arc a1 from 0 to 1.
        a = BA__a1(biarc)
        return pointAt_arc(a, t/joint if joint > 0 else 0)
    else:
        a = BA__a2(biarc)
        return pointAt_arc(a, (t - joint)/(1 - joint) if (1-joint) > 0 else 0)

def pointAt_arc(arc, u):
    # Compute angle at start and end then interpolate.
    # Vector from center to start and end.
    v_start = sub(arc._p1, arc._c)
    v_end = sub(arc._p2, arc._c)
    ang1 = math.atan2(v_start[1], v_start[0])
    ang2 = math.atan2(v_end[1], v_end[0])
    # Ensure the shortest angular distance respecting orientation
    # Adjust angles based on isClockwise flag.
    if arc._isClockwise:
        if ang1 < ang2:
            ang1 += 2*math.pi
        angle = ang1 - u*(ang1 - ang2)
    else:
        if ang2 < ang1:
            ang2 += 2*math.pi
        angle = ang1 + u*(ang2 - ang1)
    return add(arc._c, (arc._r * math.cos(angle), arc._r * math.sin(angle)))

# ------------------------
# pointAt for a Bezier (wrapper)
# ------------------------
def pointAt_bezier(bezier, t):
    return bezier.pointAt(t)

# ------------------------
# distance between two points
# ------------------------
def distance(p, q):
    return length(sub(p, q))

# ------------------------
# biarc2path (Graphics.BiArc => [PathCommand])
# ------------------------
def biarc2path(biarc):
    arcs = [BA__a1(biarc), BA__a2(biarc)]
    path = []
    for arc in arcs:
        path.append(ArcTo(toPoint(CA__c(arc)), toPoint(CA__p2(arc)), CA_isClockwise(arc)))
    return path

# ------------------------
# isStable (heuristics for unstable biarc)
# ------------------------
def isStable(biarc):
    a1 = BA__a1(biarc)
    a2 = BA__a2(biarc)
    cond1 = CA__r(a1) > 99999 or CA__r(a1) < 0.001
    cond2 = CA__r(a2) > 99999 or CA__r(a2) < 0.001
    return not (cond1 or cond2)

# ------------------------
# findRoot: Newton-bisection hybrid root finder.
# ------------------------
def findRoot(f, df, lowerBound, upperBound):
    fl = f(lowerBound)
    fu = f(upperBound)
    if fl * fu > 0:
        return -1
    if abs(fl) < eps:
        return lowerBound
    if abs(fu) < eps:
        return upperBound
    root = (lowerBound + upperBound) / 2
    for i in range(maxiter):
        fx = f(root)
        if abs(fx) < eps:
            return root
        h = fx / df(root) if abs(df(root)) > eps else 0
        n = root - h
        if n < lowerBound or n > upperBound:
            # use bisection step
            if fl * fx < 0:
                new_ub = root
                n = (lowerBound + root) / 2
                fu = fx
            else:
                new_lb = root
                n = (root + upperBound) / 2
                fl = fx
        root = n
    return root

# ------------------------
# findRadialIntersection
# ------------------------
def findRadialIntersection(bezier, biarc, t):
    if t == 0 or t == 1:
        return t
    p = pointAt_biarc(biarc, t)
    a = BA__a1(biarc) if (t <= BA_jointAt(biarc)) else BA__a2(biarc)
    c = CA__c(a)
    m = sub(p, c)
    h = normalize((-m[1], m[0]))
    def f(u):
        return dot(sub(pointAt_bezier(bezier, u), p), h)
    def df(u):
        return dot(bezier.firstDerivativeAt(u), h)
    return findRoot(f, df, 0, 1)

# ------------------------
# calculateMaxDistance
# ------------------------
def calculateMaxDistance(bezier, biarc):
    tj = findRadialIntersection(bezier, biarc, BA_jointAt(biarc))
    if tj == -1:
        return (0.5, sys.float_info.max)
    pj = pointAt_bezier(bezier, tj)
    pb = pointAt_biarc(biarc, BA_jointAt(biarc))
    dj = distance(pj, pb)
    a1 = BA__a1(biarc)
    a2 = BA__a2(biarc)
    def g(arc, u):
        return dot(sub(pointAt_bezier(bezier, u), CA__c(arc)), bezier.firstDerivativeAt(u))
    def gprime(arc, u):
        return quadrance(bezier.firstDerivativeAt(u)) + dot(sub(pointAt_bezier(bezier, u), CA__c(arc)), bezier.secondDerivativeAt(u))
    def bigger(f_tuple, s_tuple):
        (f_t, f_d) = f_tuple
        (s_t, s_d) = s_tuple
        if s_t == -1:
            return f_tuple
        return f_tuple if f_d > s_d else s_tuple
    t0 = findRoot(lambda u: g(a1, u), lambda u: gprime(a1, u), eps, tj)
    d0 = abs(distance(pointAt_bezier(bezier, t0), CA__c(a1)) - CA__r(a1))
    t1 = findRoot(lambda u: g(a2, u), lambda u: gprime(a2, u), tj, 1 - eps)
    d1 = abs(distance(pointAt_bezier(bezier, t1), CA__c(a2)) - CA__r(a2))
    return bigger(bigger((tj, dj), (t0, d0)), (t1, d1))

# ------------------------
# Main function: bezier2biarcs (Approx.BiArc.bezier2biarcs)
# ------------------------
def bezier2biarcs(mbezier, resolution):
    # Degenerate curve: all points on the same line -> it is a line 
    if (isOnLine(fromPoints(mbezier._p2, mbezier._p1), mbezier._c1) and
        isOnLine(fromPoints(mbezier._p2, mbezier._p1), mbezier._c2)):
        return [LineTo(toPoint(mbezier._p2))]
    # Degenerate curve: p1 == c1, don't split
    elif mbezier._p1 == mbezier._c1:
        return approxSpiral(mbezier, resolution)
    # Degenerate curve: p2 == c2, don't split
    elif mbezier._p2 == mbezier._c2:
        return approxSpiral(mbezier, resolution)
    else:
        ip = mbezier.inflectionPoints()
        return byInflection(mbezier, ip, resolution)

def byInflection(mbezier, ts, resolution):
    def order(a, b):
        return (a, b) if b >= a else (b, a)
    if len(ts) == 1:
        (b1, b2) = mbezier.splitAt(ts[0])
        return approxSpiral(b1, resolution) + approxSpiral(b2, resolution)
    elif len(ts) == 2:
        it1, it2_prime = order(ts[0], ts[1])
        it2 = (1 - it1) * it2_prime
        (b1, toSplit) = mbezier.splitAt(it1)
        (b2, b3) = toSplit.splitAt(it2)
        return approxSpiral(b1, resolution) + approxSpiral(b2, resolution) + approxSpiral(b3, resolution)
    else:
        return approxSpiral(mbezier, resolution)

def approxSpiral(bezier, resolution):
    # Approximate bezier length. if max length is smaller than resolution, do not approximate
    if bezier.maxArcLength() < resolution:
        return [LineTo(toPoint(bezier._p2))]
    # Edge case: start- and endpoints are the same
    elif bezier._p1 == bezier._p2:
        return splitAndRecur(bezier, 0.5, resolution)
    else:
        # Determine control points for derivative approximation
        c1 = if_(bezier._p1 == bezier._c1, bezier._c2, bezier._c1)
        c2 = if_(bezier._p2 == bezier._c2, bezier._c1, bezier._c2)
        t1 = fromPoints(bezier._p1, c1)
        t2 = fromPoints(bezier._p2, c2)
        # Edge case: control lines are parallel
        m1 = t1._m
        m2 = t2._m
        if (m1 == m2) or (math.isnan(m1) and math.isnan(m2)):
            return splitAndRecur(bezier, 0.5, resolution)
        # V: Intersection point of tangent lines
        v = intersection(t1, t2)
        # Biarc triangle has the wrong orientation
        if (bezier.isClockwise() != isClockwise3(bezier._p1, bezier._p2, v)):
            return splitAndRecur(bezier, 0.5, resolution)
        # Compute distances for incenter computation
        dP2V = distance(bezier._p2, v)
        dP1V = distance(bezier._p1, v)
        dP1P2 = distance(bezier._p1, bezier._p2)
        sum_d = dP2V + dP1V + dP1P2
        if abs(sum_d) < eps:
            g = (0,0)
        else:
            g = div(add(add(mul(dP2V, bezier._p1), mul(dP1V, bezier._p2)), mul(dP1P2, v)), sum_d)
        # Calculate the BiArc
        # d1 = p1 - c1, d2 = p2 - c2
        d1 = sub(bezier._p1, c1)
        d2 = sub(bezier._p2, c2)
        biarc = BA_fromPoints(bezier._p1, d1, bezier._p2, d2, g)
        (maxDistanceAt, maxDistance) = calculateMaxDistance(bezier, biarc)
        if not isStable(biarc):
            return splitAndRecur(bezier, 0.5, resolution)
        elif maxDistance > resolution:
            return splitAndRecur(bezier, maxDistanceAt, resolution)
        else:
            return biarc2path(biarc)

def splitAndRecur(bezier, t, resolution):
    (b1, b2) = bezier.splitAt(t)
    return approxSpiral(b1, resolution) + approxSpiral(b2, resolution)

# ------------------------
# Exports
# ------------------------
# The module exports only bezier2biarcs
# Example usage:
#   bez = CubicBezier((0,0), (1,2), (2,2), (3,0))
#   cmds = bezier2biarcs(bez, 0.1)
#   for cmd in cmds:
#       if isinstance(cmd, LineTo):
#           print("LineTo", cmd.point)
#       elif isinstance(cmd, ArcTo):
#           print("ArcTo", cmd.center, cmd.endpoint, cmd.isClockwise)

if __name__ == '__main__':
    # A simple test example:
    bez = CubicBezier((0, 0), (1, 2), (2, 2), (3, 0))
    cmds = bezier2biarcs(bez, 0.1)
    for cmd in cmds:
        if isinstance(cmd, LineTo):
            print("LineTo", cmd.point)
        elif isinstance(cmd, ArcTo):
            print("ArcTo", cmd.center, cmd.endpoint, cmd.isClockwise)
    
# End of module Approx.BiArc
