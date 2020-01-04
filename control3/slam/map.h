/** 
 * 1/3/2020 Jared Butcher
 * 2D voxel height map
 */

#include<stdint.h>
#include<cmath>
#include<utility>
#include<cstring>
#include<unordered_map>
#include<array>

/**
 * Store a 2d voxel height map.
 * Will automaticly dynamicly expand using linked blocks
 * Distances are mesured in meters
 * Each element stores a height(double) and a confidence(unit8_t) value
 * Elements can be accessed by either an x and y distance that falls within its area, or indice for the element (both can be negitive)
 */
class Map{
private:
    /**
     * Elements are stored bottom to top left to right
     */ 
    class Block{
    public:
        Block(){};
        Block(const Map* map, int16_t offsetX, int16_t offsetY);
        ~Block();
        std::pair<double, uint8_t> getElement(int x, int y) const;
        void setElement(int x, int y, double height, uint8_t confidence);
    private:
        std::pair<double, uint8_t>* _voxels=nullptr;
        int16_t _offsetX;
        int16_t _offsetY;
        const Map* _map;
    };
public:
    /**
     * @param blockSize The size in elements to make each side of the dynamic map regions
     * @param unitSize The size in mm for each element on the x/y plane
     * @param percision The increment in mm to store the height data as
     */
    Map(uint16_t blockSize=256, uint8_t unitSize = 10, uint8_t precision = 5);
    ~Map(){};

    /**
     * Obtain the indivisual voxel described by the coordinates (in indice or meteres)
     */
    std::pair<double, uint8_t> getFromIndice(int x, int y) const;
    std::pair<double, uint8_t> getFromDistance(double x, double y) const;

    /**
     * Convert between coordinates in voxels and meters
     */
    std::pair<int,int> getIndiceFromDistance(double x, double y) const;
    std::pair<double,double> getDistanceFromIndice(int x, int y) const;

    /**
     * Set the indivisual voxel described by the coordinates (in indice or meteres)
     */
    void setByDistance(double x, double y, double height, uint8_t confidence);
    void setByIndice(int x, int y, double height, uint8_t confidence);

    /**
     * Convert the height between meters and the storage unit
     */
    double heightUnitsToMeters(int16_t value) const;
    int16_t metersToHeightUnits(double distance) const;
    
    void clear();
private:
    Block& getOrInsertBlock(int16_t x, int16_t y);
    std::pair<bool, const Block&> getBlock(int16_t x, int16_t y) const;

    uint16_t _blockSize;
    uint8_t _unitSize;
    uint8_t _precision;
    std::unordered_map<std::pair<int16_t, int16_t>, Block> _blocks;
};