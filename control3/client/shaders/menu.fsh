#version 330 core
in vec2 UV;
out vec4 color;
uniform sampler2D myTexture; 
void main() {
    color = texture(myTexture, UV).rgba;
    //color = vec3(1,UV[0],UV[1]);
}