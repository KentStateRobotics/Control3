#ifndef CS2_DNODE_HPP
#define CS2_DNODE_HPP

//#include <new>
//#include <cassert>

template <typename T>
class dnode {
public:
    dnode() : next(0), prev(0) {};
    dnode(const T& item) : data(item), next(0), prev(0) {};
    T data;                                             // data that each node holds
    dnode<T> *next, *prev;                                     // pointer to next node     
};


////////////////////////////////////////////////////////////////
// CLASS INV:   current == 0 || current->dnode<T>()
// REQUIRES:    assignable(T) && capyconstructable(T)
//
template <typename T>
class itr{
public:
            itr() : current(0) {};
            itr(dnode<T> *ptr) : current(ptr) {};
    itr<T>& operator++()        {if (current != 0) current = current->next; return *this;};     // Pre ++i
    itr<T>  operator++(int)     {itr<T> result(current); 
                                 if (current != 0) current = current->next;
                                 return result;}                                             // Post i++
    itr<T>& operator--()        {if (current != 0) current = current->prev; return *this;};     // Pre --i
    itr<T>  operator--(int)     {itr<T> result(current); 
                                 if (current != 0) current = current->prev;
                                 return result;}                                             // Post i--
    T operator*() const   {return current->data;}
    T operator*()         {return current->data;}
    dnode<T>* operator->() const {return current;}
private:
    dnode<T> *current;
};

////////////////////////////////////////////////////////////////
// CLASS INV:   (beginning == 0 && ending == 0) ||
//                beginning -> X[0] <-> X[1] <-> ... <-> X[length()-1] <- ending
//
// REQUIRES:    assignable(T) && copyconstructable(T) &&
//              comparable(T) && destructable(T)
template <typename T>
class List{
public:
                    List() : begining(0), ending(0){};
                    ~List();
                    List(const List<T>&);
    void            swap(List<T>&);
    List<T>&        operator=(List<T> rhs)  {swap(rhs); return *this;}
    bool            isEmpty() const         {return begining == 0;}
    bool            isFull() const;
    int             length() const;
    const itr<T>    operator[](int) const;
    itr<T>&         operator[](int);
    const itr<T>    find(const T&) const;
    itr<T>&         find(const T&);
    const itr<T>    begin() const           {return itr<T>(begining);};
    itr<T>          begin()                 {return itr<T>(begining);}
    const itr<T>    end() const             {return itr<T>(ending);};
    itr<T>&         end()                   {return itr<T>(ending);};
    T               front() const {};
    T&              front() {};
    T               back() const {};
    T&              back() {};

    void            remove(itr<T>);
    void            insertBefore(const T&, itr<T>);
    void            insertAfter(const T&, itr<T>);
private:
    dnode<T> *begining, *ending;
};

////////////////////////////////////////////////////////////////
// REQUIRES:    !isEmpty() && ptr -> x2
//              begining -> x1 <-> x2 <-> x3 <-> ... <-> xN <- ending
// ENSURES:     begining -> x1 <-> x2 <-> ... <-> xN <- ending
//              ptr-> x2
template <typename T>
void List<T>::remove(itr<T> ptr){
    //assert(!isEmpty() && ptr != 0)
    //if (!isempty() && ptr != 0)
    //    return;

    if (ptr == begining){
        begining = begining->next;
    } else{
        ptr->prev->next = ptr->next;
    }
    if (ptr == ending){
        ending = ending->prev;
    } else{
       ptr->next->prev = ptr->next;
    }
    delete ptr.operator->();
}

////////////////////////////////////////////////////////////////
// REQUIRES:    ptr -> x2 &&
//              begining -> x1 <-> x2 <-> ... <-> xN <- ending
// ENSURES:     begining -> x1 <-> item <-> x2 <-> ... <-> xN <- ending
//              
template <typename T>
void List<T>::insertBefore(const T& item, itr<T> ptr){
    dnode<T> *tmp = new dnode<T>(item);
    if (begining == 0) {
        begining = tmp;
        ending = tmp;
    } else if (ptr == begining){
        begining->prev = tmp;
        tmp->next = begining;
        begining = tmp;
    } else{
        tmp->next = ptr.operator->();
        tmp->prev = ptr->prev;
        ptr->prev->next = tmp;
        ptr->prev = tmp;
    }
}

////////////////////////////////////////////////////////////////
// REQUIRES:    ptr -> x2 &&
//              begining -> x1 <-> x2 <-> ... <-> xN <- ending
// ENSURES:     begining -> x1 <-> item <-> x2 <-> ... <-> xN <- ending
//     
template <typename T>
void List<T>::insertAfter(const T& item, itr<T> ptr) {
    dnode<T> *tmp = new dnode<T>(item);
    if (ending == 0) {
        begining = tmp;
    } else if (ptr == ending){
        ending->next = tmp;
        tmp->prev = ending;
        ending = tmp;
    } else{
        ptr->next->prev = tmp;
        tmp->next = ptr->next;
        tmp->prev = ptr.operator->();
        ptr->next = tmp;
    }
}

template <typename T>
int List<T>::length() const{
    int result = 0;
    for (itr<T> i = begin(); i != end(); ++result)
    return result;
}

template <typename T>
itr<T>& List<T>::operator[](int n) {
    itr<T> result = begin();
    for (int i = 0; i < n; ++i) {
        if (result == 0) break;
        ++result;
    }
    return result;
}

template <typename T>
const itr<T> List<T>::operator[](int n) const{
    itr<T> result = begin();
    for (int i = 0; i < n; ++i) {
        if (result == 0) {break;}
        ++result;
    }
    return result;
}

template <typename T>
itr<T>& List<T>::find(const T& key) {
    itr<T> result = begin();
    while ((result != 0) && (*result != key))
        ++result;
    return result;
}

template <typename T>
List<T>::~List() {
    dnode<T> *tmp;
    while (begining != 0) {
        tmp = begining;
        begining = begining->next;
        delete tmp;
    }
}

template <typename T>
List<T>::List(const List<T>& actual) : List() {
    dnode<T> *tmp= actual.begining;
    while (tmp != 0) {
        if (begining == 0){
            begining = new dnode<T>(tmp->data);
            ending = begining;
        } else{
            ending->next = new dnode<T>(tmp->data);
            ending->next->prev = ending;
        }
        tmp = tmp->next;
    }
}

template <typename T>
void List<T>::swap(List<T>& rhs) {
    dnode<T> *tmp = begining;
    begining = rhs.begining;
    rhs.begining = tmp;
    tmp = ending;
    ending = rhs.ending;
    rhs.ending = tmp;
}

#endif