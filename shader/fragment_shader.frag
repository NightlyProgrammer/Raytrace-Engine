#version 330 core

#define PI 3.14159265359

layout (location = 0) out vec4 fragColor;

in vec2 fragPos;
in vec2 uv;

uniform vec3 camera_pos;
uniform vec3 camera_rotation;
uniform float fov;
uniform sampler2D background_image;
uniform sampler2D hud_image;

struct PrimitiveObj{
    int normal_fun_name;
    float dist;
    vec3 color;
    vec3 second_color;
    float reflectiveness;
    //float refractiveness;
};

mat3 rotation(int axis,float angle){
    switch (axis){
        case 0:
            //x axis
            return mat3(
                1,0,0,
                0,cos(angle),-sin(angle),
                0,sin(angle),cos(angle)
            );
        case 1:
            //y axis
            return mat3(
                cos(angle),0,sin(angle),
                0,1,0,
                -sin(angle),0,cos(angle)
            );
        case 2:
            //z axis
            return mat3(
                cos(angle),-sin(angle),0,
                sin(angle),cos(angle),0,
                0,0,1
            );
    }
}

#define_normal_functions#//defines the normal functions of the multiple objects in the scene

#define_normal_function#//defines the final get_normal function that gets called

#define_intersect_functions#

PrimitiveObj raytrace(vec3 ray_origin,vec3 dir){
    #calc_distance#//save dist in a float named dist
    return PrimitiveObj(id,dist,color,color2,kr);
}

float calcShadow(vec3 ray_origin,vec3 dir,vec3 end_pos){
    float dist = raytrace(ray_origin,dir).dist;
    if(dist>0.01 && dist<distance(ray_origin,end_pos)){
        return 0;
    }
    return 1;
}

vec3 phong_shader(vec3 color,vec3 hit_pos,vec3 direction,vec3 light_pos,vec3 light_color,vec3 normal){
    //edit later to use a light struct for the light pos,ambient diffuse spec etc
    vec3 light_dir = normalize(light_pos-hit_pos);

    float ambient_strength = 0.2;
    vec3 ambient = ambient_strength*light_color;

    float diff = max(dot(normal, light_dir), 0.0);
    vec3 diffuse = diff*light_color;

    vec3 specular;
    if(diff>0.0){
        float specularStrength = 0.6;

        vec3 reflectDir = reflect(-light_dir,normal);  
        float spec = pow(max(dot(direction, reflectDir), 0.0), 16);
        specular = specularStrength * spec * light_color;
    }
    float shadow = calcShadow(hit_pos,normalize(vec3(1,2,1)-hit_pos),vec3(1,2,1));
    return (ambient+(diffuse+specular)*shadow)*color;
            
}

vec3 reflection(vec3 color,vec3 hit_pos,vec3 direction,vec3 normal,float reflectiveness){
    int reflection_iterations = 10;
    //kr = reflection mix value aka how much does the color of the reflection affect this obj color
    float kr = reflectiveness;
    vec3 dir = reflect(direction,normal);
    vec3 reflection_hit_pos = hit_pos;
    vec3 hit_normal = normal;
    PrimitiveObj hit_object;
    float density = 0.01;
    vec3 bg_color;
    for(int i;i<reflection_iterations;i++){
        hit_object = raytrace(reflection_hit_pos,dir);
        float fog_k =  1/exp(pow(hit_object.dist * density,2));
        float sphere_uv_x = atan(dir.z,dir.x)/(2*PI);
        float sphere_uv_y = atan(dir.y,sqrt(pow(dir.z,2)+pow(dir.x,2)))/(PI)+0.5;
        bg_color = texture2D(background_image,vec2(-sphere_uv_x,-sphere_uv_y)).rgb*kr+color*(1-kr);
        if(hit_object.dist>0){
            
            reflection_hit_pos = reflection_hit_pos+dir*hit_object.dist;
            vec3 obj_color = hit_object.color*fog_k;
            if(hit_object.second_color != vec3(0,0,0)){//for checker board
                float scale = 5.0;
                bool isEven = mod(floor(reflection_hit_pos.x/scale)+floor(reflection_hit_pos.z/scale),2)==0;
                obj_color = isEven ? hit_object.color : hit_object.second_color;
            }
            color = phong_shader(obj_color,reflection_hit_pos,dir,vec3(1,2,1),vec3(1,1,1),hit_normal)*kr+color*(1-kr);
            
            hit_normal = get_normal(reflection_hit_pos,hit_object.normal_fun_name);
            dir = reflect(dir,hit_normal);
            kr = hit_object.reflectiveness;
        }else{
            fog_k = 0;
            i = reflection_iterations;
        }
        color = color*fog_k+bg_color*(1-fog_k);
    }
    return color;
}

/*vec3 refraction(){
    pass
}*/

vec3 calculateColor(vec3 ray_origin,vec3 dir){
    PrimitiveObj hit_obj = raytrace(ray_origin,dir);
    vec3 color;
    float dist = hit_obj.dist;
    float density = 0.01;
    float fog_k =  1/exp(pow(dist * density,2));
    if(dist>0){
        color = hit_obj.color;
        vec3 hit_pos = ray_origin+dir*dist;
        if(hit_obj.second_color != vec3(0,0,0)){//for checker board
            float scale = 5.0;
            bool isEven = mod(floor(hit_pos.x/scale)+floor(hit_pos.z/scale),2)==0;
            color = isEven ? hit_obj.color : hit_obj.second_color;
        }
        vec3 normal = get_normal(hit_pos,hit_obj.normal_fun_name);
        color = phong_shader(color,hit_pos,dir,vec3(1,2,1),vec3(1,1,1),normal);
        color = reflection(color,hit_pos,dir,normal,hit_obj.reflectiveness);
        //color = phong_shader(color,hit_pos,dir,vec3(1,2,1),vec3(1,1,1),normal);
        
        
    }else{
        fog_k = 0;
    }
    //calcualte color of 360 img
    float sphere_uv_x = atan(dir.z,dir.x)/(2*PI);
    float sphere_uv_y = atan(dir.y,sqrt(pow(dir.z,2)+pow(dir.x,2)))/(PI)+0.5;
    vec3 bg_color = texture2D(background_image,vec2(-sphere_uv_x,-sphere_uv_y)).rgb;

    
    return color*fog_k+(1-fog_k)*bg_color;
}

void main(){
    float cam_to_screen = 1/tan(fov/2);
    vec3 pos = vec3(fragPos.x,fragPos.y,cam_to_screen)*rotation(0,camera_rotation.x)*rotation(1,camera_rotation.y)*rotation(2,camera_rotation.z)+camera_pos;
    vec3 color = calculateColor(pos,normalize(pos-camera_pos));
    vec4 hud_color = texture2D(hud_image,uv*vec2(1,-1));
    fragColor = vec4(color*(1-hud_color.a)+hud_color.rgb*hud_color.a,1);
}