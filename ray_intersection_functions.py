SPHERE_INTERSECT = """float raySphereIntersect(vec3 r0, vec3 rd,vec3 obj_pos,float sr) {
    // - r0: ray origin
    // - rd: normalized ray direction
    // - obj_pos: sphere center
    // - sr: sphere radius
    // - Returns distance from r0 to first intersecion with sphere,
    //   or -1.0 if no intersection.
    float a = dot(rd, rd);
    vec3 obj_pos_r0 = r0 - obj_pos;
    float b = 2.0 * dot(rd, obj_pos_r0);
    float c = dot(obj_pos_r0, obj_pos_r0) - (sr * sr);
    if (b*b - 4.0*a*c < 0.0) {
        return -1.0;
    }
    return (-b - sqrt((b*b) - 4.0*a*c))/(2.0*a);
}"""
FLOOR_INTERSECT = """float rayGroundIntersect(vec3 rayOrigin, vec3 rayDir,vec3 obj_pos) {
    vec3 normal = vec3(0,1,0);
    float denom = dot(normal,rayDir);
    if (abs(denom) > 0.001) // your favorite epsilon
    {
        float t = dot((obj_pos - rayOrigin),normal) / denom;
        if (t >= 0.001){
            return t;
        }
    }
    return -1.0;
}"""

TRIANGLE_INTERSECT = """
vec3 IntersectPlane(vec3 r0, vec3 rd, vec3 p0, vec3 p1, vec3 p2)
{
    vec3 D = rd;
    vec3 N = cross(p1-p0, p2-p0);
    vec3 X = r0 + D * dot(p0 - r0, N) / dot(D, N);

    return X;
}"""