#version 330 core

layout (location = 0) in vec2 in_position;
layout (location = 1) in vec2 in_texcoord;

out vec2 fragPos;
out vec2 uv;

uniform vec2 size;

void main(){
    uv = in_texcoord;
    fragPos = in_position*vec2(1,size.y/size.x);
    gl_Position = vec4(in_position,0.0,1.0);
}