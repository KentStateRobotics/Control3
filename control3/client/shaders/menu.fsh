#version 330 core
in vec2 UV;
out vec4 color;
uniform sampler2D myTexture;
uniform vec4 tint;
void main() {
    color = texture(myTexture, UV).rgba * tint;
}