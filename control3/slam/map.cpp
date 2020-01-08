#include"map.h"

#include<iostream>

Map::Block::Block(const Map* map, int16_t offsetX, int16_t offsetY) : _map(map), _offsetX(offsetX), _offsetY(offsetY){
    int size = static_cast<int>(std::pow(static_cast<int>(map->_blockSize), 2));
    _voxels = new std::pair<double, uint8_t>[size];
    //std::cout << "pre mem set" << std::endl;
    memset(_voxels, 0, sizeof(std::pair<double, uint8_t>) * size);
    //std::cout << "post set" << std::endl;
}

Map::Block::~Block(){
    delete[] _voxels;
}

Map::Block::Block(Map::Block&& other){
    _voxels = other._voxels;
    other._voxels = nullptr;
    _map = other._map;
    _offsetX = other._offsetX;
    _offsetY = other._offsetY;
}
/*
Map::Block::Block(const Map::Block& other){
    _voxels = other._voxels;
    _map = other._map;
    _offsetX = other._offsetX;
    _offsetY = other._offsetY;
}

Map::Block& Map::Block::operator=(const Map::Block& other){
    _voxels = other._voxels;
    _map = other._map;
    _offsetX = other._offsetX;
    _offsetY = other._offsetY;
    return *this;
}*/

std::pair<double, uint8_t> Map::Block::getElement(int x, int y) const{
    return _voxels[x * _map->_blockSize + y];
}

void Map::Block::setElement(int x, int y, double height, uint8_t confidence){
    //std::cout << x * _map->_blockSize + y << " pre set elm" << std::endl;
    _voxels[x * _map->_blockSize + y] = std::make_pair(height, confidence);
    //std::cout << _map->_blockSize * _map->_blockSize << " post set elm" << std::endl;
}


Map::Map(uint16_t blockSize, uint8_t unitSize, uint8_t precision) : _blockSize(blockSize), _unitSize(unitSize), _precision(precision) {};

Map::~Map(){
    std::for_each(_blocks.begin(), _blocks.end(), [](std::pair<std::pair<int16_t, int16_t>, Block*> block){
        delete block.second;
    });
}

std::pair<double, uint8_t> Map::getFromIndice(int x, int y) const{
    int blockX = static_cast<int>(std::floor(x / static_cast<double>(_blockSize)));
    int blockY = static_cast<int>(std::floor(y / static_cast<double>(_blockSize)));
    int elmX = x - blockX * _blockSize;
    int elmY = y - blockY * _blockSize;
    auto block = getBlock(blockX, blockY);
    if(block.first){
        return block.second->getElement(elmX, elmY);
    }else{
        return std::make_pair(0,0);
    }
}

std::pair<double, uint8_t> Map::getFromDistance(double x, double y) const{
    auto convert = getIndiceFromDistance(x, y);
    return getFromIndice(convert.first, convert.second);
}

std::pair<int,int> Map::getIndiceFromDistance(double x, double y) const{
    //std::cout << "distance " << x << " " << y << std::endl;
    return std::make_pair(static_cast<int>(std::floor(x * 1000 / _unitSize)), static_cast<int>(std::floor(y * 1000 / _unitSize)));
}

std::pair<double,double> Map::getDistanceFromIndice(int x, int y) const{
    return std::make_pair(static_cast<double>(x) / (_unitSize * 1000), static_cast<double>(y) / (_unitSize * 1000));
}

void Map::setByDistance(double x, double y, double height, uint8_t confidence){
    auto convert = getIndiceFromDistance(x, y);
    setByIndice(convert.first, convert.second, height, confidence);
}

void Map::setByIndice(int x, int y, double height, uint8_t confidence){
    //std::cout << "cords " << x << " " << y << std::endl;
    int blockX = static_cast<int>(std::floor(x / static_cast<double>(_blockSize)));
    int blockY = static_cast<int>(std::floor(y / static_cast<double>(_blockSize)));
    int elmX = x - blockX * _blockSize;
    int elmY = y - blockY * _blockSize;
    Block* block = getOrInsertBlock(blockX, blockY);
    block->setElement(elmX, elmY, height, confidence);
}

