
#include <vector>
#include <iostream>

#include "kademlia/first_session.hpp"
#include "kademlia/session.hpp"


int main(void)
{
    std::cout<<"********* Kademlia example ****" << std::endl;

    //just minimum usage to test package
    kademlia::first_session firstSession;

    std::cout<<"*******************************" << std::endl;

    return 0;
}
