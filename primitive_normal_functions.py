SPHERE_NORMAL = """vec3 SphereNormal(vec3 hit_pos){
    return normalize(hit_pos-object_position);
}
"""
FLOOR_NORMAL = """vec3 FloorNormal(vec3 hit_pos){
    return vec3(0,1,0);
}"""