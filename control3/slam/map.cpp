#include"map.h"

Map::Block::Block(const Map* map, int16_t offsetX, int16_t offsetY) : _map(map), _offsetX(offsetX), _offsetY(offsetY){
    int size = std::pow(map->_blockSize, 2);
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
    int blockX = std::floor(x / static_cast<double>(_blockSize));
    int blockY = std::floor(y / static_cast<double>(_blockSize));
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
    int blockX = std::floor(x / static_cast<double>(_blockSize));
    int blockY = std::floor(y / static_cast<double>(_blockSize));
    int elmX = x - blockX * _blockSize;
    int elmY = y - blockY * _blockSize;
    Block& block = getOrInsertBlock(blockX, blockY);
    block.setElement(elmX, elmY, height, confidence);
}

double Map::heightUnitsToMeters(int16_t value) const{
    return static_cast<double>(value * _precision) / 1000;
}

int16_t Map::metersToHeightUnits(double distance) const{
    return distance / _precision * 1000;
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