double Map::heightUnitsToMeters(int16_t value) const{
    return static_cast<double>(value * _precision) / 1000;
}

int16_t Map::metersToHeightUnits(double distance) const{
    return static_cast<int16_t>(distance / _precision * 1000);
}

void Map::clear(){
    std::for_each(_blocks.begin(), _blocks.end(), [](std::pair<std::pair<int16_t, int16_t>, Block*> block){
        delete block.second;
    });
    _blocks.clear();
}

Map::Block* Map::getOrInsertBlock(int16_t x, int16_t y){
    auto blockItr = _blocks.find(std::make_pair(x, y));
    //std::cout << x << " " << y << std::endl;
    if(blockItr == _blocks.end()){
        //std::cout << "none found" << std::endl;
        auto block = _blocks.insert(std::make_pair(std::make_pair(x, y), new Block(this, x, y)));
        return block.first->second;
    }else{
        //std::cout << "found" << std::endl;
        return blockItr->second;
    }

}

std::pair<bool, const Map::Block*> Map::getBlock(int16_t x, int16_t y) const{
    auto block = _blocks.find(std::make_pair(x, y));
    return std::make_pair(block != _blocks.cend(), block->second);
}

void Map::applyMinHeightIndice(int x, int y, double height){
    auto currentValue = getFromIndice(x, y);
    if(currentValue.second == 0){
        setByIndice(x, y, height, 1);
    }else{
        setByIndice(x, y, std::max(height, currentValue.first), std::min(currentValue.second + 1, 4));
    }
}

void Map::applyMaxHeightIndice(int x, int y, double height){
    auto currentValue = getFromIndice(x, y);
    if(currentValue.second != 0 && currentValue.first + 1 > height){
        if(currentValue.second < 4){
            setByIndice(x, y, height, 4);
        }else{
            setByIndice(x, y, currentValue.first, std::max(currentValue.second - 1, 1));
        }
    }
}

void Map::applyDepthImage(const uint16_t* image, float scale, int height, int width, double hFov, double vFov, double x, double y, double z, double rX, double rY, double rZ){
    double hPerPixle = hFov / width;
    double vPerPixle = vFov / height;
    //Image is stored row by row, top to bottom, left to right
    for(int i = 0; i < height; ++i){
        for(int j = 0; j < width; ++j){
            //Depth Camera IMU y-up/down, x-right/left, z-front/back axies
            if(i > 198){
                //std::cout << i << " " << j << std::endl;
            }
            uint16_t rawDistance = image[i * width + j];
            if(rawDistance > 10 && rawDistance < std::pow(2, 16) - 10){
                double distance = rawDistance * scale;
                double azimuth = hPerPixle * (j - width / 2) + rY;
                double inclination = M_PI / 2 - (vPerPixle * (i - height / 2) + rX);
                double fX = distance * std::sin(inclination) * std::cos(azimuth);
                double fZ = distance * std::sin(inclination) * std::sin(azimuth);
                double fY = distance * std::cos(inclination);
                auto convert = getIndiceFromDistance(fX, fZ);
                applyMinHeightIndice(convert.first, convert.second, fY);
            }
        }
    }
}

std::pair<int, float*> Map::getPoints(){
    float* points = new float[_blockSize * _blockSize * 3 * _blocks.size()]();
    int blockCounter = 0;
    for(auto block : _blocks){
        int x = block.first.first;
        int y = block.first.second;
        for(int i = 0; i < _blockSize; ++i){
            for(int j = 0; j < _blockSize; ++j){
                int index = (blockCounter * static_cast<int>(std::pow(_blockSize, 2)) + i * _blockSize + j) * 3;
                points[index] = (j + (y * _blockSize)) / 1000.0f;
                points[index + 1] = static_cast<float>(block.second->getElement(j, i).first * _precision / 1000.0f);
                points[index + 2] = (i + (x * _blockSize)) / 1000.0f;
            }
        }
        ++blockCounter;
    }
    return std::make_pair(_blockSize * _blockSize * 3 * _blocks.size(), points);
}