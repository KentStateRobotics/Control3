#include"map.h"

Map::Block::Block(const Map* map, int16_t offsetX, int16_t offsetY) : _map(map), _offsetX(offsetX), _offsetY(offsetY){
    int size = static_cast<int>(std::pow(map->_blockSize, 2));
    _voxels = new std::pair<double, uint8_t>[size];
    memset(_voxels, 0, sizeof(std::pair<double, uint8_t>) * size);
}

Map::Block::~Block(){
    delete[] _voxels;
}

std::pair<double, uint8_t> Map::Block::getElement(int x, int y) const{
    return _voxels[x * _map->_blockSize + y];
}

void Map::Block::setElement(int x, int y, double height, uint8_t confidence){
    _voxels[x * _map->_blockSize + y] = std::make_pair(height, confidence);
}


Map::Map(uint16_t blockSize, uint8_t unitSize, uint8_t precision) : _blockSize(blockSize), _unitSize(unitSize), _precision(precision) {};

std::pair<double, uint8_t> Map::getFromIndice(int x, int y) const{
    int blockX = static_cast<int>(std::floor(x / static_cast<double>(_blockSize)));
    int blockY = static_cast<int>(std::floor(y / static_cast<double>(_blockSize)));
    int elmX = x - blockX * _blockSize;
    int elmY = y - blockY * _blockSize;
    auto block = getBlock(blockX, blockY);
    if(block.first){
        return block.second.getElement(elmX, elmY);
    }else{
        return std::make_pair(0,0);
    }
}

std::pair<double, uint8_t> Map::getFromDistance(double x, double y) const{
    auto convert = getIndiceFromDistance(x, y);
    return getFromIndice(convert.first, convert.second);
}

std::pair<int,int> Map::getIndiceFromDistance(double x, double y) const{
    return std::make_pair(std::floor(x * _unitSize * 1000), std::floor(y * _unitSize * 1000));
}

std::pair<double,double> Map::getDistanceFromIndice(int x, int y) const{
    return std::make_pair(static_cast<double>(x) / (_unitSize * 1000), static_cast<double>(y) / (_unitSize * 1000));
}

void Map::setByDistance(double x, double y, double height, uint8_t confidence){
    auto convert = getIndiceFromDistance(x, y);
    setByIndice(convert.first, convert.second, height, confidence);
}

void Map::setByIndice(int x, int y, double height, uint8_t confidence){
    int blockX = static_cast<int>(std::floor(x / static_cast<double>(_blockSize)));
    int blockY = static_cast<int>(std::floor(y / static_cast<double>(_blockSize)));
    int elmX = x - blockX * _blockSize;
    int elmY = y - blockY * _blockSize;
    Block& block = getOrInsertBlock(blockX, blockY);
    block.setElement(elmX, elmY, height, confidence);
}

double Map::heightUnitsToMeters(int16_t value) const{
    return static_cast<double>(value * _precision) / 1000;
}

int16_t Map::metersToHeightUnits(double distance) const{
    return static_cast<int16_t>(distance / _precision * 1000);
}

void Map::clear(){
    _blocks.clear();
}

Map::Block& Map::getOrInsertBlock(int16_t x, int16_t y){
    return _blocks[std::make_pair(x, y)];
}

std::pair<bool, const Map::Block&> Map::getBlock(int16_t x, int16_t y) const{
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

void Map::applyDepthImage(const uint16_t* image, int height, int width, double hFov, double vFov, double x, double y, double z, double rX, double rY, double rZ){
    double hPerPixle = hFov / width;
    double vPerPixle = vFov / height;
    //Image is stored row by row, top to bottom, left to right
    for(int i = 0; i < height; ++i){
        for(int j = 0; j < width; ++j){
            //Depth Camera IMU y-up/down, x-right/left, z-front/back axies
            uint16_t distance = image[i * width + j];
            if(distance > 10 && distance < std::pow(2, 16) - 10){
                double azimuth = hPerPixle * (j - width / 2) + rY;
                double inclination = M_PI / 2 * (vPerPixle * (i - height / 2) + rX);
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
                points[index] = (j * _unitSize * (y * _blockSize)) / 1000.0f;
                points[index] = static_cast<float>(block.second.getElement(j, i).first * _precision / 1000.0f);
                points[index] = (i * _unitSize * (y * _blockSize)) / 1000.0f;
            }
        }
        ++blockCounter;
    }
    return std::make_pair(_blockSize * _blockSize * 3 * _blocks.size(), points);
}